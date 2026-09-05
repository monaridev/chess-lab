"""V1.2: cenários, legibilidade e revelação com dois clientes reais."""
import re
from pathlib import Path
import pytest
from playwright.sync_api import expect
from tests.test_browser import browser, live_server, pages, start_pair
from tests.test_browser_v11 import appearance

pytestmark = pytest.mark.browser
ARTIFACTS = Path(__file__).resolve().parent.parent / 'artifacts/v1.2'


@pytest.mark.parametrize('theme,scene,title', [
    ('elmore', 'school.svg', 'ELMORE SCHOOL'),
    ('watterson', 'cozy.svg', 'WATTERSON COZY'),
])
def test_special_theme_two_players_reveal_reconnect_and_mobile(pages, theme, scene, title):
    white, black, _ = start_pair(pages)
    appearance(white, theme, 'cartoon')
    appearance(black, theme, 'cartoon')
    expect(white.locator('#theme-name')).to_have_text(title)
    assert scene in white.locator('.game-layout').evaluate('n => getComputedStyle(n).backgroundImage')
    assert white.request.get(pages[3] + '/static/scenes/' + scene).ok
    expect(white.locator('#piece-skin option:checked')).to_have_text('Cartoon 2.0')
    # Lance real, depois revelação do lado preto, cuja orientação é invertida.
    white.locator('[data-square="e2"]').click()
    white.locator('[data-square="e4"]').click()
    expect(black.locator('#turn-label')).to_have_text('Sua vez')
    for level in range(1, 5):
        black.locator('#hint').click()
        expect(black.locator('#hint-content')).to_contain_text(f'PISTA {level} / 4')
        expect(black.locator('.hint-square')).to_have_count(0)
    black.locator('#reveal').click()
    expect(black.get_by_role('button', name='Continuar pensando')).to_be_focused()
    black.keyboard.press('Tab')
    expect(black.get_by_role('button', name='Mostrar jogada mesmo assim')).to_be_focused()
    black.keyboard.press('Shift+Tab')
    black.keyboard.press('Enter')
    expect(black.locator('#reveal-dialog')).not_to_be_visible()
    expect(black.locator('.hint-square')).to_have_count(0)
    black.locator('#reveal').click()
    black.get_by_role('button', name='Mostrar jogada mesmo assim').click()
    expect(black.locator('.hint-from')).to_have_count(1)
    expect(black.locator('.hint-to')).to_have_count(1)
    expect(black.locator('.hint-from .reveal-marker')).to_have_text('1')
    expect(black.locator('.hint-to .reveal-marker')).to_have_text('2')
    expect(black.locator('.hint-from')).to_have_attribute('aria-label', re.compile('origem da possibilidade revelada'))
    expect(black.locator('.hint-to')).to_have_attribute('aria-label', re.compile('destino da possibilidade revelada'))
    origin = black.locator('.hint-from').get_attribute('data-square')
    target = black.locator('.hint-to').get_attribute('data-square')
    assert black.locator('.hint-from').evaluate('n => getComputedStyle(n).backgroundColor') != black.locator('.hint-to').evaluate('n => getComputedStyle(n).backgroundColor')
    expect(white.locator('.hint-square')).to_have_count(0)
    black.context.set_offline(True)
    expect(white.locator('#black-presence')).to_have_text('Offline')
    black.context.set_offline(False)
    expect(black.locator('#connection')).to_have_text('Conectado')
    expect(black.locator('.hint-from')).to_have_attribute('data-square', origin)
    black.reload()
    expect(black.locator('.hint-to')).to_have_attribute('data-square', target)
    expect(black.locator('html')).to_have_attribute('data-theme', theme)
    # Todas as larguras mantêm as 64 casas e o diálogo dentro da tela.
    for width in (320, 390, 720, 768, 1024, 1440):
        black.set_viewport_size({'width': width, 'height': 900})
        assert black.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert black.locator('#board').bounding_box()['width'] >= min(width - 90, 250)
    black.set_viewport_size({'width': 390, 'height': 844})
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    black.screenshot(path=str(ARTIFACTS / f'{theme}-black-revealed-mobile.png'), full_page=True, animations='disabled')
    black.locator(f'[data-square="{origin}"]').click()
    black.locator(f'[data-square="{target}"]').click()
    expect(white.locator(f'[data-square="{target}"] img')).to_have_count(1)
    expect(black.locator('.hint-square')).to_have_count(0)
    expect(black.locator('#reveal-content')).not_to_be_visible()


@pytest.mark.parametrize('theme', ['elmore', 'watterson'])
def test_check_and_reveal_markers_do_not_hide_each_other(pages, theme):
    white, black, _ = start_pair(pages, fen='4k3/8/8/8/8/8/4r3/4K3 w - - 0 1')
    appearance(white, theme, 'cartoon')
    white.emulate_media(reduced_motion='reduce')
    white.locator('#reveal').click()
    white.get_by_role('button', name='Mostrar jogada mesmo assim').click()
    expect(white.locator('.hint-from.check')).to_have_count(1)
    cell = white.locator('.hint-from.check')
    assert cell.evaluate("n => getComputedStyle(n, '::before').content") == '"!"'
    assert cell.evaluate("n => getComputedStyle(n, '::before').borderTopWidth") == '0px'
    expect(cell.locator('.reveal-marker')).to_have_text('1')
    assert white.locator('#reveal-content').evaluate('n => getComputedStyle(n).animationName') == 'none'
    white.screenshot(path=str(ARTIFACTS / f'{theme}-check-reveal.png'), full_page=True, animations='disabled')
