# Validação da V1, V1.1 e V1.2

## V1.2 — refinamento validado

Antes das alterações, a V1.1 passou novamente nos **126 testes**. Cópia da
implementação preservada em `artifacts/v1.1-baseline/`. A comparação dos arquivos
confirma que regras (`game.py`), salas, protocolo, servidor e analisador
Stockfish continuam idênticos à V1.1. Classic, Soft, Cute, Minimal e o CSS
estrutural também foram preservados.

Na V1.2, a suíte contém **141 testes**, dos quais **55 usam Chromium real**
com FastAPI/HTTP/WebSocket e dois contextos independentes. Cobertura adicional:

- 35 combinações dos sete temas e cinco skins, com carregamento dos SVGs,
  preferência persistente, movimento válido e sincronização entre aparências;
- Elmore School e Watterson Cozy com quatro pistas, modal por teclado,
  revelação privada, marcadores 1/2, origem/destino distintos e rótulos acessíveis;
- pretas orientadas corretamente em emulação móvel, queda de rede, refresh,
  restauração da revelação e limpeza depois de executar a jogada;
- xeque e marcador de origem simultâneos, sem ocultar o aviso de xeque;
- larguras de 320, 390, 720, 768, 1024 e 1440 px sem overflow nos temas especiais,
  além das larguras e fluxos já cobertos pela V1/V1.1;
- texto específico de desenvolvimento, influência central (incluindo c7–c5),
  defensores e pressão sobre alvos, sem destino exato nas pistas;
- explicação de captura identificando corretamente peça e casa somente
  na revelação; tabuleiro original permanece inalterado pela análise.

Stockfish real passou em todos os **141 testes**, sem skips:
`artifacts/v1.2/tests-stockfish.txt`. A integração isolada usa o executável
local instalado; instalações sem ele podem marcar esse teste como skip.

A segunda rodada, com `STOCKFISH_PATH="" .venv/bin/python -m pytest -q`,
também passou nos **141 testes**, sem skips: `artifacts/v1.2/tests-fallback.txt`.
Todos os fluxos do navegador usaram heurísticas nessa rodada; o teste isolado
da engine continua apontando explicitamente para o executável real. As duas
rodadas finais emitiram somente os dois avisos conhecidos das dependências
de teste, sem erros JavaScript/console nos fluxos verificados.

O servidor atualizado foi iniciado novamente em `0.0.0.0:8000`. O smoke
passou localmente e pelo Cloudflare Quick Tunnel HTTPS existente: sala, dois
WebSockets, dicas, confirmação/revelação, rejeições, sincronização, reconexão
e partida até xeque-mate. Logs: `artifacts/v1.2/smoke-local.txt` e
`artifacts/v1.2/smoke-public.txt`. O reinício limpou as salas em memória,
conforme a arquitetura; nenhuma porta permanente ou configuração global foi criada.

### Inspeção visual

`docs/references/ref-gumball.png` foi aberta antes de alterar arquivos visuais.
Screenshots foram inspecionados no Chromium e comparados à referência:
armários vermelhos, caderno, fitas e stickers no Elmore; madeira, plaid,
luminária e tapete no Cozy; peças Cartoon 2.0 e modal em papel.
A revisão reduziu a altura do painel da sala, trouxe a revelação para o topo
das dicas e corrigiu a sobreposição dos indicadores de xeque/origem.

Evidências em `artifacts/v1.2/`: `elmore-desktop.png`, `watterson-desktop.png`,
respectivas capturas mobile e modal, `elmore-revealed.png`, capturas de xeque,
revelação das pretas no celular, 35 tabuleiros e `gallery.png` comparativa.
O frontend serve somente os desenhos originais em `frontend/scenes/`;
a imagem de referência não é incorporada ao produto.

### Limitações

