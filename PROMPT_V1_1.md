# Chess Lab — Prompt V1.1 (Hints + Visual Polish)

A V1 do Chess Lab já foi validada em uma partida multiplayer real.

Quero evoluir para a V1.1 sem reescrever o produto nem quebrar o núcleo existente.

## Antes de alterar qualquer coisa

Leia, nesta ordem:

1. `AGENTS.md`
2. `README.md`
3. `docs/PRODUCT.md`
4. `docs/ARCHITECTURE.md`
5. `docs/V1_SCOPE.md`
6. `docs/DECISIONS.md`
7. `docs/VISUAL_DIRECTION.md`
8. `docs/STYLE_TOKENS.md`
9. `docs/V1_1_SCOPE.md`
10. `docs/V1_1_DECISIONS.md`
11. `docs/REFERENCES.md`
12. todas as imagens em `docs/references/`

Depois inspecione o código atual e a suíte de testes.

As telas atuais do Chess Lab são a BASE APROVADA. Evolua a interface; não redesenhe tudo do zero.

---

# Objetivos da V1.1

## 1. Melhorar profundamente o sistema de dicas

A Partida Assistida deve ensinar melhor.

Hoje o projeto usa heurísticas locais. Preserve o fallback heurístico, mas adicione uma camada opcional de análise com Stockfish.

### Filosofia

Stockfish é um ANALISADOR, não o professor.

Não quero que o sistema simplesmente pergunte para a engine e entregue o melhor lance.

A engine deve fornecer evidência sobre a posição para que o Chess Lab produza dicas progressivas e pedagógicas.

### Níveis 1–4

Os quatro níveis continuam voltados ao raciocínio:

**Nível 1 — Observe**
- chamar atenção para uma ameaça, oportunidade ou desequilíbrio;
- não citar o lance exato.

**Nível 2 — Olhe mais perto**
- indicar peça, região, linha, coluna, diagonal ou lado do tabuleiro;
- ainda sem entregar o movimento.

**Nível 3 — Entenda a ideia**
- explicar o conceito tático/estratégico relevante;
- exemplos: peça solta, garfo, cravada, raio-X, ataque duplo, rei exposto, desenvolvimento, controle de coluna, promoção etc.;
- não entregar a jogada exata.

**Nível 4 — Uma possibilidade**
- aproximar bastante o raciocínio;
- pode indicar a peça que merece atenção e o objetivo do movimento;
- ainda evitar mostrar origem + destino exatos quando possível.

As dicas devem ser específicas à posição atual sempre que a análise permitir.
Evite templates vagos repetitivos.

### Botão separado: “Revelar uma possibilidade”

O lance exato NÃO faz parte automaticamente da progressão 1–4.

Adicionar um botão separado, visualmente secundário:

`Revelar uma possibilidade`

Ao clicar, abrir um modal de confirmação.

Texto aproximado (pode melhorar a redação preservando o significado):

> Esta opção revela uma jogada já calculada para a posição atual.
> Ao usá-la, você pratica menos o processo de encontrar a jogada por conta própria.
> Para aprender melhor, tente as dicas anteriores primeiro.

Ações:

- `Continuar pensando`
- `Mostrar jogada mesmo assim`

Se o usuário confirmar:

- revelar UMA jogada forte/razoável;
- mostrar notação;
- destacar origem/destino no tabuleiro;
- explicar em 1–3 frases por que a jogada é interessante;
- deixar claro que é uma possibilidade calculada e que outras jogadas podem existir.

Não use linguagem de culpa ou julgamento.

---

# 2. Stockfish

Integrar Stockfish de modo simples e robusto.

Requisitos:

- preferir subprocesso/local engine;
- caminho configurável (`STOCKFISH_PATH` ou equivalente);
- detectar indisponibilidade;
- se Stockfish não estiver disponível, o Chess Lab continua funcionando com o sistema heurístico atual;
- não tornar uma API externa obrigatória;
- não introduzir serviço pago;
- não bloquear o event loop do FastAPI por análises longas;
- limitar profundidade/tempo de análise para uma experiência rápida;
- cachear análise por FEN quando fizer sentido;
- cancelar/ignorar análise obsoleta se a posição mudar;
- nunca permitir que a engine altere o estado oficial da partida.

