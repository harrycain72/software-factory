# Material Design 3

`material3.css` is Google's Material Design 3 style system from
https://m3.material.io/styles as a single drop-in stylesheet. The tokens are
the official M3 design tokens (`--md-ref-*`, `--md-sys-*`), generated
value-for-value from Google's `material-web` repository
(`tokens/versions/v0_192`, "Google Material 3", baseline scheme from seed
`#6750A4`) on 2026-10-17. The element and `.md-*` component rules follow the M3
component specs and use only those tokens.

Open `preview.html` (served over http, e.g. `python3 -m http.server`) to see
every token, both themes and every component. The seed-colour picker in its
top bar regenerates the whole scheme.

| File | What it is |
|---|---|
| `material3.css` | Tokens, light and dark schemes, base element styles, `.md-*` components and utilities |
| `theme.js` | Optional. Builds a full M3 scheme from any brand colour |
| `preview.html` | Specimen page |

## Apply it to any HTML file

```html
<link rel="stylesheet" href="platform/design/material_design_3/material3.css">
```

That alone restyles plain elements: body, headings, links, buttons, inputs,
selects, tables, code, blockquotes and `hr`. Every element rule is wrapped in
`:where()` (zero specificity), so the page's own CSS still wins. To restyle an
existing page fully, replace its hard-coded colours, sizes and radii with the
tokens below. Roboto and Material Symbols load from Google Fonts.

**Theme.** The stylesheet follows the OS light/dark setting. To force one, use
`<html data-theme="light">` or `<html data-theme="dark">`. A `data-theme` on
any other element re-themes that subtree and paints its surface.

**Your own colour.** M3 schemes are generated from one seed colour. Add this
after the stylesheet:

```html
<script type="module" src="platform/design/material_design_3/theme.js" data-seed="#0b57d0"></script>
```

This uses Google's `material-color-utilities` (the Theme Builder engine,
loaded from jsDelivr) to write all `--md-sys-color-*` roles for light and dark.
Options: `data-variant="tonal-spot|vibrant|expressive|neutral|fidelity|content|monochrome"`
(default `tonal-spot`; use `fidelity` to stay closest to the exact brand hue)
and `data-contrast` from `-1` to `1` (`0.5` medium, `1` high). From JS, use
`import { applyTheme } from "./theme.js"; await applyTheme("#0b57d0", { variant: "vibrant" })`.
Without the script, or offline, the baseline purple scheme applies.

## The language in brief

- **Colour roles, not colours.** Use `primary` for key actions, `secondary` for
  less prominent ones, `tertiary` for contrasting accents and `error` for errors.
  Each role has a `-container` for lower-emphasis fills. Always pair a fill with
  its `on-` role for text and icons (`primary` → `on-primary`,
  `secondary-container` → `on-secondary-container`).
- **Tonal surfaces.** Depth comes mostly from surface tone, not shadow. From the
  page outward: `surface` → `surface-container-lowest/low/(default)/high/highest`.
  Use `outline` for important borders and `outline-variant` for dividers.
- **Roboto, fifteen roles.** Display, headline, title, body and label, each in
  large, medium and small. Medium weight (500) appears only on title-medium and
  title-small and on the label roles. Headings map h1 = display-small,
  h2 = headline-large, h3 = headline-medium, h4 = headline-small,
  h5 = title-large, h6 = title-medium. Body text is body-large.
- **Rounded shape scale.** 0, 4, 8, 12, 16 and 28px, plus full. Buttons and
  chips use full/8px, cards 12px, FABs 16px and dialogs 28px.
- **Soft elevation.** Levels 0–5 (0, 1, 3, 6, 8, 12dp) as paired key and
  ambient shadows. Raised components also move to a lighter surface-container.
- **State layers.** Hover, focus, pressed and dragged lay the content colour
  over the component at 8%, 12%, 12% and 16% opacity. Buttons, chips, cards,
  list items and nav items get this automatically. Add `.md-state` to anything
  else. Disabled is on-surface at 12% (container) and 38% (content).
- **Emphasized motion.** `cubic-bezier(.2,0,0,1)`. Durations run from short1
  (50ms) to extra-long4 (1000ms). Everything is switched off under
  `prefers-reduced-motion`.
- **Adaptive layout.** Window size classes are compact (<600px), medium
  (600–839), expanded (840–1199), large (1200–1599) and extra-large (≥1600).
  Margins are 16px on compact and 24px above. Use the navigation bar on compact
  and the navigation rail from medium up.

## Tokens