Os dois clientes e os dispositivos móveis foram simulados no Chromium desta
máquina; não houve teste manual da V1.2 em dois aparelhos físicos nem em
Safari/Firefox. O smoke público verifica o caminho HTTPS/WSS do túnel, mas
não substitui esse teste manual. As explicações continuam pedagógicas e
limitadas, não uma demonstração completa da linha da engine. Salas continuam
em memória. Os avisos de depreciação de dependências de teste já existentes
na V1 não são erros do aplicativo.

## V1.1 — cobertura adicional

A suíte preserva as regras e os fluxos da V1 descritos abaixo. O teste antigo
que esperava um lance no nível 4 foi atualizado para o contrato da V1.1:
nenhuma pista 1–4 contém o lance; a revelação é uma ação separada.

Comando completo: `.venv/bin/python -m pytest -q`.

Rodada integrada com descoberta do Stockfish local: **126 testes passaram**,
incluindo 46 testes de navegador e 80 de backend/integração. Log completo em
`artifacts/v1.1/tests-final.txt`. Os dois avisos de depreciação já presentes
na V1 continuam restritos às dependências de teste.

Segunda rodada com `STOCKFISH_PATH=""`: **126 testes passaram** em fallback,
incluindo todos os fluxos de navegador. O teste isolado da integração real
continua apontando explicitamente para o binário local, para verificar também
o encerramento do subprocesso. Log: `artifacts/v1.1/tests-fallback.txt`.

O servidor atualizado foi iniciado em `0.0.0.0:8000`. O smoke de rede também
passou pelo Cloudflare Quick Tunnel HTTPS existente: criação/entrada, dois
WebSockets, quatro dicas, revelação confirmada, rejeições, reconexão e partida
até xeque-mate. Nenhuma configuração do roteador foi alterada.

Novos testes de backend verificam:

- Stockfish 19 real via subprocesso UCI, sugestão legal e mate detectado;
- engine ausente, erro, timeout, resposta ilegal e fila ocupada usando fallback;
- cache limitado e isolamento da cópia analisada;
- event loop responsivo e lance aplicado enquanto a análise está pendente;
- descarte de dica/revelação obsoleta, sem alterar a partida;
- pistas específicas de garfo, cravada, promoção, en passant, xeque,
  desenvolvimento e mate, sem origem/destino exatos na progressão;
- confirmação obrigatória, turno/modo/final, privacidade e restauração da
  revelação após reconexão.

Novos testes de navegador verificam:

- modal com foco inicial em Continuar pensando, cancelamento e Escape;
- quatro respostas sem UCI/SAN, revelação explícita e destaque das duas casas;
- privacidade, refresh e limpeza após lance; fechamento do modal offline;
- todas as 30 combinações dos seis temas com cinco skins, assets carregados
  e jogadas sincronizadas com um adversário usando outra aparência;
- persistência após refresh e nova aba, valores inválidos e armazenamento bloqueado;
- responsividade, indicação de xeque além da cor e animações desativadas
  com movimento reduzido.

Evidências em `artifacts/v1.1/`: 30 capturas dos tabuleiros, galeria comparativa,
modais desktop/mobile, tela de revelação e Elmore móvel em xeque. A V1 está
preservada para comparação em `artifacts/v1-baseline/`, além das referências
aprovadas em `docs/references/`.

Stockfish é opcional: em outra instalação, o teste do executável real é
marcado como skip se `.tools/stockfish/stockfish` não existir. Os testes de
fallback continuam obrigatórios. Nesta máquina o executável foi instalado
e a integração real foi executada.

Limitações: explicações são produzidas por regras pedagógicas locais e não
representam uma prova completa da linha calculada; análise é curta e pode
errar. Testes móveis aqui usam emulação no Chromium. O usuário informou que
a V1 já foi validada numa partida multiplayer real; isso não equivale a um
teste manual da V1.1 em dois aparelhos físicos.

## Registro anterior — V1

Validação executada em 05/09/2026, com Python 3.12 e Chromium headless instalado
localmente no projeto. Os testes iniciam e encerram servidores próprios; não
dependem de API paga, engine externa ou recursos fora da V1.

