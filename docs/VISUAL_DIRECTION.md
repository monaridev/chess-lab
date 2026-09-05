# Chess Lab — Visual Direction V1.1

> V1.2: `references/ref-gumball.png` é a referência visual principal e tem
> prioridade sobre orientações antigas abaixo. Veja `V1_2_SCOPE.md`.

## Regra principal

A interface atual está APROVADA.

A V1.1 deve parecer uma evolução natural do produto existente, não um redesign desconectado.

Consulte as imagens em `docs/references/` para ver:

- home atual;
- partida;
- retomada de sessão;
- xeque-mate.

## Personalidade

Palavras-chave:

- laboratório aconchegante;
- inteligente;
- gentil;
- curioso;
- delicado;
- moderno;
- limpo;
- charmoso;
- calmo.

A interface deve parecer um lugar confortável para duas pessoas passarem tempo aprendendo juntas.

## O significado de “fofo”

Neste projeto:

`fofo = suave + acolhedor + charmoso + pequenos detalhes de personalidade`

Não:

`fofo = infantil + rosa excessivo + coração + emoji + mascote`

## O que preservar

- dark green como base;
- bastante espaço negativo;
- headline grande e limpa;
- cards com bordas discretas;
- hierarquia forte;
- tabuleiro central;
- green/mint como cor funcional;
- linguagem editorial curta;
- aparência de produto real.

## O que suavizar

- cantos ligeiramente mais arredondados;
- superfícies menos rígidas;
- hover mais delicado;
- sombras/contornos mais sutis;
- pequenos detalhes pastel;
- ícones de traço fino;
- microinterações rápidas;
- transições suaves.

## Accent colors

Pastéis devem aparecer como detalhes, não dominar a tela.

Sugestões:

- Mint — ações positivas / estado ativo
- Cream — texto principal e superfícies claras
- Lavender — dica/conceito
- Blush pink — detalhe afetivo, seleção temática ou highlight raro
- Soft peach — aviso leve
- Blue-grey — informação secundária

## Sparkles e detalhes

Pequenos `✦`, estrelas geométricas ou brilhos podem aparecer em:

- título de dica;
- confirmação de ação;
- seletor de tema;
- feedback de sucesso.

Nunca espalhar em toda a interface.

## Cards

Cards devem continuar escuros, mas podem ter:

- raio maior;
- borda suave;
- leve mudança de luminância;
- highlight pastel em estado ativo.

Evitar glassmorphism exagerado.

## Modal “Revelar uma possibilidade”

Deve ser:

- bonito;
- acolhedor;
- não alarmista;
- claramente diferente de uma dica normal.

O modal explica a escolha pedagógica sem repreender o usuário.

Botão primário:

`Continuar pensando`

Botão secundário:

`Mostrar jogada mesmo assim`

## Tabuleiro

O tabuleiro é o centro do produto.

Regras:

- contraste sempre alto o suficiente;
- highlights precisam continuar visíveis em todos os temas;
- xeque precisa ser evidente;
- último movimento deve ser perceptível;
- dica pode destacar região/casa sem confundir com seleção normal;
- peças nunca podem “sumir” na casa.

## Temas

### Laboratory
Evolução do tema atual.
Dark green + mint.

### Matcha
Verde suave, cream, sensação orgânica.

### Strawberry Milk
Base escura neutra com rosa/blush/cream em doses pequenas.
Não transformar a tela inteira em rosa.

### Midnight
Azul/preto profundo + lavender/blue accents.

### Lavender
Dark plum/charcoal + lilás suave + cream.

## Skins de peças

### Classic
Conservadora, semelhante à atual.

### Soft
Curvas suaves, pesos mais equilibrados.

### Cute
Formas um pouco mais arredondadas e simpáticas.
Sem olhos, rostos ou estética infantil.

### Minimal
Geométrica, simples e altamente legível.

## Responsividade

A estética não pode prejudicar celular.

Em telas pequenas:

- tabuleiro continua prioridade;
- controles essenciais ficam próximos;
- painéis laterais podem virar drawers/accordion;
- código da sala deve permanecer fácil de copiar;
- dicas não podem empurrar o tabuleiro para fora da tela.

## Acessibilidade

- contraste adequado;
- não depender só de cor;
- foco de teclado visível;
- `prefers-reduced-motion`;
- tamanho de toque confortável;
- temas e skins devem continuar distinguíveis.

## Anti-exemplos

Evitar:

- kawaii excessivo;
- neon gamer agressivo;
- cyberpunk;
- glassmorphism pesado;
- sombra gigante;
- gradiente em tudo;
- 10 cores competindo;
- ícones inconsistentes;
- cards excessivamente arredondados;
- animações longas;
- texto “fofinho” demais em mensagens funcionais.
# Tema especial — Elmore / Gumball-inspired

Adicionar um tema especial opcional inspirado no clima visual de *The Amazing World of Gumball*, pensado para alguém que gosta muito da série.

## Importante

Este tema deve ser uma homenagem visual original.

Não copiar:
- logos oficiais;
- screenshots da série;
- sprites;
- personagens oficiais;
- cenários oficiais;
- assets baixados de fontes não autorizadas.

A inspiração deve vir de:
- combinação de cores;
- energia cartunesca;
- sensação de caderno/escola;
- formas recortadas;
- mistura de elementos 2D;
- pequenos doodles e stickers originais.

## Personalidade

Palavras-chave:

- divertida;
- caótica de leve;
- colorida;
- escolar;
- carismática;
- engraçada;
- inesperada;
- ainda legível.

Não transformar todo o Chess Lab nessa identidade.
É um tema selecionável.

## Paleta sugerida

- azul/ciano vivo como destaque principal;
- rosa suave;
- amarelo quente;
- creme;
- verde menta;
- fundo dark azulado para manter compatibilidade com o produto.

Exemplo de direção:

```css
--elmore-bg: #101820;
--elmore-surface: #18242d;
--elmore-blue: #69c8ff;
--elmore-pink: #f3a7c4;
--elmore-yellow: #f5d66f;
--elmore-mint: #9fd9b6;
--elmore-cream: #fff1d6;
```

Ajustar contraste após testes reais.

## Tabuleiro

Tema `Elmore`:

- casas claras: creme/azul muito claro;
- casas escuras: azul-petróleo/ciano dessaturado;
- último lance: amarelo suave;
- dica: rosa/lilás;
- xeque: vermelho coral.

## UI

Detalhes possíveis:

- pequenos doodles geométricos originais;
- fitas adesivas estilizadas;
- bordas com leve sensação de recorte;
- labels com aparência de adesivo;
- microanimações um pouco mais brincalhonas;
- pequenos elementos de caderno nos painéis.

Não comprometer a clareza da partida.

## Skins

Adicionar uma skin opcional:

`Cartoon`

Características:
- peças originais;
- formas mais arredondadas;
- contorno mais expressivo;
- levemente assimétricas;
- alta legibilidade.

Não desenhar as peças como personagens da série.

## Easter eggs visuais

Pequenos easter eggs originais podem aparecer apenas no tema Elmore, por exemplo:
- um doodle sorrindo no loading;
- pequenas estrelas;
- rabiscos de caderno;
- reação visual rápida ao xeque-mate.

Não usar falas, personagens ou elementos protegidos da série.
