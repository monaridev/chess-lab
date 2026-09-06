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

## D12 — Sessões Solo isoladas e retomada na mesma aba
Implementação: `SoloManager` mantém até 100 partidas por processo, com expiração
após 24 horas sem atividade. O servidor valida intenções e versões (`ply`); não
aceita FEN do cliente. Token temporário fica em `sessionStorage`, separado das
salas multiplayer. `localStorage` guarda apenas preferências e estatísticas leves.
Reiniciar o servidor encerra as partidas, como nas salas existentes.

## D13 — Duas etapas por turno e falhas explícitas
A intenção do usuário só é aplicada depois das duas avaliações Stockfish. A
resposta inclui o tabuleiro pós-lance e o comentário. O navegador os renderiza
antes de solicitar a resposta do adversário. Se a resposta se perder, retomar
consulta o estado oficial antes de continuar; `ply` rejeita duplicatas.
Falha de análise não recebe nota inventada nem adversário heurístico.

O Solo usa uma instância limitada de `AnalysisService`, reaproveitando descoberta
do binário, inicialização UCI e encerramento. A engine das dicas multiplayer
permanece independente para que partidas Solo não ocupem sua fila.

## D14 — Ajuda opcional, revisão obrigatória
O pacote original exige modos de ajuda, mas não enumera opções. Adotadas:
- **Só revisão após o lance**: comentário e classificação após cada lance;
- **Dicas progressivas + revisão**: quatro pistas existentes, seguidas de
  revelação mediante confirmação explícita. Nunca executar a sugestão.

## D15 — Força do adversário separada da revisão
Iniciante/Fácil/Médio/Difícil usam Skill Level 0/4/10/20, limites de
80/120/200/350 ms, profundidades 6/9/12/16 e MultiPV 8/5/3/1. A escolha
ponderada entre candidatos permite concessões máximas de 280/150/60/0 pontos
internos. Iniciante prefere alternativas inferiores dentro desse limite;
Difícil escolhe o primeiro candidato. Não há rating, adaptação escondida ou Elo.
Esses níveis são relativos; Stockfish ainda pode ser forte para iniciantes.

A revisão sempre usa Skill Level 20, até 250 ms/profundidade 14, MultiPV 3.
Cache limitado considera FEN, histórico de repetição e cor avaliada. Fila máxima
0,5 s e timeout de operação de 2 s; falha persistente requer reinício.

## D16 — Classificação e precisão próprias, explicações conservadoras
Perda ajustada: diferença não negativa entre melhor avaliação antes e avaliação
depois, ambas na perspectiva do usuário. Concessões em posições que continuam
decisivamente ganhas/perdidas (mesmo sinal, ambas além de 600) são comprimidas;
perda final limitada a 1200. Limites internos iniciais: 12 Excelente, 30 Muito
boa, 60 Boa, 100 Interessante **se houver ideia tática**, 140 Imprecisa,
320 Erro, acima Grave. Sem tática, 61–140 é Imprecisa.

Mate encontrado e lance forçado são reconhecidos. Perder uma sequência de mate
ou permitir mate antes inexistente impõe Grave e perda mínima de 500. Genial
exige perda até 12, ideia tática, peça de valor pelo menos 3 oferecida e vantagem
de pelo menos 160 sobre o segundo candidato. Esses critérios são conservadores
e aproximados, sujeitos à profundidade limitada; não são uma definição de
criatividade humana.

Precisão é a média de `100 * exp(-perda_ajustada / 180)` dos lances do usuário,
arredondada a uma casa, sem lances do adversário. Sem lances, é indisponível.
Não considera o uso de dicas como penalidade; não mede habilidade ou rating.

Comentários são determinísticos e descrevem evidências reais. Captura possível
não significa ganho forçado; a linguagem preserva essa diferença. Sacrifícios
não recebem erro só por oferecer material: a avaliação determina a perda.

## D17 — Revisão visual do Solo sem mudar as regras
A preparação usa opções segmentadas de dificuldade/cor/ajuda e prévias de temas
e skins. A aparência utiliza os controles, tokens, assets e chave
`chesslab.appearance.v1` já existentes; não há preferência visual paralela.

Desktop prioriza três colunas: Pogona e nota, tabuleiro, ajuda e ações. A partida
ocupa uma altura fixa na viewport. O tabuleiro se dimensiona pela célula central,
preservando as oito fileiras. Histórico abre somente por solicitação em um modal
com rolagem interna. O resultado abre automaticamente em outro modal, com chips
de classificação e acesso à análise completa. Esses painéis não alongam a página.

No mobile, Pogona ocupa uma faixa própria acima do tabuleiro. Ajuda e ações
adicionais são recolhidas; a preparação pode rolar dentro de sua área, com o
botão de iniciar acessível. Os modais ficam abaixo do professor, com altura
limitada. Dialogs nativos fornecem Escape e contenção do foco.

As referências em `chesslab_solo_ui_refs/` orientam hierarquia e composição,
sem incorporar navegação, Elo ou funcionalidades ilustradas fora do escopo.
Stockfish, classificação, comentários, precisão, regras e persistência Solo
permanecem inalterados nesta revisão visual.
