# ChessLab Solo — Decisões de produto e arquitetura

## D1 — Stockfish é o adversário
Decisão: usar Stockfish local como engine do modo Solo.

Motivo: é especializado em xadrez, funciona offline, é previsível e não possui custo por requisição.

## D2 — Não usar LLM
Decisão: nenhuma LLM será necessária para escolher jogadas ou escrever comentários.

Os comentários são montados dinamicamente a partir de evidências do tabuleiro e análise da engine.

## D3 — Sem API paga
Decisão: o modo Solo não dependerá de serviços pagos externos.

## D4 — Sem banco de dados
Decisão: não adicionar banco de dados para o modo Solo.

Dados opcionais de progresso ficam em `localStorage`.

## D5 — Sem Elo/rating público
Decisão: não implementar sistema de Elo.

O usuário escolhe dificuldade diretamente: Iniciante, Fácil, Médio ou Difícil.

Motivo: reduz complexidade, elimina necessidade de identidade persistente e evita transformar a experiência em ranking.

## D6 — Precisão não é Elo
A precisão representa a qualidade dos lances dentro de uma partida.

Ela não representa ranking e não precisa ser persistida além de estatísticas locais opcionais.

## D7 — Classificações próprias do ChessLab
Não copiar nomes exatos, fórmulas, identidade visual ou thresholds de plataformas externas.

O ChessLab terá critérios próprios calibrados com Stockfish e testes.

## D8 — Comentário baseado no lance real
O Pogona não escolherá simplesmente uma frase aleatória de um conjunto associado a `Boa`, `Erro`, etc.

O comentário precisa usar evidências detectadas naquela posição.

## D9 — Pogona sempre presente
No modo Solo, o Pogona permanece visível durante toda a partida.

Ele deve reagir sem cobrir o tabuleiro ou interromper excessivamente o ritmo.

## D10 — Melhor lance não é mostrado automaticamente
A análise pode calcular o melhor lance, mas o sistema não deve entregá-lo por padrão após todo erro.

O foco é explicar o problema da jogada. Mostrar solução deve exigir ação explícita quando fizer sentido.

## D11 — Modos existentes permanecem isolados
Normal, Assistido e Aprender não devem mudar de comportamento por causa do modo Solo.
