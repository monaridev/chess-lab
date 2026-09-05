"""Integração de ponta a ponta: Chromium + HTTP/WebSocket reais + FastAPI.

As posições especiais são preparadas no servidor do teste, antes da entrada
do segundo jogador. A aplicação não expõe endpoints para alterar tabuleiros.
"""

import os
import re
import socket
import threading
import time
from contextlib import ExitStack
from pathlib import Path

import chess
import pytest
import uvicorn
from playwright.sync_api import expect, sync_playwright

from backend.main import create_app
from backend.rooms import RoomManager

pytestmark = pytest.mark.browser
ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def live_server():
    manager = RoomManager()
    listener = socket.socket()
    listener.bind(("0.0.0.0", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(manager), log_level="warning", ws_ping_interval=0.5, ws_ping_timeout=0.5))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.02)
    assert server.started, "Servidor não iniciou"
    yield f"http://127.0.0.1:{port}", manager
    server.should_exit = True
    thread.join(timeout=10)
    listener.close()
    assert not thread.is_alive(), "Servidor não encerrou"


@pytest.fixture(scope="module")
def browser():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".browsers"))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def pages(browser, live_server):
    base, manager = live_server
    errors = []
    with ExitStack() as stack:
        white_context = browser.new_context(viewport={"width": 1440, "height": 1000}, permissions=["clipboard-read", "clipboard-write"])
        stack.callback(white_context.close)
        black_context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        stack.callback(black_context.close)
        white, black = white_context.new_page(), black_context.new_page()
        for page in (white, black):
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
            page.set_default_timeout(8000)
            page.goto(base)
        yield white, black, manager, base
    assert not errors, f"Erros JavaScript/console: {errors}"


def start_pair(pages, mode="assisted", fen=None):
    white, black, manager, base = pages
    white.locator(f'input[name="mode"][value="{mode}"]').check()
    white.get_by_role("button", name="Criar sala").click()
    expect(white.locator("#turn-label")).to_have_text("Aguardando segundo jogador")
    code = white.locator("#room-code").inner_text()
    if fen:
        manager.get(code).board = chess.Board(fen)
    black.get_by_label("Código da sala", exact=True).fill(code)
    black.get_by_role("button", name="Entrar", exact=False).click()
    expect(white.locator("#black-presence")).to_have_text("Online")
    expect(black.locator("#white-presence")).to_have_text("Online")
    expect(white.locator("#board .square")).to_have_count(64)
    expect(black.locator("#board .square")).to_have_count(64)
    assert white.locator("#board .square").first.get_attribute("data-square") == "a8"
    assert black.locator("#board .square").first.get_attribute("data-square") == "h1"
    return white, black, code


def board_pieces(page):
    return page.locator("#board .square:has(img)").evaluate_all("nodes => Object.fromEntries(nodes.map(n => [n.dataset.square, n.querySelector('img').getAttribute('src')]))")


def make_move(player, other, uci, promotion=None):
    expect(player.locator("#turn-label")).to_have_text("Sua vez")
    player.locator(f'[data-square="{uci[:2]}"]').click()
    expect(player.locator(f'[data-square="{uci[2:4]}"]')).to_have_class(re.compile(r".*legal.*"))
    player.locator(f'[data-square="{uci[2:4]}"]').click()
    if promotion:
        expect(player.get_by_role("dialog")).to_be_visible()
        player.get_by_role("button", name=promotion, exact=True).click()
        expect(player.get_by_role("dialog")).not_to_be_visible()
    expect(other.locator(f'[data-square="{uci[2:4]}"]')).to_have_class(re.compile(r".*last.*"))
    expect(player.locator(f'[data-square="{uci[:2]}"] img')).to_have_count(0)
    assert board_pieces(player) == board_pieces(other)


def test_desktop_mobile_full_game_hints_refresh_and_reconnection(pages):
    white, black, code = start_pair(pages)
    # Copiar funciona no desktop; a orientação muda sem mudar a posição.
    white.bring_to_front()
    white.get_by_role("button", name="Copiar código da sala").click()
    expect(white.locator("#copy-status")).to_contain_text("Código copiado")
    assert board_pieces(white) == board_pieces(black)
    white.locator('[data-square="e7"]').click()
    expect(white.locator("#game-error")).to_contain_text("pertence ao outro jogador")
    white.locator('[data-square="e2"]').click()
    expect(white.locator('[data-square="e4"]')).to_have_class(re.compile(r".*legal.*"))
    white.locator('[data-square="e5"]').click()
    expect(white.locator("#game-error")).to_contain_text("destino destacado")
    expect(white.locator('[data-square="e2"] img')).to_have_count(1)
    for level in range(1, 5):
        white.locator("#hint").click()
        expect(white.locator("#hint-content")).to_contain_text(f"PISTA {level} / 4")
    expect(white.locator("#hint")).to_be_disabled()
    expect(black.locator("#hint-content")).not_to_contain_text("PISTA")
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    white.screenshot(path=str(artifacts / "game-desktop.png"), full_page=True)
    black.screenshot(path=str(artifacts / "game-mobile.png"), full_page=True)
    make_move(white, black, "f2f3")
    black.locator("#hint").click()
    expect(black.locator("#hint-content")).to_contain_text("PISTA 1 / 4")
    black.reload()
    expect(black.locator("#connection")).to_have_text("Conectado")
    expect(black.locator("#room-code")).to_have_text(code)
    expect(black.locator("#your-color")).to_have_text("Pretas")
    expect(black.locator("#hint-content")).to_contain_text("PISTA 1 / 4")
    assert board_pieces(black) == board_pieces(white)
    # Queda real de rede do cliente, detectada pelo ping do WebSocket.
    black.context.set_offline(True)
    expect(white.locator("#black-presence")).to_have_text("Offline")
    expect(white.locator("#game-status")).to_contain_text("Adversário desconectado")
    black.context.set_offline(False)
    expect(white.locator("#black-presence")).to_have_text("Online", timeout=12000)
    expect(black.locator("#connection")).to_have_text("Conectado")
    assert board_pieces(black) == board_pieces(white)
    make_move(black, white, "e7e5")
    make_move(white, black, "g2g4")
    make_move(black, white, "d8h4")
    expect(white.locator("#turn-label")).to_have_text("O outro jogador venceu")
    expect(black.locator("#turn-label")).to_have_text("Você venceu!")
    expect(white.locator("#game-status")).to_contain_text("Xeque-mate · 0-1")
    expect(white.locator('[data-square="e1"]')).to_have_class(re.compile(r".*check.*"))
    expect(white.locator("#hint")).to_be_disabled()
    white.reload()
    expect(white.locator("#game-status")).to_contain_text("Xeque-mate · 0-1")


