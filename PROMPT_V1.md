# Prompt inicial para Codex / GPT-6 Astra

Quero que você implemente a V1 funcional do Chess Lab neste diretório.

Antes de qualquer alteração:
1. leia `AGENTS.md`;
2. leia `docs/PRODUCT.md`;
3. leia `docs/ARCHITECTURE.md`;
4. leia `docs/V1_SCOPE.md`;
5. leia `docs/DECISIONS.md`;
6. inspecione o diretório atual.

A documentação é a fonte de verdade.

Você tem autorização para criar/editar arquivos dentro deste projeto, instalar dependências locais necessárias, executar servidores, testes e ferramentas de desenvolvimento.

Trabalhe de forma autônoma.

Não pare apenas para apresentar um plano. Planeje brevemente, implemente, execute, teste, corrija e valide.

Só peça intervenção se:
- uma ação potencialmente destrutiva for necessária;
- precisar alterar algo relevante fora do projeto;
- existir decisão de produto realmente ambígua não resolvida nos docs.

Objetivo:
- FastAPI;
- frontend HTML/CSS/JS;
- WebSocket;
- salas por código;
- dois jogadores;
- regras via python-chess;
- servidor como fonte da verdade;
- partida normal;
- partida assistida;
- dicas progressivas;
- reconexão simples;
- interface dark/responsiva;
- testes.

Não adicione recursos fora do escopo.

Se alguma decisão técnica precisar mudar por motivo real, registre em `docs/DECISIONS.md`.

Crie `.gitignore`.
Se ainda não houver Git, inicialize o repositório.

Antes de finalizar:
1. execute testes automatizados;
2. inicie o servidor;
3. teste frontend;
4. simule dois jogadores;
5. valide criação/entrada em sala;
6. valide sincronização;
7. valide movimentos legais/ilegais;
8. valide finais de partida;
9. valide dica;
10. valide desconexão/reconexão;
11. corrija problemas;
12. execute rodada final de testes.

No final, entregue relatório curto com:
- estrutura;
- dependências;
- comando para iniciar;
- testes;
- recursos funcionais;
- limitações;
- sugestões de V2.

Comece agora.
