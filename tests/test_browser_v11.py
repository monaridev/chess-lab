import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

from tests.test_browser import browser, live_server, pages, start_pair, make_move, board_pieces

pytestmark = pytest.mark.browser
ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts/v1.2"
THEMES = ["laboratory", "matcha", "strawberry", "midnight", "lavender", "elmore", "watterson"]
SKINS = ["classic", "soft", "cute", "minimal", "cartoon"]


def appearance(page, theme, skin):
    if not page.locator(".appearance-controls").get_attribute("open") == "":
        page.locator(".appearance-controls summary").click()
    page.get_by_label("Tema do tabuleiro").select_option(theme)
    page.get_by_label("Skin das peças").select_option(skin)


def test_separate_reveal_confirmation_privacy_highlight_refresh_and_reset(pages):
    white, black, code = start_pair(pages)
    frames = []
    white.on("websocket", lambda ws: ws.on("framereceived", lambda text: frames.append(json.loads(text))))
    white.reload()
    expect(white.locator("#connection")).to_have_text("Conectado")
    white.locator("#reveal").click()
    expect(white.get_by_role("button", name="Continuar pensando")).to_be_focused()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    white.screenshot(path=str(ARTIFACTS / "reveal-confirmation.png"), full_page=True, animations="disabled")
    white.get_by_role("button", name="Continuar pensando").click()
    expect(white.locator("#reveal-dialog")).not_to_be_visible()
    expect(white.locator("#reveal-content")).not_to_be_visible()
    white.locator("#reveal").click()
    white.keyboard.press("Escape")
    expect(white.locator("#reveal-dialog")).not_to_be_visible()
    for level in range(1, 5):
        white.locator("#hint").click()
        expect(white.locator("#hint-content")).to_contain_text(f"PISTA {level} / 4")
    hint_frames = [m for m in frames if m["type"] == "hint"]
    assert len(hint_frames) == 4
    assert all("move" not in m and "san" not in m for m in hint_frames)
    assert not any(m["type"] == "reveal" for m in frames)
    white.locator("#reveal").click()
    white.get_by_role("button", name="Mostrar jogada mesmo assim").click()
    expect(white.locator("#reveal-content")).to_be_visible()
    expect(white.locator(".hint-square")).to_have_count(2)
    expect(black.locator(".hint-square")).to_have_count(0)
    expect(black.locator("#reveal-content")).not_to_be_visible()
    expect(white.locator("#reveal-content")).to_contain_text("outras jogadas podem existir")
    revealed = next(m for m in reversed(frames) if m["type"] == "reveal")
    white.reload()
    expect(white.locator(".hint-square")).to_have_count(2)
    expect(white.locator("#reveal-content")).to_contain_text(revealed["san"])
    white.screenshot(path=str(ARTIFACTS / "revealed-desktop.png"), full_page=True, animations="disabled")
    make_move(white, black, revealed["move"])
    expect(white.locator(".hint-square")).to_have_count(0)
    expect(white.locator("#reveal-content")).not_to_be_visible()
    black.locator("#reveal").click()
    black.screenshot(path=str(ARTIFACTS / "reveal-mobile.png"), full_page=True, animations="disabled")
    black.get_by_role("button", name="Mostrar jogada mesmo assim").click()
    expect(black.locator(".hint-square")).to_have_count(2)


