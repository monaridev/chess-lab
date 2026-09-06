# Prompt sugerido para o Codex / Work

Leia integralmente a documentação em `docs/solo/` antes de alterar código.

Implemente o modo **Solo Offline** do ChessLab conforme os documentos de produto, arquitetura, decisões, análise de jogadas e testes.

Pontos obrigatórios:
- usar Stockfish local como adversário;
- não usar LLM;
- não usar API externa paga;
- não adicionar banco de dados;
- não implementar Elo/rating;
- oferecer dificuldades Iniciante, Fácil, Médio e Difícil;
- analisar cada jogada do usuário após ela acontecer;
- classificar cada jogada com o sistema próprio do ChessLab;
- gerar comentário curto e específico do Professor Pogona a partir das evidências reais da posição;
- reaproveitar `backend/hints.py`, `backend/analysis.py` e demais estruturas existentes sempre que fizer sentido;
- manter o Pogona visível durante toda a partida;
- usar poses coerentes com a classificação/contexto;
- calcular uma métrica de precisão da partida;
- criar resumo pós-partida;
- usar `localStorage` apenas para estatísticas locais opcionais;
- manter Normal, Assistido, Aprender e multiplayer sem regressões.

Antes de implementar, analise a arquitetura atual e escolha a menor mudança estrutural que mantenha o código organizado e expansível.

Não copie fórmulas, thresholds, nomenclatura visual ou comportamento proprietário de plataformas externas. O sistema de classificação e precisão deve ser próprio do ChessLab.

A análise pós-lance deve distinguir avaliação de engine de explicação pedagógica. Stockfish mede; o ChessLab interpreta.

Ao final:
1. rode toda a suíte existente;
2. adicione testes específicos do Solo;
3. corrija regressões;
4. faça teste manual local quando possível;
5. entregue resumo do que foi implementado;
6. liste arquivos alterados;
7. informe limitações e pendências;
8. não faça `git push` sem autorização explícita.
