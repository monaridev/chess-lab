# ChessLab Solo — Plano de testes

## Objetivo
Validar que o modo Solo funciona corretamente, permanece offline e não causa regressões.

## Testes de engine
- Stockfish inicia quando disponível;
- posição é enviada corretamente;
- lance retornado é legal;
- dificuldade altera comportamento;
- engine é encerrada corretamente;
- ausência do binário é tratada sem crash.

## Testes de classificação
Criar posições controladas para validar:
- melhor lance -> Excelente/Muito boa;
- pequena perda -> Boa/Interessante;
- imprecisão real -> Imprecisa;
- perda clara de peça -> Erro;
- blunder grande -> Grave;
- mate encontrado;
- mate perdido;
- lance forçado;
- sacrifício correto não marcado como erro automaticamente.

## Testes de conceitos
Posições específicas para:
- desenvolvimento;
- centro;
- roque;
- peça pendurada;
- peça salva;
- garfo;
- cravada;
- captura favorável/desfavorável;
- segurança do rei;
- promoção;
- mate.

## Testes dos comentários
- comentário corresponde às evidências;
- não menciona peça/casa inexistente;
- frase permanece curta;
- prioridade correta quando há múltiplas evidências;
- erro grave de rei/material supera observação posicional menor;
- não depende de rede ou API.

## Testes de precisão
- partida sem erros graves -> precisão alta;
- partida com vários erros -> precisão menor;
- um erro grave tem impacto relevante;
- posições já completamente perdidas não distorcem excessivamente a métrica;
- valor sempre limitado a intervalo válido.

## Testes de UI
- entrada do modo Solo aparece corretamente;
- seleção de dificuldade funciona;
- tabuleiro inicia;
- Pogona fica visível;
- pose muda após análise;
- balão mostra comentário;
- classificação aparece próxima ao contexto da jogada;
- fluxo continua após feedback;
- resumo final aparece;
- mobile não cobre tabuleiro.

## Testes de persistência
- `localStorage` salva estatísticas opcionais;
- ausência/limpeza de storage não quebra nada;
- dados antigos inválidos usam fallback seguro.

## Regressões obrigatórias
Executar toda a suíte existente e confirmar:
- multiplayer continua funcionando;
- modo Normal continua funcionando;
- modo Assistido continua funcionando;
- modo Aprender continua funcionando;
- dicas existentes permanecem corretas;
- deploy continua inicializando.

## Teste manual mínimo
1. jogar uma partida em Iniciante;
2. cometer propositalmente um erro de peça pendurada;
3. verificar classificação e comentário;
4. fazer um bom desenvolvimento;
5. verificar elogio contextual;
6. concluir a partida;
7. conferir precisão e resumo;
8. desligar internet e repetir o fluxo local.

## Execução implementada

Consulte `IMPLEMENTATION.md` para os comandos e a cobertura automatizada.
Os testes de navegador bloqueiam requisições externas preservando o servidor
local; não desligam as interfaces de rede do computador. O smoke Solo também
bloqueia conexões Python externas, sem alterar configurações globais.
