# Chess Lab

Chess Lab é um site multiplayer de xadrez para duas pessoas jogarem e aprenderem juntas, com partidas em tempo real, dicas progressivas e personalização visual.

**Jogar agora:** https://chesslab.up.railway.app

## Destaques

- multiplayer em tempo real com salas por código;
- regras validadas no servidor com `python-chess`;
- modo normal e modo assistido;
- dicas progressivas para ajudar a entender a posição;
- revelação opcional de uma possibilidade, com confirmação antes de mostrar o lance;
- análise local com Stockfish quando disponível e fallback heurístico;
- reconexão da sessão na mesma aba;
- temas e skins de peças salvos localmente;
- interface responsiva para desktop e mobile.

## Aparência

Temas disponíveis:

- Laboratory
- Matcha
- Strawberry Milk
- Midnight
- Lavender
- Elmore School
- Watterson Cozy

Skins disponíveis:

- Classic
- Soft
- Cute
- Minimal
- Cartoon 2.0

Os temas especiais usam cenários, stickers e elementos SVG originais criados para o projeto.

## Stack

**Backend**
- Python
- FastAPI
- WebSocket
- python-chess
- Stockfish opcional

**Frontend**
- HTML
- CSS
- JavaScript puro

**Deploy**
- Railway
- Docker

## Como funciona

Um jogador cria uma sala e recebe um código de seis caracteres. O segundo jogador entra usando esse código e os dois tabuleiros ficam sincronizados via WebSocket.

O servidor é a fonte de verdade da partida: ele valida os lances, mantém o estado do jogo e distribui as atualizações para os dois clientes.

No modo assistido, as dicas ajudam o jogador de forma progressiva:

1. **Observe** — chama atenção para algo importante na posição;
2. **Olhe mais perto** — direciona para uma peça, região ou linha relevante;
3. **Entenda a ideia** — apresenta o conceito por trás da posição;
4. **Uma possibilidade** — aproxima o jogador de uma solução sem executar o lance.

A opção **Revelar uma possibilidade** fica separada e só mostra o lance após confirmação.

## Aprender com o Pogona

Na tela inicial, clique em **Aprender com o Pogona**. São seis capítulos e
19 exercícios interativos, com professor sempre visível, pistas progressivas,
revelação opcional confirmada e progresso salvo neste navegador. A partida
guiada é um roteiro curto até o mate, sem IA adversária. Normal e Assistido
continuam disponíveis para duas pessoas.

Documentação do currículo, assets e expansão: [docs/pogona/IMPLEMENTACAO.md](docs/pogona/IMPLEMENTACAO.md).
Testes específicos: `.venv/bin/pytest -q tests/test_learning.py tests/test_browser_learning.py`.

## Modo Solo Offline

Na tela inicial, escolha **Modo Solo** para jogar contra Stockfish local nas
dificuldades Iniciante, Fácil, Médio ou Difícil. Escolha brancas/pretas e revisão
pós-lance com ou sem dicas progressivas. O Professor Pogona comenta cada lance
com evidências da posição; o fim da partida mostra precisão estimada e resumo.

Este modo exige o binário Stockfish local (o caminho habitual ou `STOCKFISH_PATH`).
Com aplicação, dependências e binário instalados, funciona sem internet usando o
servidor local. Sem LLM, serviços externos, conta, banco ou Elo. Preferências e
estatísticas leves ficam no navegador; reiniciar o servidor apaga a partida.
Detalhes, comandos de teste e limites: [implementação Solo](docs/solo/IMPLEMENTATION.md).

## Rodar localmente

Requer Python 3.12 ou superior.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --ws-max-size 4096
```

Depois abra:

```text
http://localhost:8000
```

Como as salas ficam em memória, use apenas um processo/worker do servidor.

## Estrutura

```text
backend/       FastAPI, salas, regras, dicas e análise
frontend/      interface, temas, peças e lógica do cliente
tests/         testes de regras, integração e navegador
docs/          arquitetura, decisões, escopos e documentação técnica
```

## Testes

A suíte cobre regras do xadrez, salas, WebSocket, multiplayer, reconexão, dicas, Stockfish/fallback e fluxos de navegador.

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Mais detalhes em [`docs/TESTING.md`](docs/TESTING.md).

## Documentação

- [`docs/PRODUCT.md`](docs/PRODUCT.md) — visão do produto
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — arquitetura
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — decisões técnicas
- [`docs/TESTING.md`](docs/TESTING.md) — validação e testes
- [`docs/RAILWAY.md`](docs/RAILWAY.md) — implantação
- [`docs/V1_SCOPE.md`](docs/V1_SCOPE.md) — escopo inicial
- [`docs/V1_1_SCOPE.md`](docs/V1_1_SCOPE.md) — evolução da V1.1
- [`docs/V1_2_SCOPE.md`](docs/V1_2_SCOPE.md) — evolução da V1.2

## Limitações atuais

- as salas ficam em memória e são perdidas quando o servidor reinicia;
- o projeto usa uma única réplica por esse motivo;
- as dicas são apoio pedagógico e podem não representar a melhor explicação possível em toda posição;
- não há login, ranking, matchmaking, chat ou adversário de IA.

## Créditos

O projeto usa `python-chess` para regras e integração com engines UCI. Créditos e informações de licenciamento das peças SVG estão em [`frontend/pieces/ATTRIBUTION.md`](frontend/pieces/ATTRIBUTION.md).
