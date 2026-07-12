# Handoff: Aura Energy — Brand Identity

## Overview
This bundle is the **Aura Energy** brand identity (design tokens, fonts, logos, iconography) plus a small set of reference UI components. The goal: apply Aura Energy's visual identity to an existing (or new) application codebase.

## About the files
Everything here is a **design reference**, not production code to copy verbatim:
- `colors_and_type.css` is real, usable CSS — wire it in directly (tokens + font-faces + a few semantic classes).
- `reference_components/*.jsx` are **HTML/React prototypes** showing how the brand's components look and behave (a marketing-site kit: header, hero, KPI strip, services, footer). Recreate this look using the target codebase's existing framework and component patterns — don't paste the JSX in as-is unless the target is a plain React app with no existing component system.

## Fidelity
**High-fidelity.** Colors, type, spacing, radii and motion values below are final brand values, not placeholders.

## Design tokens (`colors_and_type.css`)
- **Brand colors:** `--aura-petrol: #006858` (primary, ~80% of surfaces/text), `--aura-lime: #D8F088` (single accent — one CTA, one highlight, never a full background).
- **Neutrals:** `--ink-900…050`, `--paper: #fff`. `--ink-050 (#F2F4F3)` is the only acceptable off-white.
- **Type families:** `--font-display` (Sora Bold — headlines), `--font-eyebrow` (SweetSansPro Medium — all-caps labels, 0.18em tracking), `--font-body` (Open Sans — body/UI copy).
- **Type scale:** `--t-display-xl/l/m/s`, `--t-eyebrow-l/m/s`, `--t-body-xl/l/m/s/xs`.
- **Spacing:** 4pt base, `--space-0` through `--space-32`.
- **Radii:** `--radius-xs(4)` → `--radius-xl(28)`, `--radius-pill(999)`. Default 12px for cards.
- **Shadows:** petrol-tinted only, never pure black (`--shadow-sm/md/lg/xl`).
- **Motion:** `--ease-out` (expo-out entrances), `--ease-inout` (in-out moves), durations `--dur-fast(150ms)/med(280ms)/slow(520ms)`. No bounces/overshoots.

Full rationale and usage rules (color balance, background modes, hover/press states, layout grid) are documented as comments inside `colors_and_type.css`.

## Fonts
`fonts/Sora-Bold.otf`, `fonts/SweetSansProMedium.otf`, `fonts/OpenSans-VariableFont_wdth,wght.ttf` — already wired via `@font-face` in `colors_and_type.css`. Copy the `fonts/` folder alongside it, or point the `src: url(...)` paths at wherever fonts live in the target project.

## Voice & content rules
- Spanish (es-AR), calm/technical tone, no exclamation marks, no emoji.
- Wordmark: "Aura" mixed case + "ENERGY" tracked caps below — never on one baseline as "Aura Energy".
- Eyebrows ALL CAPS wide-tracked; headlines Sora Bold mixed case, no trailing period.
- Lead with physical numbers (MW, GWh/año, toneladas CO₂) before adjectives.

## Assets
- `assets/logos/` — 5 lockups: `logo_03` (dark petrol on white, default), `logo_00` (black), `logo_01` (white knockout), `logo_02` (lime), `logo_04` (deepest petrol).
- `assets/isologos/` — standalone "A" mark, same color variants.
- `assets/elementos/` — Solar / Eólico / Energía glyph badges, in lime/petrol/white/black/outline. Treat as filled illustrative badges (PNG, not vector) — not a stroke-icon system.
- For functional UI icons (arrows, chevrons, menu, close, etc.) not covered by the brand kit, use **Lucide** (1.5px stroke, 20–24px) — this is a substitution, not brand-provided.

## Reference components (`reference_components/`)
A marketing-site kit built on the tokens above: `Header.jsx`, `Hero.jsx`, `KPIStrip.jsx`, `Services.jsx`, `Footer.jsx`, plus shared atoms in `ui.js` (`Button`, `Eyebrow`, `Container`, `Tag`, `Halftone`, `Icon`). `index.html` shows them assembled and is viewable directly in a browser. Use these as the reference for how buttons, cards, section rhythm, and the halftone-wave motif should look — reimplement using the target app's component library and patterns rather than importing this JSX directly, unless the target really is an unstyled plain-React app.

## Applying this to a program
1. Drop `colors_and_type.css` and `fonts/` into the project; import the stylesheet once globally.
2. Re-theme existing components (buttons, cards, nav, inputs) to the tokens above — map the app's current color/spacing/radius variables to these, don't hardcode hex values inline.
3. Use `reference_components/` only as a visual/behavioral reference for any *new* marketing-style surfaces (landing, hero sections) the program might need.
4. Keep lime usage to a single accent per screen; petrol and white/off-white carry everything else.
