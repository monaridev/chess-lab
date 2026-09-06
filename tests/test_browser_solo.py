"""Solo through real HTTP + local Stockfish + Chromium. No remote requests."""
import socket
import threading
import time

import chess
import pytest
import uvicorn
from playwright.sync_api import expect

from backend.main import create_app
from backend.solo import SoloManager
from tests.test_browser import browser, ROOT

pytestmark = pytest.mark.browser


@pytest.fixture(scope='module')
def solo_server():
    manager = SoloManager()
    listener = socket.socket(); listener.bind(('127.0.0.1', 0)); listener.listen(128)
    server = uvicorn.Server(uvicorn.Config(create_app(solo=manager), log_level='warning'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline: time.sleep(.02)
    assert server.started
    yield f'http://127.0.0.1:{listener.getsockname()[1]}', manager
    server.should_exit = True; thread.join(10); listener.close()
    assert not thread.is_alive()


@pytest.fixture
def solo_page(browser, solo_server):
    base, manager = solo_server
    with browser.new_context(viewport={'width': 1440, 'height': 1000}) as context:
        external, errors = [], []
        def route_handler(route):
            if not route.request.url.startswith(base + '/'):
                external.append(route.request.url); route.abort()
            else: route.continue_()
        context.route('**/*', route_handler)
        page = context.new_page(); page.set_default_timeout(12000)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base)
        yield page, manager
        assert not errors and not external


def enter(page, color='white', difficulty='beginner'):
    page.locator('#solo-open').click()
    page.locator(f'#solo-color input[value="{color}"]').check()
    page.locator(f'#solo-difficulty input[value="{difficulty}"]').check()
    page.locator('#solo-start').click()
    expect(page.locator('#solo-board .square')).to_have_count(64)
    expect(page.locator('#solo-hint')).to_be_enabled()


def move(page, uci):
    expect(page.locator('#solo-board')).to_have_attribute('aria-busy', 'false')
    page.locator(f'#solo-board [data-square="{uci[:2]}"]').click()
    page.locator(f'#solo-board [data-square="{uci[2:4]}"]').click()
    if len(uci) == 5: page.locator(f'#solo-promotion button[value="{uci[4]}"]').click()
    expect(page.locator('#solo-grade')).not_to_be_empty()
    expect(page.locator('#solo-board')).to_have_attribute('aria-busy', 'false')


def session(page, manager):
    token = page.evaluate("JSON.parse(sessionStorage.getItem('chesslab.solo.session')).token")
    return manager.get(token)


def test_solo_real_game_review_hints_resume_summary_and_no_external_network(solo_page):
    page, manager = solo_page
    enter(page)
    expect(page.locator('#solo-pose')).to_be_visible()
    for n in range(1, 5):
        page.locator('#solo-hint').click()
        expect(page.locator('#solo-hints li')).to_have_count(n)
    expect(page.locator('#solo-revealed')).to_be_empty()
    page.locator('#solo-reveal').click(); page.locator('#solo-reveal-no').click()
    expect(page.locator('#solo-revealed')).to_be_empty()
    page.locator('#solo-reveal').click(); page.locator('#solo-reveal-yes').click()
    expect(page.locator('#solo-revealed')).to_contain_text('→')
    move(page, 'g1f3')
    expect(page.locator('#solo-grade')).to_contain_text('Nf3')
    expect(page.locator('#solo-speech')).to_contain_text('cavalo')
    assert session(page, manager).board.ply() == 2
    assert page.locator('#solo-hints li').count() == 0
    page.reload(); page.locator('#solo-open').click(); page.locator('#solo-resume').click()
    expect(page.locator('#solo-grade')).to_contain_text('Nf3')
    expect(page.locator('#solo-board')).to_have_attribute('aria-busy', 'false')
    page.locator('#solo-resign').click(); page.locator('#solo-resign-no').click()
    expect(page.locator('#solo-summary')).to_be_hidden()
    page.locator('#solo-resign').click(); page.locator('#solo-resign-yes').click()
    expect(page.locator('#solo-summary')).to_be_visible()
    expect(page.locator('#solo-accuracy')).to_contain_text('%')
    assert page.evaluate("JSON.parse(localStorage.getItem('chesslab.solo.v1')).gamesPlayed") == 1
    page.reload(); page.locator('#solo-open').click(); page.locator('#solo-resume').click()
    expect(page.locator('#solo-summary')).to_be_visible()
    assert page.evaluate("JSON.parse(localStorage.getItem('chesslab.solo.v1')).gamesPlayed") == 1
    page.locator('[data-close="solo-summary"]').click()
    page.locator('#solo-back').click(); page.locator('#learn-open').click()
    expect(page.locator('#learn-catalog .learn-card')).to_have_count(6)


def test_black_orientation_responsive_pogona_and_storage_fallback(solo_page):
    page, _ = solo_page
    page.evaluate("localStorage.setItem('chesslab.solo.v1', '{bad')")
    page.reload()
    enter(page, 'black', 'easy')
    assert page.locator('#solo-board .square').first.get_attribute('data-square') == 'h1'
    for width, height in [(320,568),(390,844),(844,390),(1024,768),(1440,1000)]:
        page.set_viewport_size({'width': width, 'height': height})
        for scroll in (0,5000):
            page.locator('#solo-scroll').evaluate('(el, y) => el.scrollTop = y', scroll)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            for id in ('solo-pose','solo-speech'):
                box = page.locator('#'+id).bounding_box()
                assert box['y'] >= 0 and box['y'] + box['height'] <= height
            bubble = page.locator('#solo .pogona-bubble').bounding_box()
            content = page.locator('#solo-scroll').bounding_box()
            assert bubble['x'] + bubble['width'] <= content['x'] or bubble['y'] + bubble['height'] <= content['y'] + 1
        page.locator('#solo-scroll').evaluate('el => el.scrollTop = 0')
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    page.screenshot(animations="disabled", path=str(ROOT / 'artifacts/solo-desktop.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(animations="disabled", path=str(ROOT / 'artifacts/solo-mobile.png'))
    page.locator('#solo-more').click()
    page.evaluate("() => { Storage.prototype.setItem = () => { throw Error('blocked'); }; }")
    page.locator('#solo-resign').click(); page.locator('#solo-resign-yes').click()
    expect(page.locator('#solo-storage')).to_contain_text('Não foi possível salvar')


def test_real_hanging_piece_review_and_mate(solo_page):
    page, manager = solo_page
    enter(page)
    game = session(page, manager)
    game.board = chess.Board('7k/8/8/8/8/8/1b6/RN2K3 w - - 0 1')
    page.locator('#solo-back').click(); page.locator('#solo-open').click(); page.locator('#solo-resume').click()
    expect(page.locator('#solo-board [data-square="b2"] img')).to_have_count(1)
    move(page, 'b1c3')
    assert game.reviews[-1]['classification'] in ('mistake','blunder')
    expect(page.locator('#solo-speech')).to_contain_text('torre em a1')
    game.board = chess.Board('7k/8/5KQ1/8/8/8/8/8 w - - 0 1')
    page.locator('#solo-back').click(); page.locator('#solo-open').click(); page.locator('#solo-resume').click()
    expect(page.locator('#solo-board [data-square="g6"] img')).to_have_count(1)
    move(page, 'g6g7')
    expect(page.locator('#solo-result')).to_contain_text('xeque-mate')
    expect(page.locator('#solo-grade')).to_contain_text('Excelente')
    expect(page.locator('#solo-speech')).to_contain_text('xeque-mate')


def test_underpromotion(solo_page):
    page, manager = solo_page
    enter(page)
    game = session(page, manager)
    game.board = chess.Board('7k/P7/8/8/8/8/8/4K3 w - - 0 1')
    page.locator('#solo-back').click(); page.locator('#solo-open').click(); page.locator('#solo-resume').click()
    expect(page.locator('#solo-board [data-square="a7"] img')).to_have_count(1)
    move(page, 'a7a8n')
    expect(page.locator('#solo-result')).to_contain_text('material insuficiente')
    expect(page.locator('#solo-grade')).to_contain_text('a8=N')


def test_lost_response_recovers_server_state_without_duplicate_move(solo_page):
    page, manager = solo_page
    enter(page)
    failed = []
    def lose_reply(route):
        body = route.request.post_data_json
        if body['action'] == 'reply' and not failed:
            failed.append(True)
            response = route.fetch()  # Server applies the reply; client loses its response.
            assert response.ok
            route.abort()
        else:
            route.continue_()
    page.route('**/api/solo/action', lose_reply)
    move(page, 'e2e4')
    expect(page.locator('#solo-retry')).to_be_visible()
    game = session(page, manager)
    assert game.board.ply() == 2 and len(game.reviews) == 1
    page.locator('#solo-retry').click()
    expect(page.locator('#solo-board')).to_have_attribute('aria-busy', 'false')
    expect(page.locator('#solo-turn')).to_have_text('Sua vez')
    assert game.board.ply() == 2 and len(game.reviews) == 1


def test_visual_setup_shared_appearance_and_persistence(solo_page):
    page, _ = solo_page
    page.locator('#solo-open').click()
    expect(page.locator('#solo-form select')).to_have_count(0)
    page.locator('#solo-difficulty input[value="medium"]').check()
    page.locator('#solo-help input[value="review"]').check()
    page.locator('[data-appearance="theme"][data-option="midnight"]').click()
    page.locator('[data-appearance="skin"][data-option="soft"]').click()
    assert page.evaluate('document.documentElement.dataset.theme') == 'midnight'
    assert page.evaluate("JSON.parse(localStorage.getItem('chesslab.appearance.v1')).skin") == 'soft'
    output = ROOT / 'artifacts/solo-ui'
    output.mkdir(exist_ok=True)
    for name, size in [('desktop', (1440,1000)), ('mobile',(390,844))]:
        page.set_viewport_size({'width':size[0], 'height':size[1]})
        page.screenshot(animations="disabled", path=str(output / f'setup-{name}.png'))
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        expect(page.locator('#solo-pose')).to_be_in_viewport()
    page.locator('#solo-start').click()
    expect(page.locator('#solo-board .square')).to_have_count(64)
    expect(page.locator('#solo-board [data-square="g1"] img')).to_have_attribute('src', '/static/pieces/skins/soft/white-n.svg')
    expect(page.locator('#solo-hint')).to_be_hidden()
    page.locator('#solo-look-open').click()
    for theme in ['laboratory', 'matcha', 'strawberry', 'midnight', 'lavender', 'elmore', 'watterson']:
        option = page.locator(f'[data-appearance="theme"][data-option="{theme}"]')
        option.click()
        preview = option.locator('.solo-swatch-preview i').first.evaluate('el => getComputedStyle(el).backgroundColor')
        actual = page.locator('#solo-board [data-square="a8"]').evaluate('el => getComputedStyle(el).backgroundColor')
        assert preview == actual, theme
    page.locator('[data-appearance="theme"][data-option="watterson"]').click()
    page.locator('[data-appearance="skin"][data-option="cartoon"]').click()
    expect(page.locator('#solo-board [data-square="g1"] img')).to_have_attribute('src','/static/pieces/skins/cartoon/white-n.svg')
    page.locator('[data-close="solo-look"]').click()
    page.reload(); page.locator('#solo-open').click()
    expect(page.locator('[data-appearance="theme"][data-option="watterson"]')).to_have_attribute('aria-pressed','true')
    expect(page.locator('[data-appearance="skin"][data-option="cartoon"]')).to_have_attribute('aria-pressed','true')
    page.locator('#solo-back').click()
    # The original appearance controls read the same preference; there is no Solo copy.
    expect(page.locator('#board-theme')).to_have_value('watterson')
    expect(page.locator('#piece-skin')).to_have_value('cartoon')


def test_history_containment_summary_dialog_focus_and_final_screenshots(solo_page):
    page, manager = solo_page
    enter(page)
    move(page, 'g1f3')
    output = ROOT / 'artifacts/solo-ui'; output.mkdir(exist_ok=True)
    game = session(page, manager)
    original = page.locator('#solo-board').bounding_box()
    # Stress server-owned review history without making the main document taller.
    game.reviews.extend([dict(game.reviews[0]) for _ in range(79)])
    page.locator('#solo-back').click(); page.locator('#solo-open').click(); page.locator('#solo-resume').click()
    expect(page.locator('#solo-history-open')).to_contain_text('(80)')
    expect(page.locator('#solo-analysis')).not_to_be_visible()
    assert page.locator('#solo-board').bounding_box()['height'] == original['height']
    for name, size in [('desktop',(1440,1000)), ('mobile',(390,844)), ('small',(320,568)), ('landscape',(844,390))]:
        page.set_viewport_size({'width':size[0], 'height':size[1]})
        assert page.evaluate('document.documentElement.scrollHeight <= innerHeight + 1')
        expect(page.locator('#solo-board')).to_be_in_viewport(ratio=1)
        board_box = page.locator('#solo-board').bounding_box()
        assert abs(board_box['height'] - board_box['width']) < 1
        for square in ('a8', 'h8', 'a1', 'h1'):
            expect(page.locator(f'#solo-board [data-square="{square}"]')).to_be_in_viewport(ratio=.99)
        expect(page.locator('#solo-pose')).to_be_in_viewport(ratio=1)
        if name in ('desktop','mobile'): page.screenshot(animations="disabled", path=str(output / f'game-{name}.png'))
    page.set_viewport_size({'width':1440, 'height':1000})
    page.locator('#solo-history-open').click()
    expect(page.locator('#solo-history li')).to_have_count(80)
    page.locator('#solo-analysis').evaluate('el => el.scrollTop = el.scrollHeight')
    assert page.evaluate('document.documentElement.scrollHeight <= innerHeight + 1')
    page.keyboard.press('Escape')
    expect(page.locator('#solo-history-open')).to_be_focused()
    page.locator('#solo-resign').click(); page.locator('#solo-resign-yes').click()
    expect(page.locator('#solo-summary')).to_be_visible()
    expect(page.locator('#solo-counts li')).to_have_count(8)
    for name, size in [('desktop',(1440,1000)), ('mobile',(390,844)), ('small',(320,568)), ('landscape',(844,390))]:
        page.set_viewport_size({'width':size[0], 'height':size[1]})
        page.locator('#solo-summary').evaluate('el => el.scrollTop = 0')
        box = page.locator('#solo-summary').bounding_box()
        professor = page.locator('#solo-professor').bounding_box()
        assert box['y'] >= 0 and box['y'] + box['height'] <= size[1] + 1
        assert box['x'] >= 0 and box['x'] + box['width'] <= size[0] + 1
        assert box['x'] >= professor['x'] + professor['width'] or box['y'] >= professor['y'] + professor['height']
        if name in ('desktop','mobile'): page.screenshot(animations="disabled", path=str(output / f'result-{name}.png'))
    page.set_viewport_size({'width':390, 'height':844})
    page.locator('#solo-analysis-open').click()
    expect(page.locator('#solo-analysis')).to_be_visible()
    expect(page.locator('#solo-summary')).not_to_be_visible()
    page.keyboard.press('Escape')
    expect(page.locator('#solo-analysis')).not_to_be_visible()
    page.locator('#solo-result-open').click()
    page.locator('#solo-new').click()
    expect(page.locator('#solo-setup')).to_be_visible()
    expect(page.locator('#solo-summary')).not_to_be_visible()