## Rodada final

```bash
.venv/bin/python -m pytest -q
```

72 testes: 61 de backend/integração e 11 de navegador. Os testes de navegador
usam FastAPI/Uvicorn real, TCP, HTTP, WebSocket e dois contextos independentes
de Chromium, um com tela e interação móvel.

As dependências de teste emitem dois avisos de depreciação internos de
Starlette/AnyIO e da integração Starlette/httpx. Eles não são erros da aplicação.

## Cobertura

| Fluxo | Validação |
| --- | --- |
| Servidor e frontend | Inicialização real, health, HTML, CSS, JavaScript e SVGs carregados |
| Salas | Criação em ambos os modos, brancas/pretas, código sem caracteres confusos, entrada sem distinguir caixa |
| Entrada inválida | Mensagens amigáveis para sala inexistente e cheia, inclusive na interface |
| Dois jogadores | Dois WebSockets autenticados, posições idênticas após cada lance, orientação inversa |
| Autoridade do servidor | Lance ilegal, fora do turno, peça adversária, casa vazia, FEN/campos extras e mensagens inválidas rejeitados |
| Integridade | Erros não mudam posição, turno nem histórico; salas isoladas; tokens não aparecem nos broadcasts |
| Concorrência | Disputa pelo segundo lugar reserva apenas uma vaga; nova conexão substitui a anterior |
| Reconexão | Presença offline/online, refresh, queda de rede do cliente, voltar ao início/retomar, estado e cor preservados |
| Falha de envio | Socket quebrado removido e fechado; jogador restante recebe presença corrigida |
| Roque | Roque pequeno e grande, deslocamento da torre; travessia de casa atacada rejeitada |
| En passant | Captura e remoção do peão; captura que exporia o rei rejeitada |
| Promoção | Quatro escolhas, ambas as cores, diálogo no desktop/celular, cancelamento e obrigatoriedade da escolha |
| Xeque | Indicação visual, resposta legal, rejeição de lance que mantém/expõe o rei em xeque |
| Partida completa | Sequência desde a posição inicial até xeque-mate, resultado sincronizado e bloqueio de lances posteriores |
| Empates | Afogamento, material insuficiente, 50 lances e repetição tripla sem antecipação |
| Dicas | Quatro níveis, sugestão legal apenas no quarto, privacidade, ambos os jogadores, reset após lance e restauração após refresh |
| Modo normal | Dicas desabilitadas na interface e rejeitadas no servidor |
| Expiração | Sala desconectada expira; sala conectada permanece; limite de capacidade |
| Interface | Clique/seleção/destinos/último lance, botão copiar, peças carregadas, ausência de erros JS/console nos fluxos normais |
| Responsividade | Larguras 320, 375, 390, 720, 768, 1024 e 1440 px sem overflow horizontal |

Nos testes de regras especiais, algumas posições são preparadas diretamente
no servidor isolado de testes. Não existe endpoint de manipulação de posição
na aplicação. Um teste adicional executa en passant e roque a partir da
posição inicial, por cliques alternados nos dois navegadores.

## Rede local

O servidor foi iniciado em `0.0.0.0:8000` e respondeu pelo IP LAN da máquina.
Dois clientes WebSocket independentes executaram criação/entrada, dicas,
rejeições, sincronização, desconexão/reconexão e uma partida até mate por esse
endereço, usando:

```bash
.venv/bin/python -m tests.smoke_network --url http://IP-DO-COMPUTADOR:8000
```

Resultado esperado: `OK: HTTP, sala, dois WebSockets, dicas, rejeições,
sincronização, reconexão e xeque-mate.`

Limite da evidência: os clientes foram executados nesta máquina, com contextos
independentes e emulação móvel. Não houve teste manual em dois aparelhos
físicos. O README contém o procedimento para jogar em dois dispositivos na
mesma rede; a rede/firewall precisa permitir o acesso entre eles.

