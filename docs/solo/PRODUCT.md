# ChessLab — Modo Solo Offline

## Visão
O Modo Solo Offline permite que uma pessoa jogue xadrez sozinha contra um adversário controlado por Stockfish, sem depender de outra pessoa, sem conta, sem API externa e sem internet para a lógica da partida.

O Professor Pogona continua sendo o guia pedagógico da experiência. O Stockfish é apenas o adversário.

## Objetivo do produto
Criar uma forma simples e acolhedora de praticar xadrez sozinho, mantendo a proposta principal do ChessLab: aprender jogando.

O modo deve ajudar o jogador a:
- praticar partidas completas;
- aplicar o que aprendeu no modo Aprender;
- desenvolver autonomia;
- reconhecer ameaças, peças indefesas e padrões básicos;
- ganhar confiança sem enfrentar um adversário excessivamente forte.

## Princípio central
O usuário joga contra o Stockfish, mas aprende com o Pogona.

Separação de responsabilidades:
- **Stockfish**: escolhe os lances do adversário;
- **Professor Pogona**: observa, explica, alerta, elogia e oferece pistas;
- **ChessLab**: mantém regras, tabuleiro, progresso e interface.

## Fluxo ideal
1. Abrir o ChessLab.
2. Entrar em `Jogar Solo`.
3. Escolher nível do adversário.
4. Escolher ajuda do Pogona.
5. Iniciar partida.
6. Jogar normalmente.
7. Receber orientação pedagógica quando necessário.
8. Finalizar a partida.
9. Ver um resumo curto de aprendizado.

## Níveis iniciais
### Nível 1 — Primeiro jogo
- adversário muito fraco;
- permite erros óbvios;
- Pogona oferece bastante orientação;
- indicado para quem ainda está aprendendo a enxergar ameaças.

### Nível 2 — Iniciante
- adversário joga lances razoáveis;
- ainda comete erros simples;
- Pogona intervém em erros importantes.

### Nível 3 — Intermediário leve
- adversário mais consistente;
- menos erros gratuitos;
- Pogona fala menos e prioriza raciocínio.

### Nível 4 — Desafio
- adversário forte o bastante para exigir atenção;
- ajuda pedagógica mínima por padrão;
- não deve necessariamente usar a força máxima do Stockfish.

## Modos de ajuda do Pogona
### Guiado
- pode alertar antes de um erro grave;
- oferece pistas progressivas;
- pode permitir nova tentativa em alguns exercícios ou partidas de treino.

### Assistido
- não impede jogadas;
- explica depois de erros relevantes;
- oferece dicas sob demanda.

### Livre
- partida praticamente normal;
- Pogona aparece visualmente, mas interfere pouco;
- resumo pedagógico ao final.

## Comportamento do Professor Pogona
O personagem deve permanecer visível durante toda a partida Solo.

Ele pode usar estados como:
- observando;
- pensando;
- alertando;
- ensinando;
- elogiando;
- comemorando.

O personagem não deve cobrir o tabuleiro nem interromper toda jogada.

## Perguntas que o Pogona deve reforçar
- Meu rei está seguro?
- Tem peça minha em perigo?
- O adversário ameaça o quê?
- Consigo capturar algo sem perder mais?
- Qual peça minha está menos ativa?

## Pós-partida
Ao terminar, mostrar um resumo simples, por exemplo:
- ameaças percebidas;
- peças deixadas sem defesa;
- boas decisões de desenvolvimento;
- segurança do rei;
- táticas encontradas;
- pontos a treinar.

O resumo não deve virar uma análise técnica pesada com centipawns e números difíceis.

## Fora do escopo inicial
- matchmaking;
- ranking/ELO;
- conta de usuário;
- banco de dados;
- IA generativa para escolher jogadas;
- personalidade conversacional via API externa;
- força máxima competitiva do Stockfish.
