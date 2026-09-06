# ChessLab — Modo Solo Offline — Decisões

## D1 — Stockfish será o adversário
**Decisão:** usar Stockfish para escolher os lances do oponente.

**Motivo:** é especializado em xadrez, rápido, previsível, testável e pode funcionar localmente.

## D2 — Não usar IA generativa para jogar
**Decisão:** nenhuma LLM será responsável por escolher os lances.

**Motivo:** adicionaria dependência de internet/API, custo, imprevisibilidade e complexidade sem necessidade.

## D3 — Pogona continua sendo o professor
**Decisão:** Stockfish não fala diretamente com o usuário.

**Motivo:** manter personalidade e pedagogia centralizadas no Professor Pogona.

## D4 — O adversário não deve jogar sempre perfeito
**Decisão:** limitar a força da engine por nível.

**Motivo:** um iniciante precisa de uma experiência desafiadora, não frustrante.

## D5 — Sem login e sem banco no escopo inicial
**Decisão:** preferências e progresso leve ficam no navegador.

**Motivo:** manter o ChessLab simples e coerente com o produto atual.

## D6 — A ajuda do Pogona é configurável
**Decisão:** oferecer modos Guiado, Assistido e Livre.

**Motivo:** permitir evolução gradual sem criar três sistemas diferentes de jogo.

## D7 — Não expor avaliação técnica pesada
**Decisão:** evitar centipawns, profundidade de engine e números técnicos na interface padrão.

**Motivo:** o objetivo é ensinar xadrez, não ensinar a ler uma engine.

## D8 — Priorizar reaproveitamento da arquitetura atual
**Decisão:** reutilizar `python-chess`, integração Stockfish, análise e hints existentes.

**Motivo:** reduzir bugs, duplicação e tempo de implementação.

## D9 — Primeira versão não precisa ser PWA
**Decisão:** o primeiro objetivo é não depender de API externa para a partida Solo.

**Motivo:** suporte totalmente offline após fechar/reabrir o navegador exigiria cache/PWA ou empacotamento e pode ser tratado depois.
