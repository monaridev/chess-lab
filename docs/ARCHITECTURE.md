# Arquitetura — Chess Lab

## Objetivo
Aplicação multiplayer simples, confiável e fácil de entender.

## Stack
Backend:
- Python
- FastAPI
- WebSocket
- python-chess

Frontend:
- HTML
- CSS
- JavaScript puro

Persistência:
- nenhuma obrigatória;
- salas em memória.

## Topologia
```text
Browser A
   │ HTTP/WebSocket
FastAPI Server
   ├─ Room Manager
   ├─ Chess Game
   └─ Hint Engine
   │ HTTP/WebSocket
Browser B
```

O FastAPI também serve o frontend.

## Fonte da verdade
Cliente não envia "o tabuleiro agora é X".
Cliente envia "quero mover e2 para e4".

Servidor:
1. identifica jogador;
2. verifica turno;
3. verifica propriedade da peça;
4. valida com `python-chess`;
5. aplica;
6. atualiza estado;
7. transmite aos dois.

## Sala
Modelo conceitual:
```text
Room
├── code
├── board: chess.Board
├── white_player
├── black_player
├── connections
├── mode
├── hint_state
├── created_at
└── last_activity
```

## Código da sala
Código curto, 5–6 caracteres.
Evitar caracteres confusos como O/0 e I/1.

## WebSocket
Exemplo cliente → servidor:
```json
{"type":"move","from":"e2","to":"e4","promotion":null}
```

Servidor → clientes:
```json
{"type":"state","fen":"...","turn":"black","last_move":"e2e4","status":"playing"}
```

Erro:
```json
{"type":"error","code":"NOT_YOUR_TURN","message":"Agora é a vez do outro jogador."}
```

Dica:
```json
{"type":"hint","level":1,"message":"Existe uma peça sua sob ameaça."}
```

## Regras
Usar `python-chess` para:
- movimentos legais;
- xeque;
- xeque-mate;
- roque;
- en passant;
- promoção;
- afogamento;
- repetição;
- material insuficiente;
- outros finais relevantes.

## Orientação
Brancas enxergam brancas embaixo.
Pretas enxergam pretas embaixo.

## Reconexão
V1 deve tolerar refresh/queda curta.
Abordagem sugerida:
- servidor gera `player_token`;
- cliente salva token;
- reconecta usando token;
- servidor reassocia jogador.

Não é autenticação forte.

## Hint Engine
Sem Stockfish obrigatório ou IA externa.

Heurísticas:
- xeques disponíveis;
- capturas;
- atacantes/defensores;
- material;
- desenvolvimento;
- segurança do rei.

Valores simples:
- peão 1
- cavalo 3
- bispo 3
- torre 5
- dama 9

## Frontend
Responsabilidades:
- renderizar tabuleiro;
- mostrar cor/turno;
- destacar seleção, movimentos e último lance;
- enviar intenção;
- mostrar status;
- pedir e mostrar dicas.

Não decide sozinho o estado oficial.

## Estrutura sugerida
```text
chess-lab/
├── AGENTS.md
├── README.md
├── requirements.txt
├── .gitignore
├── backend/
│   ├── main.py
│   ├── rooms.py
│   ├── game.py
│   ├── hints.py
│   └── schemas.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
└── docs/
```

## Implantação
A V1 roda localmente.
Hospedagem futura deve aceitar Python/FastAPI/WebSocket.
Evitar acoplamento a provedor específico.

## Contrato implementado na V1

- `GET /`: frontend; assets em `/static/`.
- `GET /api/health`: confirmação de que o servidor está ativo.
- `POST /api/rooms`, corpo `{"mode":"normal"}` ou `{"mode":"assisted"}`:
  devolve `code`, `color`, `player_token` e `mode`.
- `POST /api/rooms/{code}/join`: reserva pretas e devolve a mesma estrutura.
  Código é tratado sem diferenciar maiúsculas/minúsculas; sala cheia retorna
  HTTP 409, inexistente/expirada retorna 404.
- `/ws/{code}`: recebe primeiro `{"type":"auth","token":"..."}`. Só aceita
  lances/dicas depois de identificar o jogador pelo token guardado no servidor.

