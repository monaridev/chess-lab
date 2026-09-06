# Revisão visual e UX do Solo

## Entrega
A interface do Solo foi revisada com base nas duas referências fornecidas em
`chesslab_solo_ui_refs/`, preservando a lógica aprovada. A revisão do usuário e a
autorização de commit/push foram concedidas na conversa.

- Preparação com hierarquia visual, opções segmentadas de dificuldade, cor e
  ajuda, além de amostras de temas e estilos de peças.
- Aparência usa os controles, tokens, assets e localStorage já existentes.
- Desktop com Pogona/classificação à esquerda, tabuleiro central e ajuda/ações
  à direita. A nota aparece uma vez junto do personagem; a fala é contextual.
- Histórico fechado por padrão, com contador e modal próprio de análise.
- Resultado automático em modal: motivo, precisão, chips de classificação,
  acertos, pontos a praticar, jogar novamente e análise completa.
- Altura da partida limitada à viewport. Tabuleiro dimensionado pela área
  disponível para manter as oito fileiras visíveis e quadradas.
- Mobile com professor em faixa própria, ajuda/ações recolhidas e modais abaixo
  do personagem. Na preparação, o botão principal permanece acessível.
- Dialogs nativos para navegação por teclado, Escape e contenção do foco.

## Preservação da lógica
Todos os arquivos `backend/*.py` mantiveram os mesmos hashes SHA-256 de antes
da revisão visual. Não houve mudança em Stockfish, regras, classificação,
comentários semânticos, precisão, API ou persistência de partidas.

A alteração de `app.js` restringe o comportamento de fechamento de formulários
aos dialogs que possuem formulário. Os novos dialogs de análise/resultado têm
seu próprio fechamento nativo, evitando interferência com os já existentes.
`appearance.css` permite reutilizar os tokens Laboratory também na amostra.

## Arquivos desta revisão
Interface e testes:
- `frontend/index.html`
- `frontend/solo.js`
- `frontend/solo.css`
- `frontend/app.js`
- `frontend/appearance.css`
- `tests/test_browser_solo.py`

Documentação:
- `docs/DECISIONS.md`
- `docs/solo/DECISIONS.md`
- `docs/solo/IMPLEMENTATION.md`
- `docs/solo/README.md`
- `docs/solo/VALIDATION.md`
- `docs/solo/UI_REVIEW.md`

As duas imagens fornecidas permanecem em `chesslab_solo_ui_refs/`.

## Validação visual e funcional
Chromium real, com requisições externas bloqueadas:
- seleção e persistência de aparência compartilhada;
- comparação das sete amostras de tema com as cores reais do tabuleiro;
- mudança de estilo das peças na preparação e durante a partida;
- 80 revisões no histórico sem aumentar a página ou alterar o tamanho do tabuleiro;
- histórico inicialmente fechado, rolagem interna e retorno de foco;
- resultado, análise completa, fechar/reabrir e jogar novamente;
- viewport de 320×568, 390×844, 844×390 e 1440×1000;
- tabuleiro quadrado e casas dos quatro cantos visíveis;
- Pogona visível e sem sobreposição com os modais.

## Screenshots finais
Arquivos locais em `artifacts/solo-ui/`:
- `setup-desktop.png` e `setup-mobile.png`;
- `game-desktop.png` e `game-mobile.png`;
- `result-desktop.png` e `result-mobile.png`.

As capturas de partida/resultado usam o cenário de teste com 80 revisões para
validar contenção do histórico. Não representam estatísticas de uma partida
humana. Capturas são realizadas com animações finalizadas e inspecionadas
visualmente. Esses artefatos de teste são ignorados pelo Git.

## Limitações restantes
- Em viewports pequenas, preparação, ajuda e modais podem precisar de rolagem
  interna. A página principal da partida permanece contida.
- A ajuda expandida no mobile é um painel temporário sobre parte da área de
  jogo, aberto pelo usuário, sem cobrir o professor.
- Validação feita em Chromium; não houve teste em Safari/iOS nem em dispositivos
  físicos nesta etapa.
- As limitações da análise curta e da execução offline com servidor local
  continuam descritas em `IMPLEMENTATION.md`; não foram alteradas pela revisão.

## Resultado final da suíte
`.venv/bin/pytest -q`: **204 testes passaram**, nenhum ignorado, em 216,84 s.
Os dois avisos de depreciação Starlette/httpx e AnyIO já existiam.
`git diff --check` passou. Comparação SHA-256 dos arquivos do backend passou.

O código visual já estava publicado no commit `f8386a3`. O complemento de
encerramento registra as decisões, cobertura, screenshots e limitações.
