# Entrega Solo Offline — 6 de setembro de 2026

Implementado localmente, sem commit nem push.

## Resultado
Modo Solo com quatro dificuldades Stockfish, seleção de cor, revisão obrigatória
após cada lance do usuário, ajuda progressiva opcional e revelação confirmada.
Pogona permanece visível e apresenta classificação/comentário com evidências
reais. Pós-jogo inclui precisão, contagens, acertos e conceitos a praticar.
Retomada na mesma aba, promoção com quatro opções e desistência confirmada.
Sem LLM, APIs pagas, login, banco, Elo ou dependências novas.

## Testes executados
- Suíte original antes das mudanças: **157 passaram**, 137,52 s.
- Solo e revisão na primeira rodada: **38 passaram**, 4,96 s.
- Suíte completa final: **202 passaram**, 150,09 s; nenhum teste ignorado.
- Após ajuste de concordância nos textos, revisão: **22 passaram**, 0,11 s.
- `python -m tests.smoke_solo`: partida real Stockfish desde o início,
  **1–0 por xeque-mate em 45 meios-lances**, 23 lances revisados,
  precisão estimada 98,3%. Conexões externas bloqueadas.
- Sintaxe Python válida e `git diff --check` sem problemas.
- Chromium real: desktop/mobile, dicas/revelação, partida/retomada/resumo,
  torre em a1 exposta, mate, subpromoção, storage indisponível/corrompido e
  resposta perdida recuperada sem duplicação. Sem erros JavaScript detectados.

Dois avisos preexistentes de depreciação Starlette/httpx e AnyIO permanecem.
Um seletor genérico de balão no teste Aprender foi restrito à tela Aprender,
pois agora existem dois balões no DOM. O teste continuou verificando a mesma
geometria; nenhuma regra/objetivo de Aprender foi alterada.

Screenshots inspecionados visualmente: `artifacts/solo-desktop.png` e
`artifacts/solo-mobile.png`. Registro da partida: `artifacts/solo-full-game.json`.
Artefatos locais ignorados pelo Git. O bloqueio de rede ocorreu dentro dos
processos de teste, sem desligar interfaces ou alterar configurações do sistema.

## Arquivos criados
- `backend/solo_engine.py`
- `backend/move_review.py`
- `backend/solo.py`
- `frontend/board_view.js`
- `frontend/solo.js`
- `frontend/solo.css`
- `tests/test_solo.py`
- `tests/test_move_review.py`
- `tests/test_browser_solo.py`
- `tests/smoke_solo.py`
- `docs/solo/IMPLEMENTATION.md`
- `docs/solo/VALIDATION.md`

## Arquivos alterados
- `README.md`
- `backend/analysis.py`
- `backend/main.py`
- `frontend/index.html`
- `frontend/learning.js`
- `tests/test_browser_learning.py`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/solo/DECISIONS.md`
- `docs/solo/README.md`
- `docs/solo/TESTING.md`

## Limitações e pendências
- Offline exige servidor local ativo, dependências e binário Stockfish. Não há
  PWA nem execução integral no navegador. Reiniciar o servidor apaga a partida.
- A análise curta é aproximada. Genial, notas e níveis precisam de calibração
  com mais partidas humanas; Iniciante ainda pode ser forte para quem começa.
- Sobrecarga, descoberta, peão passado e sequências longas de troca não têm
  detectores completos. Não há reanálise profunda no pós-jogo.
- Casos sem diagnóstico específico usam atividade concreta da peça/casa,
  evitando inventar uma causa tática. Ver `IMPLEMENTATION.md` para cobertura.
- Os testes de partida usam automação; não houve teste com dois dispositivos
  físicos nesta entrega. Multiplayer foi validado por HTTP/WebSocket e Chromium.
- Revisão do usuário e autorização de commit/push continuam pendentes.
