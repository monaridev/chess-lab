# ChessLab — Modo Solo Offline — Arquitetura Técnica

## Objetivo técnico
Adicionar um modo de partida individual usando Stockfish como adversário, reaproveitando ao máximo a arquitetura atual do ChessLab e mantendo os modos Normal, Assistido e Aprender intactos.

## Decisão principal
Não usar IA generativa para a lógica do adversário.

O Stockfish é suficiente para:
- analisar posições;
- escolher lances;
- ajustar força;
- funcionar localmente;
- produzir comportamento previsível e testável.

## Componentes esperados
### Backend
Responsável por:
- validar posição e lances com `python-chess`;
- coordenar a partida Solo;
- solicitar um lance ao Stockfish;
- aplicar limites de força;
- expor endpoints ou eventos necessários ao frontend;
- reaproveitar `backend/analysis.py` e `backend/hints.py` sempre que fizer sentido.

### Frontend
Responsável por:
- iniciar partida Solo;
- selecionar nível;
- selecionar modo de ajuda;
- renderizar o tabuleiro;
- bloquear interação durante a jogada do adversário;
- mostrar estado do Pogona;
- mostrar balões de fala e dicas;
- exibir resumo pós-partida.

## Integração com Stockfish
O projeto já possui integração opcional com Stockfish para análise. O modo Solo deve reaproveitar essa base em vez de criar uma segunda integração independente.

A engine deve receber a posição atual e devolver um lance legal.

## Controle de força
O objetivo não é usar sempre o melhor lance possível.

Possíveis controles, conforme suporte da integração escolhida:
- `Skill Level`;
- tempo máximo por lance;
- profundidade limitada;
- nós limitados;
- escolha probabilística entre alguns lances candidatos.

## Estratégia recomendada por nível
### Nível 1
- força muito baixa;
- tempo de cálculo curto;
- aceitar escolhas entre vários lances razoáveis;
- evitar comportamento perfeito.

### Nível 2
- força baixa;
- ainda permitir imprecisões.

### Nível 3
- força moderada;
- menos aleatoriedade.

### Nível 4
- força maior, mas ainda limitada.

## Requisito importante
Não implementar dificuldade apenas como "Stockfish forte + atraso artificial".

A diferença precisa estar na qualidade dos lances, não somente no tempo de resposta.

## Fluxo de jogada
1. Usuário realiza uma jogada.
2. Backend valida a jogada.
3. Estado da partida é atualizado.
4. Sistema verifica fim da partida.
5. Se continuar, o Stockfish recebe a posição.
6. Stockfish escolhe uma jogada conforme o nível.
7. Backend valida/aplica o lance da engine.
8. Novo estado é enviado ao frontend.
9. Pogona pode gerar feedback pedagógico.

## Estado da partida
O modo Solo não precisa inicialmente de persistência no servidor.

Pode usar:
- estado em memória durante a sessão;
- `localStorage` para preferências e progresso leve no cliente.

## Offline
O modo Solo deve funcionar sem chamadas para APIs externas.

Observação: se o ChessLab continuar hospedado como site web, "offline" significa que a lógica de adversário não depende de uma API externa. Para funcionamento totalmente sem rede após carregar a aplicação, seria necessário um passo adicional como PWA/cache ou empacotamento local. Isso pode ficar fora da primeira implementação.

## Stockfish indisponível
O comportamento deve ser explícito.

Opções aceitáveis:
1. impedir início da partida Solo e mostrar mensagem clara;
2. usar fallback simples apenas se já houver uma solução segura e testada no projeto.

Não fingir que a engine está disponível.

## Pogona e pedagogia
A engine não deve gerar textos para o usuário.

O feedback deve vir da camada pedagógica existente, preferencialmente reaproveitando `hints.py` e análise de posição.

## Estrutura sugerida
Exemplo, não obrigatório:

```text
backend/
  solo.py
  analysis.py
  hints.py
  game.py

frontend/
  solo.js
  solo.css
  assets/pogona/
```

A implementação final deve respeitar a arquitetura já existente e evitar duplicação de lógica.

## Segurança contra regressões
- Normal continua funcionando;
- Assistido continua funcionando;
- Aprender continua funcionando;
- multiplayer continua funcionando;
- salas não devem depender do modo Solo;
- lógica Solo deve ficar isolada sempre que possível.
