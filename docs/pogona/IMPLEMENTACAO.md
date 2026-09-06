# Aprender com o Pogona

Primeira versão: seis capítulos, 19 exercícios interativos. Entrada no início,
independente de criar sala. O modo usa as preferências visuais já salvas.
Normal e Assistido mantêm seus contratos, regras, sessões e dicas.

## Conteúdo

| Capítulo | Exercícios |
| --- | --- |
| Movimentos das peças | Peão, torre, bispo, cavalo, dama e rei |
| Xeque e xeque-mate | Capturar o atacante; encontrar mate em um |
| Valor das peças e peças indefesas | Ganhar material; salvar uma torre atacada |
| Abertura saudável | Centro, desenvolvimento e roque pequeno |
| Garfos e ameaças simples | Garfo de cavalo; desenvolver com ameaça à dama |
| Partida guiada | Partida completa de quatro lances das brancas, com respostas predefinidas, até o mate do pastor |

A partida guiada demonstra uma defesa imprecisa, não uma recomendação para
sair cedo com a dama. A explicação ressalta que o adversário pode defender e
que desenvolver e rocar são hábitos preferíveis. Não há adversário de IA.
O usuário precisa realizar cada lance; nenhuma dica joga por ele.

## Código e autoridade

- `backend/learning.py`: catálogo imutável (`Chapter` / `Exercise`), objetivos,
  posições, respostas aceitas, feedback e API síncrona (thread pool do FastAPI).
- `GET /api/learn`: apenas títulos, IDs e quantidades; não revela soluções.
- `POST /api/learn/{id}`: recebe `moves` (intenções já concluídas), `action`
  (`state`, `move`, `hint`, `reveal`), `move` UCI opcional e `level` 0–4.
- Todas as intenções são reproduzidas e validadas com `game.play` e
  `python-chess` a partir dos FENs do catálogo. FENs enviados pelo cliente são
  rejeitados, assim como campos extras e históricos incompatíveis.
- Lance legal fora do objetivo devolve `accepted: false` com HTTP 200: é
  feedback pedagógico normal, sem alterar o progresso. Intenção ilegal ou
  dados inválidos são erros HTTP. Nenhuma operação toca salas multiplayer.
- Sem sessões adicionais no servidor: o histórico tem no máximo 32 intenções.
  O cliente pode retomar após reinício do servidor. Progresso é pessoal, não
  credencial de certificação: `localStorage` não é uma fronteira de segurança.
- Cada exercício parte da posição preparada pelo servidor. Na partida guiada,
  as posições são consecutivas, incluindo a resposta fixa das pretas.
- Após um acerto, a interface mostra a posição resultante e o comentário antes
  de permitir avançar para a próxima posição.

## Ensino e presença

As quatro pistas usam observação e região de `hints.build_plan`, conceito
específico do exercício e objetivo do mesmo plano. O lance-alvo é informado
apenas internamente ao gerador, para que a heurística não desvie da lição.
A revelação exige quatro pistas e uma confirmação separada na interface.
Stockfish e APIs externas não são usados neste modo.

O checklist mantém as cinco perguntas do conceito original. Idle acompanha o
catálogo; pensando acompanha requisições; observando acompanha a seleção;
alerta responde a tentativas erradas; ensinando acompanha pistas/revelações;
elogiando marca acertos; comemorando marca capítulos concluídos. A pose feliz
foi preservada como asset disponível para futuras lições.

O personagem ocupa uma coluna própria no desktop e uma faixa própria no
mobile. Só o conteúdo vizinho rola. A imagem anterior permanece até a próxima
pose terminar de carregar, evitando desaparecimento na troca. As demais poses
são pré-carregadas ao entrar no modo.

## Progresso

`chesslab.learning.v1` guarda `{ "chapters": { "movimentos": ["e2e4"] } }`.
O navegador salva após cada acerto; reabrir um capítulo retoma a próxima lição.
Recomeçar apaga somente o progresso daquele capítulo. Dados malformados são
ignorados; histórico sintaticamente válido mas incompatível recebe orientação
para reiniciar. Armazenamento bloqueado exibe aviso e permite seguir em memória.
Falhas de rede mantêm a posição para tentar novamente. Respostas de uma tela
abandonada não atualizam a nova tela.

## Expandir

1. Acrescente um `Exercise` a um `Chapter`, ou um novo capítulo ao catálogo.
2. Defina FEN legal, objetivo inequívoco, todas as soluções aceitas, conceito e
   feedback. Use `reply` somente para respostas didáticas predefinidas.
3. Preserve IDs e ordem de exercícios publicados, ou versione a chave de
   progresso e faça a migração antes de alterar a sequência.
4. Rode os testes de currículo, API e navegador. Ajuste a contagem esperada
   quando acrescentar conteúdo. Adicione verificações semânticas para novos
   conceitos, além de simplesmente verificar a legalidade dos lances.

## Limites desta versão

- Exercícios curados e uma partida curta roteirizada; não é análise livre de
  qualquer partida nem adversário de IA.
- Aprendizado joga de brancas; não há exercícios de promoção ou en passant
  neste catálogo inicial. Essas regras continuam cobertas no multiplayer.
- Progresso não sincroniza entre navegadores; limpar dados locais o remove.
- A validação responsiva usa Chromium com emulação de viewport/toque; teste
  manual em dois aparelhos físicos continua recomendado antes de publicar.
