# Produto — Chess Lab

## Visão
Chess Lab é uma experiência multiplayer para duas pessoas jogarem e aprenderem xadrez juntas.

O sistema deve ser um terceiro participante silencioso: garante regras, explica quando necessário e oferece ajuda quando alguém pede.

## Problema
Quando duas pessoas ainda estão aprendendo xadrez:
- alguém esquece movimentos;
- ninguém percebe uma ameaça;
- uma jogada parece possível mas é ilegal;
- um jogador não sabe por que perdeu uma peça;
- quem sabe um pouco mais nem sempre sabe ensinar.

Chess Lab reduz esse atrito sem transformar um jogador em professor do outro.

## Experiência
Fluxo ideal:
1. abrir o site;
2. clicar em `Criar sala`;
3. receber código curto;
4. enviar o código;
5. segunda pessoa entra;
6. partida começa;
7. ambos jogam;
8. qualquer um pode pedir dica.

Sem conta, cadastro ou configuração chata.

## Modos

### Partida Normal
Xadrez tradicional.
O sistema valida regras, mostra turno, movimentos legais, xeque e fim da partida.

### Partida Assistida
A partida continua competitiva, mas cada jogador pode pedir ajuda.

Progressão:
1. observação geral;
2. peça/região relevante;
3. explicação;
4. sugestão de jogada razoável.

O objetivo é ajudar a perceber padrões, não jogar pela pessoa.

## Visual
Tema:
- dark;
- laboratório/ciência;
- moderno;
- clean;
- elegante;
- não infantil;
- animações discretas.

## UX
- tabuleiro como elemento central;
- indicar claramente cor e turno;
- código da sala visível;
- dicas sob demanda;
- mensagens curtas e claras;
- sem ranking/ELO.

## Sucesso da V1
Duas pessoas em dispositivos diferentes conseguem:
- entrar na mesma sala;
- jogar uma partida completa;
- enxergar o mesmo estado;
- pedir dicas;
- terminar sem correções manuais.

## Evolução V1.1

A estrutura e o multiplayer da V1 permanecem. A progressão de dicas passa a
ser: Observe → Olhe mais perto → Entenda a ideia → Uma possibilidade, sem
entregar o lance exato. A revelação exige ação separada e modal de confirmação.
Stockfish é um analisador local opcional, sempre com fallback heurístico.
Temas e skins personalizam apenas o navegador de cada jogador.

O escopo atual é complementado por `V1_1_SCOPE.md` e `V1_1_DECISIONS.md`.

## Evolução V1.2

Refinamento visual e pedagógico, sem expansão do produto: Elmore School,
Watterson Cozy, Cartoon 2.0 e dicas com evidências mais específicas.
A referência visual atual é `references/ref-gumball.png`; detalhes em
`V1_2_SCOPE.md`. A estrutura e os fluxos da V1.1 permanecem.
