# Escopo da V1 — Chess Lab

## Regra
Se um recurso não ajuda diretamente duas pessoas a entrar, jogar, sincronizar, entender ou pedir ajuda, provavelmente não pertence à V1.

## Deve existir

### Página inicial
- Criar sala
- Entrar por código
- Partida Normal
- Partida Assistida

### Criação de sala
- código curto;
- criador = brancas;
- botão copiar;
- `aguardando segundo jogador`.

### Entrada
- segundo jogador = pretas;
- código inválido com mensagem amigável;
- sala cheia rejeitada.

### Tabuleiro
- renderizar posição;
- orientar pela cor;
- seleção;
- movimentos legais;
- último movimento;
- indicação de xeque;
- promoção;
- clique peça → clique destino.

Drag-and-drop é opcional.

### Turno
Mostrar `Sua vez` / `Vez do outro jogador`.

### Regras
Suportar:
- movimentos;
- capturas;
- promoção;
- roque;
- en passant;
- xeque;
- xeque-mate;
- afogamento;
- empates;
- material insuficiente.

### Multiplayer
WebSocket.
Após mudança válida, ambos recebem o mesmo estado.

### Partida Assistida
Botão `Pedir dica`.

Níveis:
1. observação;
2. região/peça;
3. explicação;
4. sugestão de jogada.

### Mensagens educativas
Exemplos:
- Não é sua vez.
- Essa peça pertence ao outro jogador.
- Seu rei continuaria em xeque.

### Conexão
Mostrar:
- conectado;
- esperando adversário;
- adversário desconectado;
- reconectando.

### Reconexão
Refresh/queda breve não deve destruir imediatamente a partida.

### Interface
- dark;
- responsiva;
- clean;
- laboratório;
- tabuleiro central.

## Deve ser testado
- servidor;
- frontend;
- criar sala;
- entrar;
- código inválido;
- sala cheia;
- jogada válida;
- inválida;
- fora do turno;
- peça adversária;
- roque;
- promoção;
- en passant;
- xeque;
- mate;
- empate;
- sincronização;
- desconexão;
- reconexão;
- dica;
- partida completa.

## Não fazer agora
- cadastro/login;
- banco;
- perfil/avatar;
- ranking/ELO;
- histórico;
- matchmaking;
- amigos;
- chat;
- espectadores;
- torneios;
- IA adversária;
- API paga;
- app nativo;
- React/Vue/Angular;
- microserviços;
- Kubernetes.

## Nice-to-have
Só se não atrapalhar:
- animação;
- som discreto;
- peças capturadas;
- material;
- rematch;
- coordenadas;
- pequenas explicações.

## Definição de pronto
Duas pessoas em dispositivos diferentes conseguem:
1. abrir;
2. entrar na mesma sala;
3. jogar partida inteira;
4. ver mesmo tabuleiro;
5. usar dicas;
6. terminar corretamente;
7. sobreviver a reconexão simples.