O estado comum inclui `fen`, `turn`, `last_move` (UCI), `last_san`, `ply`,
`legal_moves` (UCI, incluindo as quatro promoções), `check`, `check_square`,
`status` (`waiting`, `playing`, `finished`), `result`, `winner`, `termination`
e presença por cor. O frontend deriva as peças visíveis do FEN recebido.

Dicas recebem `{"type":"hint"}` e devolvem nível, mensagem, pistas já
reveladas e `ply`. Na V1 original, o quarto nível continha a jogada UCI; esse
comportamento foi substituído pela revelação separada da V1.1 abaixo. A progressão
é individual, privada, limitada a quatro e reinicia após cada lance válido.
Na reconexão, o servidor transmite o estado atual e depois as pistas que o
jogador já revelou, se existirem.

Jogadas não dependem de confirmação do outro cliente. Um jogador pode fazer
seu lance enquanto o adversário está desconectado; ao voltar, o adversário
recebe a posição oficial. Uma sala sem segundo jogador ainda não aceita lances.

Locks por sala mantêm a ordem dos estados. Falhas de envio removem a conexão
e atualizam presença, sem desfazer a jogada. A aplicação limita mensagens;
o comando de execução recomendado também limita frames a 4096 bytes.

O cliente reconecta com espera progressiva de 0,5 a 5 segundos, mantém a posição
visível e desabilita jogadas enquanto estiver desconectado. Uma conexão
substituída por outra aba não reconecta em loop: oferece retomada manual.

## Extensão V1.1

`backend/analysis.py` encapsula Stockfish com UCI assíncrono de python-chess,
limites de 250 ms/profundidade 14, uma thread/32 MiB de hash, timeout total de
2 segundos e lock da engine com espera máxima de 0,5 segundo. Cache LRU de
128 FENs evita repetir trabalho. Falta, erro, timeout ou sobrecarga usam
`build_plan` heurístico em thread. Nenhuma dependência Python nova é necessária.

Cada conexão pode ter um pedido de ajuda em andamento. A análise usa uma
cópia da posição, em tarefa separada, sem manter o lock da sala; por isso o
mesmo jogador pode fazer seu lance e outras salas continuam disponíveis.
Antes de entregar a resposta, o servidor confere conexão, FEN e `ply`.
Posição antiga recebe `STALE_ANALYSIS`; desconexão cancela o pedido.

As quatro mensagens `hint` não contêm `move`, SAN, PV ou a explicação reservada
à revelação. `{"type":"reveal","confirmed":true,"ply":0}` solicita a jogada
para a posição confirmada. Modo, turno, término e confirmação são validados
no servidor. A resposta privada traz `move` (UCI), `san`, `explanation`,
`source` (`stockfish`/`heuristic`) e `ply`. A interface abre o modal antes de
enviar o pedido, destaca as duas casas e não joga pelo usuário.

Pistas e revelações são restauradas apenas ao dono na reconexão e apagadas
após um lance. Ao fechar o modal por cancelamento, mudança de posição ou queda
de conexão, o cliente não envia a revelação. Preferências de aparência usam
`localStorage`, nunca o protocolo multiplayer.

`appearance.css` centraliza tokens, estados e movimento reduzido. Skins Classic
mantêm os assets existentes; `pieces/skins/` inclui 48 SVGs originais, gerados
por `scripts/generate_skins.py`. As decisões visuais seguem os screenshots em
`docs/references/`.

## Refinamento V1.2

`special-themes.css` acrescenta cenários SVG originais e papel às estruturas
existentes. `elmore` e `cartoon` mantêm compatibilidade de preferências;
`watterson` é o novo tema. Os dois marcadores de revelação usam classes distintas,
números, legenda e rótulos acessíveis, sem mudar o payload do servidor.
`hints.py` acrescenta evidências de posição aos textos. Multiplayer, regras,
Stockfish/fallback e limites permanecem. Direção atual: `V1_2_SCOPE.md` e
`references/ref-gumball.png` (prioridade visual sobre screenshots anteriores).
