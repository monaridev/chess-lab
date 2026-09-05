# Chess Lab — V1.2

## Direção e escopo

A referência visual principal é `references/ref-gumball.png`, analisada antes
das alterações. Ela substitui orientações visuais anteriores quando houver
conflito. Arquitetura, regras e comportamento continuam descritos nos documentos
atuais; a V1.1 funcional é a base preservada.

Esta rodada inclui somente Elmore School, Watterson Cozy, Cartoon 2.0,
textos de dicas mais específicos e acabamento visual. Não inclui novos modos,
contas, persistência, chat, espectadores, ranking nem adversário de IA.

## Aparência

- Elmore School (`elmore`): armários vermelhos, tabuleiro azul/cream, fitas
  amarelas, caderno e doodles. Mantém preferências salvas da V1.1.
- Watterson Cozy (`watterson`): navy, bege, madeira, plaid, vermelho suave,
  rosa e laranja; sala original com luminária e tapete.
- Cartoon 2.0 (`cartoon`): seis silhuetas originais nas duas cores, contornos
  expressivos, bases suaves e detalhes convencionais para reconhecer as peças.
- Laboratory, Matcha, Strawberry Milk, Midnight e Lavender permanecem.
- Classic, Soft, Cute e Minimal permanecem.

Os cenários são assets locais em `frontend/scenes/`, independentes da referência.
Não há screenshots, logos ou personagens oficiais no produto. Os SVGs ficam
atrás dos painéis; o tabuleiro mantém botões reais e a orientação por jogador.
No celular, sala, tabuleiro e dicas continuam empilhados. Movimento reduzido,
foco e feedback de cópia são preservados.

## Dicas

Observe → Olhe mais perto → Entenda a ideia → Uma possibilidade.
A progressão não mostra notação nem destino exato. Textos usam evidências do
número de peças por desenvolver, influência central, defensores e novos alvos.
A revelação continua privada e exige confirmação em modal com as ações
Continuar pensando e Mostrar jogada mesmo assim.

Depois da confirmação, mostrar SAN, origem (1/amarelo), destino (2/verde),
legenda e explicação específica. Não executar o lance. Stockfish local opcional,
heurísticas, cache, limites, validação de posição e restauração por reconexão
permanecem com a arquitetura da V1.1.

## Validação

Ver `TESTING.md`. Exigir suíte completa com Stockfish e fallback, dois clientes
reais HTTP/WebSocket, reconexão, regras, privacidade das dicas, combinações de
temas/skins, mobile e inspeção de screenshots comparada à referência principal.
