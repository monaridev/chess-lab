# Prompt sugerido para o Codex

Leia toda a documentação em `docs/solo/` antes de alterar código.

Implemente o Modo Solo Offline descrito nesses documentos, usando Stockfish como adversário e mantendo o Professor Pogona como camada pedagógica.

Antes de implementar, analise a arquitetura atual e localize a integração Stockfish já existente. Reaproveite `python-chess`, `backend/analysis.py`, `backend/hints.py` e os componentes atuais sempre que fizer sentido.

Requisitos principais:
- não usar IA generativa para escolher lances;
- permitir partida individual contra Stockfish;
- oferecer níveis de força adequados a iniciantes;
- adicionar modos de ajuda Guiado, Assistido e Livre;
- manter o Pogona visível e usar os estados visuais existentes;
- manter falas em balões próximos ao personagem;
- criar resumo pedagógico pós-partida;
- não adicionar login ou banco;
- manter Normal, Assistido, Aprender e multiplayer intactos;
- criar testes de backend, integração e frontend para o novo fluxo;
- executar toda a suíte ao final e corrigir regressões.

Tome decisões técnicas por conta própria quando necessário, mas preserve simplicidade e a arquitetura existente.

Ao final, entregue:
1. resumo do que foi implementado;
2. arquivos criados/alterados;
3. testes executados e resultados;
4. limitações conhecidas;
5. próximos passos recomendados.
