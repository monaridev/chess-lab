# Chess Lab — Escopo V1.1

## Objetivo

Melhorar duas áreas sem expandir o produto horizontalmente:

1. qualidade pedagógica das dicas;
2. personalidade visual/personalização.

## Deve entrar

### Dicas
- níveis 1–4 pedagógicos;
- textos mais específicos à posição;
- Stockfish opcional;
- fallback heurístico;
- botão separado para revelar lance;
- modal de confirmação;
- explicação do lance revelado;
- limite de tempo/profundidade da engine.

### Visual
- refinamento sem redesign;
- mais suavidade;
- detalhes pastel;
- microinterações;
- melhor feedback de estados;
- manter identidade dark/laboratório.

### Temas
- Laboratory
- Matcha
- Strawberry Milk
- Midnight
- Lavender
- Elmore (tema especial, homenagem visual original)

### Skins
- Classic
- Soft
- Cute
- Minimal
- Cartoon (skin original, sem personagens oficiais)

### Preferências
- localStorage ou equivalente;
- não sincronizar entre jogadores;
- sem conta.

### Acessibilidade
- contraste;
- reduced motion;
- foco;
- mobile.

## Não entra

- login;
- conta;
- banco;
- matchmaking;
- ranking;
- chat;
- espectadores;
- torneio;
- engine como adversário;
- análise pós-partida completa;
- opening explorer;
- cloud sync de preferências;
- marketplace de skins.

## Não pode regredir

- sala;
- código;
- WebSocket;
- turno;
- regras;
- sincronização;
- reconexão;
- xeque-mate;
- final de partida;
- modo normal;
- modo assistido.

## Definição de pronto

V1.1 está pronta quando:

1. uma partida V1 ainda pode ser concluída do começo ao fim;
2. dicas 1–4 não entregam automaticamente o lance;
3. revelar lance exige ação separada e confirmação;
4. Stockfish melhora análise quando disponível;
5. heurística continua funcional sem Stockfish;
6. temas funcionam;
7. skins funcionam;
8. preferências persistem localmente;
9. UI continua boa em desktop e celular;
10. suíte de regressão passa.
