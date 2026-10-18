/*
 * Material Design 3 — custom colour scheme from a seed colour (optional).
 *
 * material3.css ships the baseline scheme (seed #6750A4). This module builds
 * the full light and dark M3 colour schemes from any brand colour with
 * Google's material-color-utilities (the same engine as Material Theme
 * Builder and dynamic colour), and writes them as --md-sys-color-* overrides.
 *
 * Use, after material3.css:
 *   <script type="module" src="platform/design/material_design_3/theme.js" data-seed="#0b57d0"></script>
 * Optional attributes: data-variant="tonal-spot|vibrant|expressive|neutral|fidelity|content|monochrome"
 *                      data-contrast="0" (-1 … 1; 0.5 = medium, 1 = high)
 * Or from JS:  import { applyTheme } from "./theme.js"; applyTheme("#0b57d0");
 */

const MCU = "https://cdn.jsdelivr.net/npm/@material/material-color-utilities@0.4.0/+esm";

const ROLES = [
  "primary", "onPrimary", "primaryContainer", "onPrimaryContainer", "inversePrimary",
  "primaryFixed", "primaryFixedDim", "onPrimaryFixed", "onPrimaryFixedVariant",
  "secondary", "onSecondary", "secondaryContainer", "onSecondaryContainer",
  "secondaryFixed", "secondaryFixedDim", "onSecondaryFixed", "onSecondaryFixedVariant",
  "tertiary", "onTertiary", "tertiaryContainer", "onTertiaryContainer",
  "tertiaryFixed", "tertiaryFixedDim", "onTertiaryFixed", "onTertiaryFixedVariant",
  "error", "onError", "errorContainer", "onErrorContainer",
  "background", "onBackground", "surface", "onSurface", "surfaceVariant", "onSurfaceVariant",
  "surfaceDim", "surfaceBright", "surfaceContainerLowest", "surfaceContainerLow",
  "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest",
  "inverseSurface", "inverseOnSurface", "outline", "outlineVariant", "shadow", "scrim", "surfaceTint",
];

const VARIANTS = {
  "tonal-spot": "SchemeTonalSpot", vibrant: "SchemeVibrant", expressive: "SchemeExpressive",
  neutral: "SchemeNeutral", fidelity: "SchemeFidelity", content: "SchemeContent", monochrome: "SchemeMonochrome",
};

const kebab = (s) => s.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase());

/** Returns { light, dark } maps of CSS custom property → hex for a seed colour. */
export async function schemesFromSeed(seed, { variant = "tonal-spot", contrast = 0 } = {}) {
  const mcu = await import(MCU);
  const Scheme = mcu[VARIANTS[variant] ?? VARIANTS["tonal-spot"]];
  const hct = mcu.Hct.fromInt(mcu.argbFromHex(seed));
  const build = (dark) => {
    const scheme = new Scheme(hct, dark, contrast);
    const out = {};
    for (const role of ROLES) {
      const dc = mcu.MaterialDynamicColors[role];
      if (dc) out[`--md-sys-color-${kebab(role)}`] = mcu.hexFromArgb(dc.getArgb(scheme));
    }
    return out;
  };
  return { light: build(false), dark: build(true) };
}

/** Builds the schemes and installs them as a <style id="md-theme"> after material3.css. */
export async function applyTheme(seed, options = {}) {
  const { light, dark } = await schemesFromSeed(seed, options);
  const decl = (map) => Object.entries(map).map(([k, v]) => `${k}: ${v};`).join(" ");
  const css =
    `:root, [data-theme="light"] { ${decl(light)} }\n` +
    `[data-theme="dark"] { ${decl(dark)} }\n` +
    `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { ${decl(dark)} } }`;
  let style = document.getElementById("md-theme");
  if (!style) {
    style = document.createElement("style");
    style.id = "md-theme";
    document.head.append(style);
  }
  style.textContent = css;
  return { light, dark };
}

// Auto-apply when loaded as <script type="module" src="theme.js" data-seed="#…">.
const tag = [...document.querySelectorAll('script[type="module"][data-seed]')].find((s) => s.src === import.meta.url);
if (tag) {
  applyTheme(tag.dataset.seed, { variant: tag.dataset.variant, contrast: Number(tag.dataset.contrast) || 0 })
    .catch((err) => console.warn("[material3 theme] falling back to baseline scheme:", err));
}
