# Chess Lab

Chess Lab é um site multiplayer de xadrez para duas pessoas jogarem e aprenderem juntas.

## Stack
- Python
- FastAPI
- WebSocket
- python-chess
- HTML
- CSS
- JavaScript puro

## Documentação
- `AGENTS.md` — instruções permanentes para agentes
- `docs/PRODUCT.md` — visão do produto
- `docs/ARCHITECTURE.md` — arquitetura
- `docs/V1_SCOPE.md` — escopo da primeira versão
- `docs/DECISIONS.md` — decisões do projeto
- `PROMPT_V1.md` — prompt inicial pronto para Codex/Astra
- `PROMPT_V1_1.md` e `docs/V1_1_SCOPE.md` — evolução das dicas e da aparência
- `docs/V1_1_DECISIONS.md` — decisões complementares da V1.1
- `docs/V1_2_SCOPE.md` — refinamento visual e pedagógico da V1.2
- `docs/references/ref-gumball.png` — referência visual principal da V1.2

## Objetivo da V1
Permitir:
1. criar uma sala;
2. compartilhar um código;
3. entrar por outro dispositivo;
4. jogar em tempo real;
5. validar regras no servidor;
6. sincronizar os dois tabuleiros;
7. usar um modo de partida assistida com dicas.

Sem login, banco, ranking ou matchmaking na V1.

## Publicar no Railway

O projeto está preparado com Dockerfile, Stockfish e uma única réplica.
Selecione `monaridev/chess-lab`, branch `main`, usando a raiz do repositório.
Não é necessário definir variáveis manualmente: `PORT` vem do Railway e
`STOCKFISH_PATH` já está na imagem. Veja [o guia de implantação](docs/RAILWAY.md)
para domínio HTTPS, validação e limites das salas em memória.

## Executar

Requer Python 3.12 ou superior. Na raiz do projeto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --ws-max-size 4096
```

Abra **http://localhost:8000**. Use **um único processo/worker**, pois as salas ficam em memória. `--reload` pode ser usado no desenvolvimento, mas qualquer reinicialização apaga as partidas.

Se o sistema tiver `pip` mas não `ensurepip`/`python3-venv`, é possível preparar o ambiente sem mudar pacotes globais:

```bash
python3 -m venv --without-pip .venv
python3 -m pip --python .venv install -r requirements-dev.txt
```

## Jogar em dois dispositivos

1. Inicie o servidor com `--host 0.0.0.0`.
2. Descubra o IP local do computador, por exemplo com `hostname -I` no Linux.
3. No computador e no celular conectados à mesma rede, abra `http://IP-DO-COMPUTADOR:8000`. No celular, `localhost` apontaria para o próprio celular.
4. Escolha o modo e clique em **Criar sala**. Compartilhe o código de seis caracteres.
5. No segundo dispositivo, entre pelo código. O criador recebe brancas; o segundo jogador, pretas.
6. Clique em uma peça e num destino destacado. Na promoção, escolha a peça no diálogo.

A rede precisa permitir acesso à porta 8000 entre os dispositivos. Não é necessário serviço externo. Para acesso pela internet seria necessário hospedar o servidor com HTTPS/WSS; essa implantação não faz parte da V1 local.

Na V1.2, **Pedir dica** só fica ativo no modo assistido, no turno do jogador. As quatro pistas ensinam a observar, localizar, entender a ideia e aproximar o objetivo; não incluem automaticamente o lance exato. São privadas e reiniciam depois de um lance.

**Revelar uma possibilidade** é uma ação separada. O modal prioriza **Continuar pensando**; **Mostrar jogada mesmo assim** confirma a revelação. Só então aparecem notação, origem amarela marcada com **1**, destino verde marcado com **2**, legenda e explicação. O aviso de xeque permanece visível quando coincide com a origem. É possível revelar antes de terminar as quatro pistas. A confirmação vale apenas para a posição atual e não executa a jogada.

## Stockfish opcional (V1.1)

A aplicação continua funcionando sem Stockfish. Para ativá-lo, instale um binário local compatível com seu sistema e configure o caminho:

```bash
STOCKFISH_PATH=/caminho/para/stockfish .venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --ws-max-size 4096
```

Ordem de descoberta: `STOCKFISH_PATH`, `.tools/stockfish/stockfish` dentro do projeto, ou `stockfish` no PATH. `STOCKFISH_PATH=""` desabilita a engine explicitamente. Nesta instalação, Stockfish 19 foi baixado da distribuição oficial e instalado em `.tools/stockfish/`, com checksum SHA-256 verificado. `.tools/` não é versionada; não houve instalação de serviço nem alteração global.

A engine local UCI analisa até três candidatos, com limite de 250 ms e profundidade 14, uma thread e 32 MiB de hash. Comunicação e espera são assíncronas. Há timeout de 2 segundos para inicialização e análise combinadas e fila de espera limitada a 0,5 segundo; resultados são cacheados por FEN (até 128 posições). O módulo pedagógico verifica os candidatos no tabuleiro e produz as explicações.

Se o executável faltar, falhar, travar ou estiver ocupado, entram as heurísticas locais, executadas fora do event loop. Após falha da engine, o processo usa fallback até reiniciar; resultados já cacheados permanecem. Em nenhum modo a análise altera o tabuleiro oficial. Pedidos obsoletos são descartados quando a posição muda.

