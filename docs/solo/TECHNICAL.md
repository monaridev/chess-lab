# ChessLab Solo — Arquitetura técnica

## Princípios
- offline sempre que o cliente/servidor local possuir Stockfish;
- sem LLM;
- sem API externa;
- sem banco de dados;
- sem Elo público;
- compatível com a arquitetura atual;
- sem regressão nos modos existentes.

## Componentes

### Stockfish
Responsável por:
- escolher lances do adversário;
- analisar o melhor lance da posição;
- avaliar a jogada do usuário;
- fornecer candidatos para comparação.

### python-chess
Responsável por:
- regras;
- estado do tabuleiro;
- FEN/SAN/UCI;
- legalidade;
- detecção de cheque/mate;
- suporte à engine UCI.

### Camada pedagógica ChessLab
Responsável por:
- interpretar o que a jogada fez;
- detectar conceitos;
- classificar o lance;
- gerar comentário textual curto;
- selecionar estado/pose do Pogona.

## Reuso da base atual
Priorizar reuso de:
- `backend/analysis.py`;
- `backend/hints.py`;
- estruturas de `python-chess` já existentes;
- assets do Pogona;
- componentes visuais do modo Aprender.

Evitar duplicar detectores de conceito quando a lógica já existir.

## Estrutura sugerida
A implementação pode adaptar os nomes à arquitetura atual, mas uma separação possível é:

```text
backend/
  solo.py
  move_review.py
  analysis.py
  hints.py

frontend/
  solo.js
  solo.css
```

## Estado de uma partida Solo
Deve incluir pelo menos:
- board/FEN;
- lado do jogador;
- dificuldade;
- histórico de lances;
- avaliações por lance;
- classificações por lance;
- precisão parcial;
- resultado final.

## Dificuldade do Stockfish
Sem mostrar Elo ao usuário.

O frontend apresenta apenas:
- Iniciante
- Fácil
- Médio
- Difícil

Internamente, usar parâmetros como:
- `Skill Level`;
- tempo máximo por jogada;
- profundidade;
- escolha entre MultiPV candidatos;
- aleatoriedade controlada entre lances aceitáveis.

### Regra importante
Nos níveis baixos, não basta reduzir profundidade se isso ainda produzir comportamento muito forte. Preferir seleção entre vários lances razoáveis para criar um adversário mais humano e menos punitivo.

## Fluxo de uma jogada
1. usuário faz um lance legal;
2. backend registra posição anterior;
3. engine avalia posição/lance;
4. sistema detecta evidências;
5. gera `MoveReview`;
6. frontend exibe classificação + fala do Pogona;
7. Stockfish escolhe resposta;
8. resposta é aplicada;
9. turno volta ao usuário.

## Estrutura de resposta sugerida

```json
{
  "move": "Nf3",
  "classification": "excellent",
  "accuracy_delta": 0.04,
  "comment": "Você desenvolveu o cavalo e ganhou mais controle do centro.",
  "pogona_state": "praise",
  "concepts": ["development", "center"],
  "best_move": "Nf3",
  "is_forced": false
}
```

`best_move` pode existir internamente e não precisa ser mostrado automaticamente.

## Offline
A execução deve funcionar sem internet quando o ambiente local possuir:
- aplicação;
- python-chess;
- binário Stockfish.

Não fazer chamadas remotas para análise ou texto.

## Fallback
Se Stockfish não estiver disponível:
- não fingir que existe análise de engine;
- exibir mensagem clara;
- preservar outros modos;
- opcionalmente permitir apenas uma análise heurística limitada, marcada explicitamente como tal.

## Persistência local
Se houver estatísticas, usar `localStorage`.

Exemplo:

```json
{
  "gamesPlayed": 12,
  "bestAccuracy": 91,
  "recentAccuracy": [77, 81, 84, 88, 85],
  "lastDifficulty": "medium",
  "conceptStats": {
    "development": 0.82,
    "kingSafety": 0.66,
    "hangingPieces": 0.58
  }
}
```

Nada disso exige servidor ou banco.
