# Chess Lab — Decisões da V1.1

Estas decisões complementam `docs/DECISIONS.md`. O prefixo `V1.1-` evita colisão com os identificadores D-015 a D-018 já usados pela V1; o conteúdo das decisões foi preservado. Veja também D-019 a D-021 no registro principal.

## V1.1-015 — Stockfish é analisador, não professor
**Status:** aceita

Stockfish pode avaliar a posição e candidatos, mas o Chess Lab transforma a análise em explicações pedagógicas.

## V1.1-016 — Níveis 1–4 não entregam automaticamente o lance exato
**Status:** aceita

A progressão normal é destinada ao raciocínio.

## V1.1-017 — Lance exato é uma ação separada
**Status:** aceita

O usuário usa `Revelar uma possibilidade`.

Antes da revelação, existe um modal explicando a diferença entre raciocinar e receber uma resposta calculada.

## V1.1-018 — Sem culpa ao revelar
**Status:** aceita

O produto não repreende nem diminui quem decide revelar a jogada.

## V1.1-019 — Stockfish possui fallback
**Status:** aceita

A indisponibilidade da engine não impede o funcionamento da Partida Assistida.

## V1.1-020 — V1 visual é a base
**Status:** aceita

A interface validada não será descartada. V1.1 é refinamento.

## V1.1-021 — Cute significa acolhedor, não infantil
**Status:** aceita

Evitar excesso de rosa, corações, mascotes, emoji e linguagem infantil.

## V1.1-022 — Personalização é local
**Status:** aceita

Tema e skin ficam no navegador e não precisam sincronizar entre jogadores.

## V1.1-023 — Temas iniciais
**Status:** aceita

- Laboratory
- Matcha
- Strawberry Milk
- Midnight
- Lavender

## V1.1-024 — Skins iniciais
**Status:** aceita

- Classic
- Soft
- Cute
- Minimal

## V1.1-025 — Acessibilidade acima de estética
**Status:** aceita

Nenhum tema/skin pode sacrificar legibilidade, contraste, foco ou reconhecimento das peças.
## V1.1-026 — Tema especial Elmore
**Status:** aceita

Adicionar um tema opcional inspirado na energia visual de *The Amazing World of Gumball*, sem copiar assets, personagens, logos ou cenários oficiais.

O tema deve usar composição, cores e elementos originais.

## V1.1-027 — Skin Cartoon original
**Status:** aceita

Adicionar uma skin de peças cartunesca e original, com formas suaves e expressivas, sem transformar peças em personagens protegidos.
