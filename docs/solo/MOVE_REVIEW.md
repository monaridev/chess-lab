# ChessLab Solo — Análise e classificação de jogadas

## Objetivo
Criar feedback pós-lance específico e pedagógico sem usar LLM.

A análise deve combinar:
- avaliação do Stockfish;
- comparação entre o melhor lance e o lance jogado;
- estado do tabuleiro antes e depois;
- evidências semânticas detectadas pelo ChessLab;
- lógica existente em `backend/hints.py` sempre que possível.

## Pipeline

```text
posição antes
  -> análise Stockfish
  -> melhor avaliação / melhores candidatos
  -> aplicar lance do jogador
  -> nova análise
  -> calcular perda de avaliação
  -> detectar efeitos concretos do lance
  -> classificar
  -> gerar comentário curto
  -> selecionar pose do Pogona
```

## Evidências que o sistema deve tentar detectar
- mudança de material;
- peça deixada sem defesa;
- peça salva de um ataque;
- captura boa ou ruim;
- captura perdida;
- xeque criado;
- xeque ignorado;
- mate encontrado;
- mate perdido;
- ameaça de mate criada ou permitida;
- desenvolvimento de cavalo ou bispo;
- controle do centro;
- preparação ou execução de roque;
- segurança do rei;
- garfo;
- cravada;
- ataque duplo;
- descoberta;
- peça sobrecarregada;
- promoção;
- peão passado;
- torre em coluna aberta/semiaberta;
- atividade de peça;
- coordenação;
- troca favorável/desfavorável;
- oportunidade única ou quase única.

## Comentários dinâmicos sem LLM
O texto não deve ser apenas uma lista fixa por categoria de nota.

O sistema deve montar a mensagem a partir das evidências.

Exemplo de estrutura:

```text
[classificação] + [efeito principal] + [efeito secundário opcional]
```

Exemplos:
- "Excelente. Você tirou o cavalo do ataque e ainda ganhou espaço no centro."
- "Boa. O bispo ficou mais ativo e seu rei continua seguro."
- "Imprecisa. O lance funciona, mas você deixou uma captura forte passar."
- "Erro. Sua torre ficou sem defesa depois desse movimento."
- "Grave. Esse lance abriu uma linha direta contra seu rei."

## Prioridade da explicação
Quando várias evidências forem detectadas, priorizar:
1. mate / ameaça ao rei;
2. grande perda ou ganho material;
3. tática imediata;
4. peça pendurada;
5. segurança do rei;
6. desenvolvimento / centro;
7. atividade e coordenação;
8. outros detalhes posicionais.

A fala deve ser curta. Idealmente 1 frase; no máximo 2 frases curtas.

## Classificação por perda de avaliação
Os valores exatos devem ser calibrados durante testes e não precisam reproduzir nenhuma plataforma externa.

Sugestão inicial aproximada, considerando centipawns e contexto:
- Excelente: perda mínima ou nula;
- Muito boa: perda muito pequena;
- Boa: pequena concessão sem dano real;
- Interessante: ideia válida, mas com custo concreto;
- Imprecisa: perda perceptível de qualidade;
- Erro: perda relevante de avaliação/material;
- Grave: grande alteração da posição ou do resultado esperado.

A classificação deve considerar contexto, não apenas delta bruto.

Exemplos:
- em posição já perdida, um delta grande pode não justificar `Grave`;
- lance forçado deve ser reconhecido;
- mate perdido deve receber forte penalização;
- sacrifício correto não pode ser classificado como erro apenas por perda material imediata.

## Categoria Genial
`Genial` deve ser rara.

Sugestão de critérios combinados:
- lance único ou quase único;
- mantém ou melhora significativamente a posição;
- difícil de encontrar;
- pode envolver sacrifício aparente ou recurso tático não óbvio;
- alternativas naturais são claramente piores.

Não tentar copiar uma definição externa.

## Precisão da partida
A precisão deve ser uma métrica interna do ChessLab.

Ela pode ser derivada da perda média ponderada de avaliação por lance, com proteção contra distorções em posições já ganhas/perdidas.

Objetivo da métrica:
- 100% representa uma partida extremamente próxima das melhores escolhas;
- erros graves devem reduzir bastante a precisão;
- pequenas imprecisões devem ter impacto moderado;
- não precisa coincidir com valores de outros sites.

## Tempo de análise
A análise pós-lance deve ser curta o suficiente para manter fluidez.

Priorizar:
- limite de tempo baixo por análise;
- cache quando possível;
- análise mais profunda no pós-partida, se necessário.