## Evidências visuais locais

A suíte salva em `artifacts/` (ignorado pelo Git):

- `lobby-desktop.png` e `lobby-mobile.png`;
- `game-desktop.png` e `game-mobile.png`.

As capturas foram inspecionadas visualmente para verificar tabuleiro, peças,
legibilidade, orientação, painéis e ausência de cortes de layout.

## Reexecutar

Consulte o README para instalar dependências e Chromium. Para testes sem
navegador, use `--ignore=tests/test_browser.py`. A suíte completa exige o
Chromium local e não omite esses testes silenciosamente se ele faltar.

## Preparação para GitHub/Railway

A suíte completa passou novamente: **141 testes**, dois avisos conhecidos de
 dependências. O produto V1.2 não foi alterado nesta tarefa de implantação.

O mesmo `scripts/start.sh` da imagem foi iniciado localmente com `PORT=18765`
e `PORT=18766`, escutando em `0.0.0.0`. Nos dois servidores, passaram HTTP,
dois WebSockets, quatro dicas, revelação, rejeições, sincronização, reconexão
e uma partida até xeque-mate. A segunda porta usou `STOCKFISH_PATH=""`.

`scripts/check_analysis.py` confirmou Stockfish real, fallback desativado e
fallback por executável inexistente. O pacote Debian Stockfish 15.1-4 usado
no Dockerfile também foi extraído localmente e passou na integração UCI.
`railway.toml` foi validado contra o schema oficial. Logs locais ficam em
`artifacts/deploy/`, fora do Git.

Não há Docker instalado na máquina local. A construção e os smokes da imagem
final são executados no GitHub Actions, pelo workflow `Validate Railway image`.
Consulte a execução correspondente ao commit antes de implantar. A automação
não acessa nem autentica no Railway; a seleção do repositório e geração do
domínio serão feitas pelo proprietário, conforme `RAILWAY.md`.

## Aprender com o Pogona

Validação final desta implementação: `.venv/bin/pytest -q` — **155 passed**,
116,13 s, dois avisos de depreciação já existentes em Starlette/httpx e AnyIO.
São 141 testes existentes e 14 novos (incluindo parametrizações). O sandbox
impediu iniciar Chromium; a execução completa foi autorizada fora dele.

- `test_learning.py`: seis capítulos/19 exercícios, todas as soluções aceitas,
  posições legais, xeque, mate, roque, garfo, ameaça segura, sequência da partida
  guiada, pistas progressivas, revelação, rejeições sem avanço, histórico
  inválido, campos extras e independência das salas.
- `test_browser_learning.py`: 19 exercícios jogados no Chromium, conclusão
  dos seis capítulos, progresso após reload, reinício, armazenamento corrompido
  ou bloqueado, falha de rede/recuperação, revelação confirmada/cancelada,
  tentativas erradas, volta ao multiplayer e retomada da sala.
- Responsividade: 320×568, 390×844, 720×900, 844×390, 1024×768 e 1440×1000;
  professor dentro do viewport mesmo ao rolar o conteúdo, sem sobreposição ao
  tabuleiro ou overflow horizontal. Imagens carregadas; fluxos normais sem
  erros de JavaScript/console. Falha de rede é exercitada separadamente.
- A suíte existente continua cobrindo servidor, HTTP, dois WebSockets, modos
  Normal/Assistido, regras especiais, sincronização, reconexão e análise/dicas.

Capturas locais inspecionadas: `artifacts/learning-desktop.png`,
`artifacts/learning-mobile.png` e a entrada atualizada em
`artifacts/lobby-desktop.png`. Artefatos permanecem ignorados pelo Git.
`git diff --check` passou; módulos Python novos compilam. Node não está
instalado, portanto o JavaScript foi validado pela execução real no Chromium.
Não houve teste manual em dois aparelhos físicos nesta implementação.