@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("skin", SKINS)
def test_every_theme_skin_combination_renders_and_keeps_gameplay(pages, theme, skin):
    white, black, code = start_pair(pages)
    appearance(white, theme, skin)
    expect(white.locator("html")).to_have_attribute("data-theme", theme)
    expect(white.locator("html")).to_have_attribute("data-skin", skin)
    expect(black.locator("html")).to_have_attribute("data-theme", "laboratory")
    folder = "" if skin == "classic" else f"skins/{skin}/"
    expect(white.locator('[data-square="e1"] img')).to_have_attribute("src", f"/static/pieces/{folder}white-k.svg")
    assert white.locator("#board img").evaluate_all("images => Promise.all(images.map(i => i.decode())).then(() => images.every(i => i.naturalWidth > 0))")
    # Contraste entre casas: diferença de luminância e identidade cromática.
    colors = white.locator("#board .square").evaluate_all("nodes => nodes.slice(0,2).map(n => getComputedStyle(n).backgroundColor)")
    assert colors[0] != colors[1]
    white.locator('[data-square="e2"]').click()
    expect(white.locator(".square.legal")).to_have_count(2)
    white.locator('[data-square="e2"]').click()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    white.locator("#board").screenshot(path=str(ARTIFACTS / f"board-{theme}-{skin}.png"))
    # Com skins locais diferentes, comparamos peças semanticamente.
    white.locator('[data-square="e2"]').click()
    white.locator('[data-square="e4"]').click()
    expect(black.locator('[data-square="e4"] img')).to_have_attribute("src", "/static/pieces/white-p.svg")
    expect(white.locator('[data-square="e4"] img')).to_have_attribute("src", f"/static/pieces/{folder}white-p.svg")
    expect(white.locator('[data-square="e2"] img')).to_have_count(0)
    white.reload()
    expect(white.locator("#connection")).to_have_text("Conectado")
    expect(white.locator("html")).to_have_attribute("data-theme", theme)
    expect(white.locator("html")).to_have_attribute("data-skin", skin)
    expect(white.locator('[data-square="e4"] img')).to_have_attribute("src", f"/static/pieces/{folder}white-p.svg")


def test_preferences_persist_new_tab_and_invalid_storage_is_safe(browser, live_server):
    base, _ = live_server
    with browser.new_context() as context:
        page = context.new_page()
        page.goto(base)
        page.get_by_role("button", name="Criar sala").click()
        expect(page.locator("#connection")).to_have_text("Conectado")
        appearance(page, "elmore", "cartoon")
        second = context.new_page()
        second.goto(base)
        expect(second.locator("html")).to_have_attribute("data-theme", "elmore")
        expect(second.locator("html")).to_have_attribute("data-skin", "cartoon")
    with browser.new_context() as context:
        page = context.new_page()
        page.add_init_script("localStorage.setItem('chesslab.appearance.v1', JSON.stringify({theme: '<invalid>', skin: '../../bad'}));")
        page.goto(base)
        expect(page.locator("html")).to_have_attribute("data-theme", "laboratory")
        expect(page.locator("html")).to_have_attribute("data-skin", "classic")


def test_storage_blocked_still_plays_and_applies_appearance(browser, live_server):
    base, _ = live_server
    with browser.new_context() as context:
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script("Object.defineProperty(window, 'localStorage', {get() {throw new DOMException('Blocked', 'SecurityError')}});")
        page.goto(base)
        page.get_by_role("button", name="Criar sala").click()
        expect(page.locator("#connection")).to_have_text("Conectado")
        appearance(page, "matcha", "soft")
        expect(page.locator("html")).to_have_attribute("data-theme", "matcha")
        expect(page.locator("#appearance-status")).to_contain_text("não permitiu salvar")
        assert not errors


def test_mobile_layout_reduced_motion_and_check_in_all_themes(pages):
    white, black, _ = start_pair(pages, fen="4k3/8/8/8/8/8/4r3/4K3 w - - 0 1")
    white.set_viewport_size({"width": 390, "height": 844})
    white.emulate_media(reduced_motion="reduce")
    for theme in THEMES:
        appearance(white, theme, "cartoon")
        expect(white.locator('[data-square="e1"]')).to_have_class(re.compile(".*check.*"))
        assert white.locator('[data-square="e1"]').evaluate("n => getComputedStyle(n, '::before').content") == '"!"'
        for width in (320, 390, 768):
            white.set_viewport_size({"width": width, "height": 844})
            assert white.evaluate("document.documentElement.scrollWidth <= innerWidth")
        white.locator("#reveal").click()
        assert white.locator("#reveal-dialog").evaluate("n => getComputedStyle(n).animationName") == "none"
        white.get_by_role("button", name="Continuar pensando").click()
    white.set_viewport_size({"width": 390, "height": 844})
    white.locator(".appearance-controls summary").click()
    white.screenshot(path=str(ARTIFACTS / "elmore-mobile-check.png"), full_page=True, animations="disabled")


def test_disconnect_closes_reveal_confirmation(pages):
    white, black, _ = start_pair(pages)
    white.locator("#reveal").click()
    white.context.set_offline(True)
    expect(white.locator("#reveal-dialog")).not_to_be_visible()
    expect(white.locator("#reveal-content")).not_to_be_visible()
    white.context.set_offline(False)
    expect(white.locator("#connection")).to_have_text("Conectado")
    expect(white.locator("#reveal-content")).not_to_be_visible()
