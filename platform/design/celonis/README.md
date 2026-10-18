# Celonis design language

`celonis.css` is the Celonis design language from https://www.celonis.com/de as a
single drop-in stylesheet. The tokens are Celonis' own foundation tokens
(`--fnd-*`), copied value-for-value from the site's `styles.css` on 2026-10-17.
The element and `.cel-*` component rules recreate how the site uses those tokens.

Open `preview.html` to see every token, theme and component.

## Apply it to any HTML file

```html
<link rel="stylesheet" href="platform/design/celonis/celonis.css">
```

That alone restyles plain elements: body, headings, links, buttons, inputs,
tables, code and blockquotes. Every element rule is wrapped in `:where()`
(zero specificity), so the page's own CSS still wins. To restyle an existing
page fully, replace its hard-coded colours, sizes and radii with the tokens below.

**Theme.** The stylesheet follows the OS light/dark setting. To force one:
`<html data-theme="light">` or `<html data-theme="dark">`.
To re-theme part of a page, put a theme class on any element:

| Class | Surface | Use for |
|---|---|---|
| `.light-base-theme` | `#fff` | default content |
| `.light-secondary-theme` | `#f5f5f5` | alternating grey bands |
| `.dark-base-theme` | `#000` | hero, nav, footer |
| `.dark-secondary-theme` | `#1d1d1d` | raised panels on dark |
| `.dark-accent-theme` | `#0029ff` | Celonis-blue feature band |

## The language in brief

- **Monochrome first.** Black, white and a grey ramp do almost all the work
  (`#000 #1d1d1d #333 #4d4d4d #666 #767676 #8e8d8d #cbcbcb #e5e5e5 #f5f5f5 #fff`).
- **One accent: neon green `#5cfe50`.** Use it for the single most important
  action (`button.conversion`), the square bullet on `a.conversion` links, and
  highlights. Don't use it for decoration. Celonis blue `#0029ff` appears only
  as a full section background (`.dark-accent-theme`).
- **Poppins Regular, one weight.** Headings are never bold. Large sizes use
  tight negative letter-spacing (−0.5px to −4px). The type scale steps up at
  768, 960, 1200 and 1600px. The page loads Poppins from Google Fonts with a
  metric-matched Arial fallback.
- **Squares, not circles.** Radii are 2px (buttons, labels), 4px (cards,
  images) and 8px (code blocks). Bullets and status dots are small squares.
- **Flat surfaces.** No shadows. Hover moves a surface one background step
  (secondary → tertiary), and dark buttons turn translucent.
- **4px spacing grid.** `--fnd-spacing-01…12` = 4, 8, 12, 16, 20, 24, 32, 40,
  56, 64, 80, 112px. Page gutters grow 20 → 32 → 40 → 56 → 64px, and content
  is capped at 1472px.
- **Calm motion.** 0.2–0.3s `ease-in-out` on colour changes. Everything is
  switched off under `prefers-reduced-motion`.

## Tokens

| Group | Tokens |
|---|---|
| Text | `--fnd-color-text-{high,mid,low,inverse,state-disabled}`, `--fnd-color-semantic-text-{success,danger}` |
| Background | `--fnd-color-background-{base,secondary,tertiary,quaternary,quinary,inverse,accent-green,accent-secondary,state-disabled,transparency-mid,transparency-low}`, `--fnd-color-semantic-background-{success,danger}` |
| Border | `--fnd-color-border-{high,mid-dark,mid,low,inverse,state-disabled}`, `--fnd-color-semantic-border-{success,danger}` |
| Fixed | `--fnd-color-always-dark`, `--fnd-color-always-light` |
| Type | `--fnd-typography-{paragraph-xs…xl, heading-xxs…xxl, display-s}-{font-size,line-height,letter-spacing}`, `--ff-celonis-poppins`, `--ff-mono` |
| Space / shape | `--fnd-spacing-none, 01…12`, `--fnd-radius-{none,s,m,l}`, `--fnd-image-ratio-*` |
| Motion | `--fnd-motion-ease-{informative,focused,expressive}`, `--fnd-motion-duration-*`, `--fnd-motion-delay-*` |

Headings map onto the scale: h1 = heading-xl, h2 = l, h3 = m, h4 = s,
h5 = xs, h6 = xxs. Body text is paragraph-xl.

## Components

| Markup | What it is |
|---|---|
| `<button>` / `<a class="button">` | Primary, solid inverse, 48px tall. Sizes: `.small` 40px, `.large` 56px, `.xlarge` 72px |
| `.secondary` · `.conversion` · `.ghost` · `.icon-button` · `:disabled` | Button variants |
| `<a class="conversion">` | Text link with the green square bullet |
| `.cel-label` (`.dense`, `.success`, `.danger`, `.accent`) in `.cel-labels` | Tag chips |
| `.cel-card` (`.outlined`) | Flat card; deepens on hover when it's a link or has `tabindex` |
| `.cel-stat` with `.value` + `.caption` | Square big-number tile |
| `.cel-grid` (`.cols-2`, `.cols-4`) | Card grid, 1 → 3 columns by default |
| `.cel-container` · `.cel-section` | Page-width wrapper with responsive gutters · vertical section rhythm |
| `.cel-nav` | Always-black top bar; links marked `.cel-nav-optional` hide below 768px |
| `.cel-notice` (`.success`, `.danger`) | Inline message |
| `.cel-overline` · `.cel-muted` · `.cel-text-{l,m,s}` · `.cel-display` · `.cel-heading-xxl` · `.cel-highlight` · `.cel-dot` | Type and accent helpers |

## Not included

- **Celonis' own build of Poppins.** It ships stylistic sets for square
  punctuation, a double-storey "a" and alternate numerals. The stylesheet keeps
  the `font-variant-alternates` and `@font-feature-values` rules so those
  glyphs appear if that font is installed. With Google Fonts Poppins, you get
  the standard glyphs.
- **Logos, icons and imagery.** These are Celonis brand assets and aren't copied.
  This stylesheet captures the visual language, not the brand identity, so
  don't use it to make pages that pass as Celonis.
