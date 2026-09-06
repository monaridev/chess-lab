"""Learning in real Chromium, alongside the unchanged multiplayer flow."""

import pytest
from playwright.sync_api import expect

from backend.learning import CHAPTERS
from tests.test_browser import browser, live_server, pages, start_pair, make_move

pytestmark = pytest.mark.browser


def enter(page, chapter='movimentos'):
    page.locator('#learn-open').click()
    expect(page.locator('#learn-catalog .learn-card')).to_have_count(6)
    page.locator(f'[data-chapter="{chapter}"]').click()
    expect(page.locator('#learn-board .square')).to_have_count(64)
    expect(page.locator('#learn-hint')).to_be_enabled()


def move(page, uci):
    page.locator(f'#learn-board [data-square="{uci[:2]}"]').click()
    page.locator(f'#learn-board [data-square="{uci[2:4]}"]').click()
    expect(page.locator('#learn-next')).to_be_visible()


def test_learning_progress_hints_errors_reload_and_multiplayer(pages):
    white, black, _, _ = pages
    enter(white)
    expect(white.locator('#pogona-pose')).to_be_visible()
    white.locator('#learn-board [data-square="e7"]').click()
    expect(white.locator('#learn-error')).to_contain_text('outro jogador')
    white.locator('#learn-board [data-square="a2"]').click()
    white.locator('#learn-board [data-square="a3"]').click()
    expect(white.locator('#learn-error')).to_contain_text('ainda não resolve')
    expect(white.locator('#learn-board [data-square="a2"] img')).to_have_count(1)
    for level in range(1, 5):
        white.locator('#learn-hint').click()
        expect(white.locator('#learn-hints li')).to_have_count(level)
    expect(white.locator('#learn-hint')).to_be_disabled()
    expect(white.locator('#learn-revealed')).to_be_empty()
    white.locator('#learn-reveal').click()
    white.locator('#learn-reveal-cancel').click()
    expect(white.locator('#learn-revealed')).to_be_empty()
    white.locator('#learn-reveal').click()
    white.locator('#learn-reveal-confirm').click()
    expect(white.locator('#learn-revealed')).to_contain_text('e2 → e4')
    move(white, 'e2e4')
    expect(white.locator('#pogona-pose')).to_have_attribute('src', '/static/assets/pogona/professor_pogona_elogiando.png')
    white.reload()
    enter(white)
    expect(white.locator('#learn-title')).to_have_text('Torre: linhas retas')
    white.locator('#learn-back').click()
    # Both preexisting modes still use their usual room/session flow.
    white, black, code = start_pair(pages, 'normal')
    make_move(white, black, 'e2e4')
    white.locator('#back').click()
    enter(white, 'abertura')
    white.locator('#learn-back').click()
    white.locator('#resume').click()
    expect(white.locator('#room-code')).to_have_text(code)
    expect(white.locator('#board [data-square="e4"] img')).to_have_count(1)


def test_all_chapters_interactive_and_completion(pages):
    page, _, _, _ = pages
    page.locator('#learn-open').click()
    expect(page.locator('#learn-catalog .learn-card')).to_have_count(6)
    for chapter in CHAPTERS:
        page.locator(f'[data-chapter="{chapter.id}"]').click()
        expect(page.locator('#learn-board .square')).to_have_count(64)
        for index, ex in enumerate(chapter.exercises):
            expect(page.locator('#learn-title')).to_have_text(ex.title)
            move(page, ex.answers[0])
            expect(page.locator('#learn-feedback')).to_have_text(ex.success)
            if index == len(chapter.exercises) - 1:
                expect(page.locator('#pogona-pose')).to_have_attribute('src', '/static/assets/pogona/professor_pogona_comemorando.png')
            page.locator('#learn-next').click()
        expect(page.locator(f'[data-chapter="{chapter.id}"]')).to_contain_text('Concluído')
    expect(page.locator('#learn-progress')).to_have_text('6 de 6 capítulos concluídos')
    page.reload()
    page.locator('#learn-open').click()
    expect(page.locator('#learn-progress')).to_have_text('6 de 6 capítulos concluídos')
    page.locator('[data-chapter="movimentos"]').click()
    expect(page.locator('#learn-title')).to_have_text('Capítulo concluído')
    page.locator('#learn-restart').click()
    expect(page.locator('#learn-title')).to_have_text('Peão: o primeiro passo')


def test_professor_stays_visible_without_board_overlap_and_assets(pages):
    page, mobile, _, _ = pages
    enter(page)
    enter(mobile)
    for width, height in [(320, 568), (390, 844), (720, 900), (844, 390), (1024, 768), (1440, 1000)]:
        page.set_viewport_size({'width': width, 'height': height})
        for scroll in [0, 5000]:
            page.locator('#learn-scroll').evaluate('(el, y) => el.scrollTop = y', scroll)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            professor = page.locator('#pogona-pose').bounding_box()
            assert professor['y'] >= 0 and professor['y'] + professor['height'] <= height
            board = page.locator('#learn-board').bounding_box()
            assert (professor['x'] + professor['width'] <= board['x'] or professor['y'] + professor['height'] <= max(board['y'], page.locator('#learn-scroll').bounding_box()['y']))
        page.locator('#learn-scroll').evaluate('el => el.scrollTop = 0')
    assert page.locator('#pogona-pose').evaluate('img => img.complete && img.naturalWidth > 0')
    assert page.locator('#learn-board img').evaluate_all('imgs => imgs.every(img => img.complete && img.naturalWidth > 0)')
    from tests.test_browser import ROOT
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    page.screenshot(path=str(ROOT / 'artifacts/learning-desktop.png'))
    mobile.screenshot(path=str(ROOT / 'artifacts/learning-mobile.png'))


def test_storage_corruption_and_blocking(pages):
    page, _, _, _ = pages
    page.evaluate("localStorage.setItem('chesslab.learning.v1', 'broken')")
    page.reload()
    enter(page)
    page.evaluate("() => { Storage.prototype.setItem = () => { throw new Error('blocked'); }; }")
    move(page, 'e2e4')
    expect(page.locator('#learn-storage')).to_contain_text('não permitiu salvar')
    page.locator('#learn-next').click()
    expect(page.locator('#learn-title')).to_have_text('Torre: linhas retas')


def test_learning_failed_request_can_retry(browser, live_server):
    base, _ = live_server
    with browser.new_context() as context:
        page = context.new_page()
        page.goto(base)
        enter(page)
        context.set_offline(True)
        page.locator('#learn-hint').click()
        expect(page.locator('#learn-error')).to_contain_text('Confira a conexão')
        expect(page.locator('#pogona-pose')).to_be_visible()
        context.set_offline(False)
        page.locator('#learn-hint').click()
        expect(page.locator('#learn-hints li')).to_have_count(1)
