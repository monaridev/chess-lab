# Decisões — Chess Lab

## D-001 — Multiplayer desde a primeira versão
**Status:** aceita

O projeto já nasce multiplayer.

## D-002 — FastAPI + WebSocket
**Status:** aceita

Backend em Python com FastAPI e WebSocket.

## D-003 — python-chess
**Status:** aceita

Usar biblioteca para regras; não reimplementar o xadrez completo.

## D-004 — Frontend vanilla
**Status:** aceita

HTML, CSS e JavaScript puro.

## D-005 — Um servidor
**Status:** aceita

FastAPI serve backend e frontend.

## D-006 — Salas em memória
**Status:** aceita

Sem banco na V1.

## D-007 — Servidor como fonte da verdade
**Status:** aceita

Cliente envia intenção; servidor valida.

## D-008 — Sem conta
**Status:** aceita

Entrada por código.

## D-009 — Criador começa de brancas
**Status:** aceita

Segundo jogador recebe pretas.

## D-010 — Partida Assistida
**Status:** aceita

Dicas progressivas para os dois jogadores.

## D-011 — Sem engine externa obrigatória
**Status:** aceita

Nada de IA paga ou Stockfish obrigatório na V1.

## D-012 — Reconexão simples
**Status:** aceita

Token temporário por jogador é aceitável.

## D-013 — Estética
**Status:** aceita

Dark, laboratório, moderna, clean, não infantil.

## D-014 — Testes práticos multiplayer
**Status:** aceita

Testar dois clientes simultâneos antes de considerar pronto.

## D-015 — Token por aba e substituição de conexão
**Status:** aceita

O token aleatório do jogador fica em `sessionStorage`. A identificação é a
primeira mensagem do WebSocket, com prazo de 10 segundos; o token não vai na
URL nem no estado compartilhado. Só uma conexão por cor fica ativa. Uma nova
conexão com o mesmo token encerra a anterior e assume a sessão.

Motivo: sobreviver a refresh/quedas e permitir testar dois jogadores em abas
independentes, sem contas. Fechar a aba pode perder a credencial. Dicas já
reveladas são restauradas apenas para seu dono na reconexão.

## D-016 — Empates automáticos na V1
**Status:** aceita

Além dos finais automáticos de `python-chess`, encerrar automaticamente quando
a posição atual atingir repetição tripla ou 100 meios-lances sem movimento de
peão/captura. Não antecipar um empate que dependeria do próximo lance.

Motivo: manter a interface de aprendizado simples, sem fluxo de reivindicação.
É uma simplificação explícita em relação ao xadrez de torneio. Mate tem
precedência sobre a contagem de lances.

## D-017 — Limites das salas em memória
**Status:** aceita

Usar um processo/worker. Expirar salas sem conexões após 24 horas de
inatividade; nunca expirar uma sala conectada. Limitar a 500 salas simultâneas
por processo. A limpeza roda periodicamente e ao acessar/criar salas.

Motivo: impedir crescimento ilimitado de memória mantendo tempo suficiente
para reconexão. Reiniciar o processo apaga partidas, conforme o escopo da V1.

## D-018 — Serialização por sala e assets locais
**Status:** aceita

Um lock por sala ordena aplicação de lances e broadcasts. Clientes recebem
o mesmo FEN, turno, lances legais, presença e resultado; mensagens de erro e
dica ficam privadas. A validação rejeita campos extras, incluindo estados
de tabuleiro enviados pelo cliente.

Frontend e peças SVG são servidos localmente pelo FastAPI, sem CDN, fontes
remotas ou engine externa. Dicas são calculadas sob demanda, por heurísticas
de captura, segurança, desenvolvimento e atividade, e cacheadas por posição.

## D-019 — Dicas pedagógicas e revelação explícita na V1.1
**Status:** aceita

As decisões V1.1-015 a V1.1-019 em `V1_1_DECISIONS.md` substituem a entrega
do lance no quarto nível: pistas 1–4 ensinam a observar, localizar, entender
e aproximar o objetivo. A ação separada de revelar exige confirmação,
é privada e vinculada à posição. A análise não executa lances.

## D-020 — Stockfish local opcional e análise fora do fluxo de lances
**Status:** aceita

Complementa D-011 e D-018: Stockfish pode analisar localmente via subprocesso
UCI, sem serviço externo. Tem limites de tempo/profundidade/memória, cache LRU
por FEN e fila curta; falha usa heurísticas. Análises não seguram o lock da
sala nem bloqueiam o event loop; respostas obsoletas são descartadas.

Instalação opcional dentro de `.tools/`, caminho configurável em
`STOCKFISH_PATH`. Binário não é versionado. Em falha, usar fallback até o
processo ser reiniciado, sem tentativas contínuas de relançar o executável.

## D-021 — Refinamento visual e personalização local
**Status:** aceita

As decisões V1.1-020 a V1.1-027 em `V1_1_DECISIONS.md` orientam a extensão
da identidade aprovada: seis temas por tokens, cinco skins e preferências
em `localStorage`. Classic permanece; Soft, Cute, Minimal e Cartoon têm
SVGs originais. Elmore não usa personagens, logos ou cenários oficiais.

Manter sinais além da cor para xeque, seleção, último lance e revelação,
foco visível, suporte a teclado e `prefers-reduced-motion`. Nenhuma
preferência é enviada ao outro jogador.

## D-022 — Referência visual principal da V1.2
**Status:** aceita

`references/ref-gumball.png` tem prioridade sobre direções visuais anteriores.
Preservar a estrutura de três áreas e todo o comportamento da V1.1; criar
cenários SVG e recortes CSS originais, sem incorporar a imagem de referência
nem assets oficiais. Elmore School usa armários escolares; Watterson Cozy,
superfícies de madeira, plaid e detalhes domésticos. Papel pautado e fita
organizam o painel de dicas. A decoração não intercepta cliques do tabuleiro.

## D-023 — Compatibilidade de aparência e revelação na V1.2
**Status:** aceita

Preservar os IDs `elmore` e `cartoon`, mudando apenas os nomes para Elmore School
e Cartoon 2.0. Adicionar `watterson` à lista permitida de preferências locais.
Demais temas, skins e chaves de armazenamento continuam intactos.

A revelação usa origem/destino com cores distintas, números 1/2, legenda e
rótulos acessíveis. Mantém o modal obrigatório e aparece no topo do painel
para facilitar a comparação com o tabuleiro. Xeque tem sinal próprio quando
coincide com a origem. Todas as pistas continuam disponíveis para leitura.

Os textos acrescentam evidências de desenvolvimento, casas centrais,
defensores e alvos; preservam o contrato sem destino exato nos níveis 1–4.
Nenhuma mudança no protocolo, no analisador Stockfish ou nas regras.

## D-024 — Deploy Railway com um processo e Stockfish empacotado
**Status:** aceita

Container Python 3.12, dependências de runtime fixadas e Stockfish 15.1-4 do
Debian Bookworm. Start script usa `0.0.0.0:${PORT:-8000}`, `exec` e um worker.
Railway mantém uma réplica, healthcheck HTTP e suspensão desativada. Sem banco,
volume ou mudança nas salas em memória. Reinícios/redeploys encerram partidas.

Contexto Docker permite somente código/assets e dependências necessários.
Git exclui credenciais, ambientes, caches, logs e ferramentas/artefatos locais.
GitHub Actions valida a imagem sem autenticar ou fazer deploy no Railway.
Configuração e operação documentadas em `RAILWAY.md`.

## Template
```md
## D-XXX — Nome
**Status:** proposta | aceita | substituída

Descrição.

Motivo:
- ...
```
