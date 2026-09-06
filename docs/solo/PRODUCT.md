# ChessLab — Modo Solo Offline

## Visão
O modo Solo permite jogar xadrez sem depender de outra pessoa e sem depender de internet, APIs pagas, LLMs ou banco de dados.

O adversário é controlado por Stockfish local. O Professor Pogona continua sendo o professor da experiência e acompanha a partida inteira, analisando cada jogada do jogador e oferecendo um comentário curto e específico sobre o que aconteceu de fato no tabuleiro.

## Objetivos do produto
- permitir partidas completas offline;
- oferecer níveis de dificuldade previsíveis;
- ajudar o jogador a aprender com cada lance;
- transformar análise de engine em explicações curtas e compreensíveis;
- manter a experiência simples, sem conta, ranking ou cadastro;
- preservar os modos Normal, Assistido e Aprender já existentes.

## Fluxo principal
1. usuário abre o ChessLab;
2. escolhe `Modo Solo`;
3. escolhe a dificuldade do adversário;
4. inicia a partida;
5. após cada jogada do usuário, o sistema analisa o lance;
6. aparece uma classificação curta da jogada;
7. o Professor Pogona muda de pose e comenta a jogada em um balão de fala;
8. Stockfish responde;
9. a partida continua;
10. ao final, o sistema mostra precisão e resumo da partida.

## Dificuldades sugeridas
- Iniciante
- Fácil
- Médio
- Difícil

Os níveis não usam Elo público. A força deve ser configurada internamente com parâmetros do Stockfish e/ou seleção controlada entre lances candidatos.

## Classificação dos lances
A classificação deve pertencer ao ChessLab e não copiar nomenclatura ou identidade visual de terceiros.

Sugestão:
- Genial
- Excelente
- Muito boa
- Boa
- Interessante
- Imprecisa
- Erro
- Grave

Também podem existir marcadores contextuais separados da nota:
- Forçada
- Única
- Desenvolvimento
- Roque
- Tática
- Mate encontrado

## Professor Pogona
O Pogona fica visível 100% do tempo no modo Solo.

Ele não deve apenas mostrar frases predefinidas com base na nota. O comentário deve ser gerado a partir das evidências reais encontradas na posição.

Exemplos:
- `Excelente` + desenvolvimento + centro -> "Você desenvolveu o cavalo e ganhou mais controle do centro."
- `Erro` + peça pendurada -> "Esse lance deixou sua torre sem defesa e ela pode ser capturada."
- `Imprecisa` + oportunidade perdida -> "Seu lance é seguro, mas havia uma chance de pressionar a dama."
- `Boa` + segurança do rei -> "Boa. Você deixou seu rei mais seguro sem enfraquecer suas peças."

## Experiência visual
Após a jogada:
1. a casa do último lance permanece marcada;
2. aparece uma pequena classificação da jogada;
3. o Pogona troca para a pose adequada;
4. o balão mostra uma frase curta;
5. a análise não deve bloquear o fluxo da partida por tempo excessivo.

## Poses do Pogona por contexto
- Excelente / Muito boa -> elogiando
- Boa -> feliz
- Interessante / Imprecisa -> pensando
- Erro / Grave -> alerta
- analisando posição -> observando
- explicação de conceito -> ensinando
- vitória / conclusão -> comemorando

## Pós-partida
Mostrar um resumo simples:

- resultado;
- precisão estimada da partida;
- quantidade de lances por classificação;
- principais acertos;
- principais pontos a melhorar;
- conceitos mais recorrentes na partida.

Exemplo:

```text
Precisão: 84%

Excelente: 4
Muito boas: 7
Boas: 9
Imprecisas: 3
Erros: 1
Graves: 0

Ponto forte: desenvolvimento
A melhorar: peças sem defesa
```

## Persistência
Sem banco de dados.

Pode usar `localStorage` apenas para dados locais opcionais, como:
- número de partidas solo;
- melhor precisão;
- média recente;
- dificuldade usada por último;
- estatísticas simples por conceito.

Nenhuma conta é necessária.