def test_castling_and_en_passant_from_starting_position(pages):
    white, black, _ = start_pair(pages, "normal")
    expect(white.locator("#hint")).to_be_disabled()
    expect(white.locator("#hint-content")).to_contain_text("Partida Normal")
    sequence = ["e2e4", "a7a6", "e4e5", "d7d5", "e5d6", "c7d6", "g1f3", "g8f6", "f1e2", "b8c6", "e1g1"]
    for index, uci in enumerate(sequence):
        make_move(white if index % 2 == 0 else black, black if index % 2 == 0 else white, uci)
        if uci == "e5d6":
            expect(white.locator('[data-square="d5"] img')).to_have_count(0)
    expect(white.locator('[data-square="g1"] img')).to_have_attribute("src", "/static/pieces/white-k.svg")
    expect(black.locator('[data-square="f1"] img')).to_have_attribute("src", "/static/pieces/white-r.svg")


@pytest.mark.parametrize("kind,label", [("q", "Dama"), ("r", "Torre"), ("b", "Bispo"), ("n", "Cavalo")])
def test_promotion_dialog_all_choices(pages, kind, label):
    white, black, _ = start_pair(pages, fen="8/P6k/8/8/8/8/7p/4K3 w - - 0 1")
    if kind == "q":
        white.locator('[data-square="a7"]').click()
        white.locator('[data-square="a8"]').click()
        white.get_by_role("button", name="Cancelar", exact=True).click()
        expect(white.locator('[data-square="a7"] img')).to_have_count(1)
        white.locator('[data-square="a7"]').click()  # Desselecionar antes do helper.
    make_move(white, black, "a7a8", promotion=label)
    expect(white.locator('[data-square="a8"] img')).to_have_attribute("src", f"/static/pieces/white-{kind}.svg")


def test_black_promotion_on_touch_screen(pages):
    white, black, _ = start_pair(pages, fen="8/P6k/8/8/8/8/7p/4K3 b - - 0 1")
    make_move(black, white, "h2h1", promotion="Cavalo")
    expect(white.locator('[data-square="h1"] img')).to_have_attribute("src", "/static/pieces/black-n.svg")


@pytest.mark.parametrize("fen,uci,reason", [("7k/5K2/8/6Q1/8/8/8/8 w - - 0 1", "g5g6", "Afogamento"), ("n6k/8/8/8/8/8/2b5/2K5 w - - 0 1", "c1c2", "Material insuficiente")])
def test_draw_result_on_both_screens(pages, fen, uci, reason):
    white, black, _ = start_pair(pages, fen=fen)
    make_move(white, black, uci)
    for page in (white, black):
        expect(page.locator("#turn-label")).to_have_text("Partida empatada")
        expect(page.locator("#game-status")).to_contain_text(reason)


def test_responsive_layout_assets_and_resume(pages):
    white, black, _, _ = pages
    (ROOT / "artifacts").mkdir(exist_ok=True)
    white.screenshot(path=str(ROOT / "artifacts/lobby-desktop.png"), full_page=True)
    black.screenshot(path=str(ROOT / "artifacts/lobby-mobile.png"), full_page=True)
    white, black, code = start_pair(pages)
    for width in (320, 375, 390, 720, 768, 1024, 1440):
        white.set_viewport_size({"width": width, "height": 900})
        assert white.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"Overflow em {width}px"
        assert white.locator("#board").bounding_box()["width"] > 250
    assert white.locator("#board img").evaluate_all("images => images.every(img => img.complete && img.naturalWidth > 0)")
    black.get_by_role("button", name="← Início").click()
    expect(white.locator("#black-presence")).to_have_text("Offline")
    black.get_by_role("button", name="Retomar partida").click()
    expect(black.locator("#room-code")).to_have_text(code)
    expect(white.locator("#black-presence")).to_have_text("Online")
    assert board_pieces(white) == board_pieces(black)


def test_friendly_invalid_and_full_room_errors(browser, live_server):
    base, _ = live_server
    with browser.new_context() as context:
        page = context.new_page()
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.goto(base)
        page.get_by_label("Código da sala", exact=True).fill("ZZZZZZ")
        page.get_by_role("button", name="Entrar", exact=False).click()
        expect(page.locator("#lobby-error")).to_contain_text("Sala não encontrada")
        white = context.request.post(f"{base}/api/rooms", data={"mode": "normal"}).json()
        context.request.post(f"{base}/api/rooms/{white['code']}/join")
        page.get_by_label("Código da sala", exact=True).fill(white["code"])
        page.get_by_role("button", name="Entrar", exact=False).click()
        expect(page.locator("#lobby-error")).to_contain_text("já tem dois jogadores")
        assert not page_errors