Se instalar Stockfish localmente for necessário e seguro, faça da forma menos invasiva possível.
Não altere kernel, drivers, boot ou configurações irrelevantes.

Adicione testes do fallback e da integração quando praticável.

---

# 3. Visual: mais fofo, acolhedor e bonito

Preserve a identidade que já funcionou:

- dark;
- verde laboratório;
- minimalista;
- limpa;
- elegante;
- tabuleiro como foco.

Mas deixe o produto mais acolhedor e charmoso.

“Cute” aqui significa:

**suave + aconchegante + charmoso + delicado**

NÃO significa:

- infantil;
- corações em todo lugar;
- excesso de rosa;
- emoji em excesso;
- mascote aleatório;
- fonte infantil;
- visual kawaii exagerado.

Use `docs/VISUAL_DIRECTION.md`, `docs/STYLE_TOKENS.md`, `docs/REFERENCES.md` e os screenshots locais como guia.

---

# 4. Temas de tabuleiro

Criar arquitetura de temas sem duplicar CSS desnecessariamente.

Temas iniciais:

- Laboratory
- Matcha
- Strawberry Milk
- Midnight
- Lavender
- Elmore (tema especial inspirado na energia visual de The Amazing World of Gumball, mas com assets e composição originais; não copiar personagens, logos, screenshots ou cenários oficiais)

A preferência deve ser salva localmente no navegador.

Não precisa de conta ou banco.

O tabuleiro deve continuar com contraste suficiente e casas claramente distinguíveis.

---

# 5. Skins de peças

Criar arquitetura para skins.

Inicialmente:

- Classic
- Soft
- Cute
- Minimal
- Cartoon (skin original, mais expressiva e arredondada, sem personagens oficiais)

Requisitos:

- peças sempre legíveis;
- distinguir cores imediatamente;
- não comprometer acessibilidade;
- não depender de CDN se puder evitar;
- preferir SVG/local assets;
- nenhuma skin pode dificultar reconhecer rei, dama, torre, bispo, cavalo ou peão.

A skin Cute deve ser charmosa e suave, não infantil.

---

# 6. Microinterações

Adicionar apenas onde melhora feedback:

- movimento de peça;
- seleção;
- hover;
- entrada/saída de modal;
- conexão;
- xeque;
- fim de partida;
- dica desbloqueada;
- cópia do código da sala.

Manter animações discretas e rápidas.

Respeitar `prefers-reduced-motion`.

---

# 7. Configurações visuais

Adicionar um seletor simples de aparência dentro da experiência, sem criar uma tela de configurações gigante.

Permitir:

- tema do tabuleiro;
- skin de peças.

Salvar no navegador.

As escolhas visuais são locais; não precisam sincronizar entre jogadores.

---

# 8. Não quebrar a V1

Antes de finalizar, valide novamente:

- criação de sala;
- entrada;
- dois WebSockets;
- sincronização;
- turno;
- movimentos legais;
- movimentos ilegais;
- roque;
- en passant;
- promoção;
- xeque;
- xeque-mate;
- empate;
- desconexão;
- reconexão;
- partida assistida;
- dicas;
- partida completa.

A V1.1 não está pronta se algum desses fluxos regredir.

---

# 9. Documentação

Ao concluir:

- incorpore as decisões relevantes de `docs/V1_1_DECISIONS.md` em `docs/DECISIONS.md` ou mantenha referências consistentes;
- atualize README se instalação/execução mudar;
- documente Stockfish e fallback;
- documente temas/skins;
- registre limitações encontradas.

---

# 10. Processo de trabalho

Trabalhe autonomamente:

1. inspecione;
2. planeje brevemente;
3. implemente incrementalmente;
4. rode testes;
5. corrija;
6. faça validação visual se houver ferramenta disponível;
7. compare com os screenshots atuais;
8. execute suíte completa;
9. entregue relatório curto.

Não pare apenas para me apresentar um plano.

No final informe:

- o que mudou;
- como Stockfish foi integrado;
- como funciona o fallback;
- como funcionam dicas 1–4;
- como funciona “Revelar uma possibilidade”;
- temas/skins criados;
- testes executados;
- limitações;
- próximos passos sugeridos.
