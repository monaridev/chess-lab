# ChessLab — Modo Solo Offline — Testes e Critérios de Aceite

## Objetivo
Garantir que o novo modo Solo funcione sem quebrar os modos existentes.

## Testes de backend
### Criação de partida Solo
- cria tabuleiro em posição inicial válida;
- define lado do usuário corretamente;
- aplica nível selecionado;
- rejeita parâmetros inválidos.

### Jogadas do usuário
- aceita lance legal;
- rejeita lance ilegal;
- não permite jogar fora do turno;
- detecta xeque, mate, empate e promoção corretamente.

### Jogadas do Stockfish
- retorna somente lances legais;
- joga apenas no turno correto;
- respeita fim da partida;
- trata engine indisponível sem crashar servidor.

### Dificuldade
- níveis devem produzir configuração diferente da engine;
- nível mais baixo não deve usar a mesma configuração máxima do nível mais alto.

## Testes de integração
Fluxo mínimo:
1. iniciar partida Solo;
2. usuário realiza lance;
3. engine responde;
4. estado recebido pelo cliente corresponde ao backend;
5. próximo turno volta ao usuário.

Testar também:
- roque;
- promoção;
- en passant;
- xeque-mate;
- empate quando aplicável.

## Testes pedagógicos
- Pogona permanece visível;
- estado muda conforme evento relevante;
- alerta não bloqueia partida no modo Assistido;
- modo Guiado pode oferecer intervenção antes de erro conforme design;
- modo Livre não exibe mensagens excessivas;
- dicas continuam progressivas.

## Testes de frontend
- botão `Jogar Solo` acessível;
- seleção de nível funciona;
- seleção de ajuda funciona;
- tabuleiro bloqueia durante jogada da engine;
- loading/estado de pensamento é visível;
- Pogona não cobre tabuleiro;
- balões não saem da viewport;
- interface funciona em desktop e mobile.

## Persistência local
- nível preferido pode ser salvo;
- modo de ajuda pode ser salvo;
- progresso simples sobrevive a reload;
- dados corrompidos em `localStorage` não quebram a tela.

## Regressão obrigatória
Rodar toda a suíte existente e confirmar:
- Normal funcionando;
- Assistido funcionando;
- Aprender funcionando;
- multiplayer funcionando;
- reconexão funcionando;
- hints existentes funcionando.

## Teste manual recomendado
### Desktop
- Chrome/Chromium;
- Firefox se possível.

### Mobile
- largura pequena via DevTools;
- aparelho físico quando possível.

Verificar:
- tamanho do tabuleiro;
- balões do Pogona;
- botões;
- rolagem;
- legibilidade.

## Critérios de aceite da V1 Solo
A implementação pode ser considerada pronta quando:
- usuário consegue iniciar partida sem outra pessoa;
- Stockfish responde com lances válidos;
- existem pelo menos 3 níveis de força claramente distintos;
- Pogona funciona nos três modos de ajuda;
- partida chega ao fim corretamente;
- resumo pós-partida aparece;
- nenhum modo existente sofre regressão;
- testes novos e antigos passam.