| Group | Tokens |
|---|---|
| Colour roles | `--md-sys-color-{primary,secondary,tertiary,error}`, `-container`, `on-*`, `*-fixed`, `*-fixed-dim`, `on-*-fixed(-variant)`; `surface`, `surface-dim`, `surface-bright`, `surface-container-{lowest,low,,high,highest}`, `on-surface(-variant)`, `inverse-surface`, `inverse-on-surface`, `inverse-primary`, `outline(-variant)`, `background`, `shadow`, `scrim`, `surface-tint` |
| Tonal palettes | `--md-ref-palette-{primary,secondary,tertiary,neutral,neutral-variant,error}{0…100}` |
| Type | `--md-sys-typescale-{display,headline,title,body,label}-{large,medium,small}-{font,weight,size,line-height,tracking}`, `--md-ref-typeface-{brand,plain,weight-regular,weight-medium,weight-bold}` |
| Shape | `--md-sys-shape-corner-{none,extra-small,small,medium,large,extra-large,full}` (+ `-top`, `-start`, `-end` variants) |
| Elevation | `--md-sys-elevation-level{0…5}` (box-shadow), `--md-sys-elevation-level{0…5}-dp` |
| Motion | `--md-sys-motion-duration-{short,medium,long,extra-long}{1…4}`, `--md-sys-motion-easing-{emphasized,emphasized-accelerate,emphasized-decelerate,standard,standard-accelerate,standard-decelerate,linear,legacy*}` |
| State | `--md-sys-state-{hover,focus,pressed,dragged}-state-layer-opacity` |
| Layout | `--md-margin`, `--md-gutter`, `--md-content-max` |

## Components

| Markup | What it is |
|---|---|
| `<button>` / `<a class="md-button">` | Filled button. Variants: `.elevated`, `.tonal`, `.outlined`, `.text`, `.error`; `:disabled` / `aria-disabled` |
| `<button class="md-icon-button">` | Icon button. Variants: `.filled`, `.tonal`, `.outlined`; `.selected` toggles |
| `.md-fab` | FAB. Sizes `.small`/`.large`; `.extended` adds a label; colours `.surface`, `.secondary`, `.tertiary`; `.fixed` pins it bottom-right |
| `.md-segmented` > `button[aria-pressed]` | Segmented button |
| `.md-chip` in `.md-chips` | Assist/suggestion chip. `.selected` or `aria-pressed="true"` makes a filter chip; `.elevated`; `.md-chip-remove` inside makes an input chip |
| `.md-card` | Elevated card. `.filled` and `.outlined` are the other two types. Gets a state layer when it's an `a`, a `button` or has `tabindex`. `.md-media` and `.md-actions` inside |
| `<label class="md-field"><input placeholder=" "><span>Label</span></label>` | Outlined text field with floating label. `.filled` variant, `.error` state, `<small class="md-supporting">`. Also works with `textarea` and `select` |
| `<input type="checkbox" class="md-switch" role="switch">` | Switch |
| `<progress class="md-progress">` | Linear progress. Omit `value` for indeterminate |
| `.md-list` > `.md-list-item` | List item with `.md-avatar`/`.md-icon`, `.md-headline`, `.md-supporting`, `.md-trailing`; `.md-divider(.inset)` |
| `.md-top-app-bar` with `.md-title` | Small top app bar. `.medium` and `.large` variants; `.scrolled` raises it |
| `.md-nav-bar` / `.md-nav-rail` > `.md-nav-item[aria-current]` | Navigation bar (compact) and rail (medium+), with active indicator |
| `.md-tabs` > `.md-tab[aria-selected]` | Primary tabs |
| `<dialog class="md-dialog">` | Basic dialog with `h2` and `.md-actions` |
| `.md-snackbar` (`.fixed`) | Snackbar |
| `.md-tooltip[data-tooltip]` | Plain tooltip |
| `.md-badge` | Badge. Empty means the small dot |
| `<span class="md-icon">home</span>` | Material Symbols Outlined. `.filled` for the filled style |
| `.md-layout` > `.md-nav-rail` + `main` | App shell; the rail hides on compact. `.md-compact-only`, `.md-hide-compact` |
| `.md-container` · `.md-section` · `.md-grid` · `.md-row` · `.md-stack` | Page width, vertical rhythm, auto-fill grid (`--md-grid-min`), wrapping row, vertical stack |
| `.md-typescale-*` · `.md-{role}` · `.md-surface-container-*` · `.md-elevation-{0…5}` · `.md-shape-{none,xs,s,m,l,xl,full}` | Type, colour-pair, elevation and shape utilities |

## Not included

- **Material Web components (`<md-*>` custom elements) and JavaScript
  behaviour.** This is a CSS rendition of the style system. Ripples are state
  layers without the ripple animation. Menus, date and time pickers, sliders,
  carousels, bottom and side sheets, and search aren't styled beyond native
  controls.
- **Material 3 Expressive additions** such as shape morphing, the expanded
  shape library and spring motion. The tokens are the stable M3 baseline.
- **Google Sans and Google brand assets.** M3's public typeface is Roboto.