Fontes: [Stockfish oficial](https://stockfishchess.org/download/) e [UCI assíncrono do python-chess](https://python-chess.readthedocs.io/en/latest/engine.html). O pacote local mantém os arquivos de autoria/licença GPLv3 e fontes fornecidos pela distribuição.

## Aparência (V1.2)

Abra **Aparência** no painel da sala. As escolhas ficam em `localStorage`, sem conta e sem mensagens ao outro jogador:

- Temas: Laboratory, Matcha, Strawberry Milk, Midnight, Lavender, Elmore School e Watterson Cozy.
- Skins: Classic, Soft, Cute, Minimal e Cartoon 2.0.

Classic preserva as peças da V1. As quatro novas skins usam SVGs originais locais. Elmore School traz armários vermelhos, azul escolar, papel pautado, fitas e doodles. Watterson Cozy usa madeira, plaid, luminária e tons quentes de uma sala acolhedora. Os cenários e stickers são SVGs originais. Cartoon 2.0 melhora contornos e silhuetas sem transformar peças em personagens. As preferências antigas `elmore` e `cartoon` continuam válidas; o novo tema usa `watterson`. Todos mantêm coordenadas, foco, xeque, seleção, último lance e destaque da possibilidade revelada. Animações respeitam `prefers-reduced-motion`. Se o armazenamento estiver bloqueado, a escolha funciona até recarregar a página.

## Reconexão e finais

- O navegador guarda o token em `sessionStorage`, separado por aba. Refresh e queda breve recuperam cor, tabuleiro e dicas já reveladas. Mantenha a aba original aberta; o código sozinho não recupera um lugar ocupado.
- **Início → Retomar partida** preserva a sessão nesta aba. Fechar a aba ou apagar seus dados pode perder o token. Uma nova conexão com o mesmo token substitui a anterior.
- As salas sem conexões expiram após 24 horas de inatividade. Reiniciar o processo apaga todas as salas. Há limite de 500 salas por processo.
- Mate, afogamento e material insuficiente encerram a partida. Na V1, a repetição tripla e os 50 lances sem captura/movimento de peão também encerram automaticamente, quando a condição já ocorreu; não há botão de reivindicar empate. Veja `docs/DECISIONS.md`.
- Dicas usam análise local opcional e evidências do tabuleiro, com fallback heurístico; podem ser imprecisas. Não há adversário de IA nem API paga.

## Testes

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
PLAYWRIGHT_BROWSERS_PATH="$PWD/.browsers" .venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest -q
```

No ambiente alternativo sem pip dentro da `.venv`, use `python3 -m pip --python .venv install -r requirements-dev.txt` para instalar.

Os testes de navegador iniciam seu próprio servidor em uma porta livre, abrem dois contextos independentes do Chromium (desktop e celular), verificam HTTP/WebSocket reais e salvam capturas em `artifacts/`. Chromium é apenas uma ferramenta de teste, não uma dependência para rodar a aplicação.

Somente backend, sem instalar navegador:

```bash
.venv/bin/python -m pytest -q --ignore=tests/test_browser.py --ignore=tests/test_browser_v11.py --ignore=tests/test_browser_v12.py
```

Com o servidor já iniciado, teste dois clientes contra um endereço específico:

```bash
.venv/bin/python -m tests.smoke_network --url http://IP-DO-COMPUTADOR:8000
```

Cobertura e evidências: `docs/TESTING.md`.

## Estrutura implementada

```text
backend/
  main.py       # FastAPI, HTTP, WebSocket e frontend estático
  rooms.py      # Salas, tokens, presença, expiração e ordem dos broadcasts
  game.py       # Validação e estado oficial via python-chess
  hints.py      # Heurísticas e quatro níveis de ajuda
  analysis.py   # Stockfish opcional, limites, cache e fallback
  schemas.py    # Mensagens aceitas e validação de entrada
frontend/
  index.html    # Entrada, partida e diálogo de promoção
  styles.css    # Tema dark e layout responsivo
  appearance.css # Tokens dos temas, estados e microinterações
  special-themes.css # Cenários, papel e destaques da V1.2
  scenes/       # Cenários e stickers SVG originais
  app.js        # Renderização, cliques, dicas e reconexão
  pieces/       # SVGs locais das peças
tests/          # Regras, integração, navegador e smoke de rede
```

Dependências de execução: FastAPI, Uvicorn, python-chess e websockets; desenvolvimento: pytest, httpx e Playwright. Versões utilizadas estão fixadas nos arquivos `requirements*.txt`.

## Possíveis próximos passos (V2)

Melhorar a qualidade pedagógica das heurísticas e ampliar os testes para navegadores móveis físicos. Qualquer ampliação de escopo deve ser decidida antes de implementar.

## Créditos

Regras e renderização SVG das peças: `python-chess` (GPL-3.0-or-later). Os desenhos das peças incluídos pela biblioteca são de Colin M. L. Burnett (licenciamento triplo GFDL/BSD/GPL, distribuídos aqui sob GPL). Consulte `frontend/pieces/ATTRIBUTION.md`.
