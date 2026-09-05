# Chess Lab — Agent Instructions

## Purpose
Chess Lab é uma aplicação web multiplayer para duas pessoas jogarem e aprenderem xadrez juntas.

Antes de implementar alterações relevantes, leia:
- `docs/PRODUCT.md`
- `docs/ARCHITECTURE.md`
- `docs/V1_SCOPE.md`
- `docs/DECISIONS.md`

Se uma decisão relevante mudar, registre em `docs/DECISIONS.md`.

## Stack
Backend:
- Python
- FastAPI
- WebSocket
- python-chess

Frontend:
- HTML
- CSS
- JavaScript puro

O backend também serve o frontend.

## Princípios
- O servidor é a fonte da verdade.
- Cliente envia intenção de jogada; servidor valida e aplica.
- Nunca confiar no estado de tabuleiro enviado pelo cliente.
- Usar `python-chess` para regras.
- Manter arquitetura simples e legível.
- Multiplayer deve funcionar entre dois dispositivos reais.
- Salas da V1 ficam em memória.
- Evitar dependências desnecessárias.
- Não adicionar recursos fora do escopo da V1 sem motivo.

## Multiplayer
Fluxo esperado:
1. Jogador A cria sala.
2. Servidor gera código curto.
3. A recebe brancas.
4. Jogador B entra pelo código.
5. B recebe pretas.
6. Ambos conectam por WebSocket.
7. Servidor controla turno, posição e regras.
8. Após jogada válida, servidor transmite novo estado aos dois.
9. Jogadas inválidas são rejeitadas sem alterar a partida.

## Partida Assistida
Existe um botão `Pedir dica`.

A ajuda deve ser progressiva:
1. observação geral;
2. peça/região relevante;
3. explicação do conceito;
4. por último, uma jogada razoável.

Pode usar heurísticas simples para:
- xeques;
- capturas;
- peças atacadas;
- peças sem defesa;
- material;
- desenvolvimento;
- segurança do rei.

Não usar API paga nem IA externa na V1.

## Workflow
Ao receber uma tarefa:
1. leia a documentação;
2. inspecione o projeto;
3. implemente a menor solução correta;
4. execute testes;
5. corrija erros;
6. teste novamente;
7. atualize docs se necessário;
8. entregue relatório curto.

Não considere concluído só porque o código foi escrito.

## Testes mínimos
Validar:
- servidor inicia;
- frontend abre;
- criação de sala;
- segundo jogador entra;
- duas conexões WebSocket;
- movimento válido;
- movimento inválido;
- fora do turno;
- peça adversária;
- sincronização;
- desconexão/reconexão;
- promoção;
- roque;
- en passant;
- xeque;
- xeque-mate;
- empate;
- dica;
- ausência de erros JS óbvios.

## Fora do escopo
Não implementar agora:
- login;
- conta;
- banco de dados;
- ranking;
- ELO;
- matchmaking;
- amigos;
- chat;
- histórico permanente;
- IA adversária;
- pagamentos;
- microserviços;
- React/Vue/Angular;
- Kubernetes.

## Segurança
Trabalhar somente dentro deste projeto, exceto instalações normais necessárias.

Não alterar:
- drivers;
- boot;
- kernel;
- configurações globais;
- arquivos pessoais fora do projeto.

Não usar `sudo` sem necessidade real.
Evitar comandos destrutivos.
