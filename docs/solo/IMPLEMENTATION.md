# Solo Offline — implementação

## Executar
Use o comando local habitual do README, com as dependências instaladas e o
binário `.tools/stockfish/stockfish`, `stockfish` no PATH ou `STOCKFISH_PATH`.
Abra o servidor local no navegador e escolha **Modo Solo**. O frontend, as peças,
o personagem, as regras, o adversário e os comentários não precisam de internet.
Não é uma PWA: fechar o servidor local impede jogar. A implantação remota continua
precisando de conexão do navegador ao servidor.

## Estrutura
- `backend/analysis.py`: inicialização/encerramento UCI reutilizados.
- `backend/solo_engine.py`: análise estrita com scores/PV e adversário por nível.
- `backend/move_review.py`: evidências, classificação, precisão e resumo.
- `backend/solo.py`: sessões, validação, retomada e API.
- `frontend/solo.js` e `solo.css`: fluxo isolado, Pogona permanente, dicas,
  promoção para quatro peças, desistência confirmada e resumo.
- `frontend/board_view.js`: renderização compartilhada com Aprender.

## API
`POST /api/solo` cria com `difficulty`, `color` e `help_mode`. Retorna token.
`GET /api/solo`, com cabeçalho `X-Solo-Token`, retoma o estado oficial.
`POST /api/solo/action`, com o mesmo cabeçalho, recebe `action` e `ply`:
`move` (UCI), `reply`, `hint`, `reveal` (confirmed), `resign` (confirmed).
FENs e campos extras são rejeitados. Ações são serializadas por sessão; análise
não bloqueia o event loop. Reinício apaga sessões. Credencial não vai na URL.

Scores, melhor lance e evidências detalhadas ficam na memória do servidor.
Respostas comuns não expõem centipawns nem a melhor jogada; revelação é explícita.
Histórico público contém apenas os lances revisados do usuário e comentários.
O tabuleiro mantém o histórico completo para repetição e regras de empate.

## Cobertura semântica e limites
Há evidências de captura, material sob ameaça na melhor resposta, peça pendurada
sem recaptura legal, ameaça ignorada, peça salva, mate encontrado/perdido/permitido,
xeque e defesa de xeque, promoção, desenvolvimento, centro, roque, garfo,
cravada e coluna aberta/semiaberta. O detector de conceitos de `hints.build_plan`
é reaproveitado; valores/nomes e regras também são compartilhados.

A análise é curta, portanto aproximada. Não promete detectar toda tática nem
explicar com certeza uma variante longa. Sobrecarga, descoberta, peão passado,
coordenação profunda, captura perdida e balanço completo de sequências de troca
não possuem detectores completos nesta versão. O fallback textual nesses casos
descreve a peça/casa e sua atividade, sem inventar uma causa específica.

Critérios de Genial e limiares de nota precisam de calibração futura com um
conjunto maior de partidas. Os níveis têm parâmetros e seleção distintos,
mas não equivalem a faixas de habilidade humana validadas. Não há análise mais
profunda pós-partida, desfazer, exportação ou histórico permanente.

## Persistência
`chesslab.solo.v1` em localStorage: última dificuldade/cor/ajuda, número de
partidas, melhor precisão e até dez precisões recentes. Sem tabuleiros ou tokens.
`chesslab.solo.session` em sessionStorage: credencial temporária e marcador para
não contar novamente o mesmo resumo ao recarregar. Storage bloqueado/corrompido
não impede jogar; pode impedir retomada e salvar estatísticas.

## Validação
- `.venv/bin/pytest -q`: suíte completa, incluindo Chromium real.
- `.venv/bin/python -m tests.smoke_solo`: partida desde a posição inicial até
  final natural, usando Stockfish local; bloqueia conexões externas e grava
  resultado em `artifacts/solo-full-game.json` (artefato local ignorado pelo Git).
- `tests/test_solo.py`: engine real/double, níveis, falhas, versões, atomicidade,
  isolamento, dicas, retomada, regras especiais e encerramento de processo.
- `tests/test_move_review.py`: categorias, contextos, evidências e precisão.
- `tests/test_browser_solo.py`: fluxo real, comentário de torre exposta, mate,
  subpromoção, resumo, storage, layouts e recuperação de resposta perdida.
  Requisições fora do servidor local são bloqueadas nesses testes.

## Revisão visual/UX

A preparação usa opções segmentadas e amostras visuais de todos os temas/skins
existentes. Durante a partida, o botão Aparência abre os mesmos controles num
modal. A chave de aparência é a compartilhada `chesslab.appearance.v1`.

O histórico fica fechado por padrão e abre em modal próprio. O resultado abre
em modal automaticamente; é possível fechá-lo, reabri-lo, acessar a análise
completa ou iniciar outra partida. A página principal não cresce com o histórico.
Em telas pequenas, modais têm rolagem interna e a ajuda adicional é recolhida.

Relatório e screenshots da revisão: `UI_REVIEW.md`.
