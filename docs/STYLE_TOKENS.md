# Chess Lab — Style Tokens (direção, não contrato rígido)

> V1.2: `references/ref-gumball.png` é a referência visual principal e tem
> prioridade sobre orientações antigas abaixo. Veja `V1_2_SCOPE.md`.

Use estes valores como ponto de partida. Ajustes são permitidos se melhorarem contraste e coerência.

## Base

```css
--bg-0: #0b1712;
--bg-1: #101f19;
--surface-1: #14261f;
--surface-2: #192d25;

--text-1: #f2f3e8;
--text-2: #a9b9ad;
--text-3: #788b7f;

--mint-1: #c7f0b1;
--mint-2: #a8df91;
--mint-3: #73b866;

--cream: #f3efdf;
--lavender: #c9b8ee;
--blush: #efb8c8;
--peach: #efc2a6;
--blue-soft: #a8c9df;
```

## Semantic

```css
--success: var(--mint-2);
--hint: var(--lavender);
--warning-soft: var(--peach);
--danger-soft: #e88f7a;
--focus-ring: #d7f5c5;
```

## Shape

```css
--radius-sm: 10px;
--radius-md: 14px;
--radius-lg: 18px;
--radius-xl: 24px;
```

Evitar transformar todos os elementos em “pill”.

## Motion

```css
--motion-fast: 120ms;
--motion-base: 180ms;
--motion-slow: 260ms;
```

Preferir `ease-out` para entrada e feedback.

## Shadows

Usar sombras muito discretas em dark mode.
Preferir borda + mudança de superfície antes de sombras pesadas.

## Theme suggestions

### Laboratory

```css
--board-light: #c9e6b7;
--board-dark: #5d806e;
--board-last: #9fd767;
--board-hint: #c9b8ee;
```

### Matcha

```css
--board-light: #e2e7c8;
--board-dark: #7f9c78;
--board-last: #b7d987;
--board-hint: #d7c5ee;
```

### Strawberry Milk

```css
--board-light: #f2ded8;
--board-dark: #bd8f91;
--board-last: #efb8c8;
--board-hint: #c9b8ee;
```

### Midnight

```css
--board-light: #aebed0;
--board-dark: #485a70;
--board-last: #8299c9;
--board-hint: #c4b1ef;
```

### Lavender

```css
--board-light: #ddd2e8;
--board-dark: #806f91;
--board-last: #b8a2d7;
--board-hint: #e6bdd3;
```

Todos os valores devem ser revisados visualmente com peças brancas e pretas e com os estados de:
- seleção;
- legal move;
- last move;
- check;
- hint.
## Elmore

Tema especial inspirado em uma energia cartunesca/escolar, sem usar assets oficiais.

```css
--board-light: #e9f5f7;
--board-dark: #5e91a3;
--board-last: #f5d66f;
--board-hint: #f3a7c4;
--board-check: #ef806f;
```

Accent UI sugerido:

```css
--elmore-blue: #69c8ff;
--elmore-pink: #f3a7c4;
--elmore-yellow: #f5d66f;
--elmore-mint: #9fd9b6;
--elmore-cream: #fff1d6;
```
