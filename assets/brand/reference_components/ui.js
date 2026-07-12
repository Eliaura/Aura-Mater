/* global React */
// Shared atoms for the Aura Energy marketing-site recreation kit.
// Plain JS (React.createElement) — not JSX — so it can be loaded with a
// normal <script src> instead of a Babel-transformed <script type="text/babel">.
(function () {
  const h = React.createElement;

  function Eyebrow({ children, tone = "petrol", style }) {
    const color = tone === "lime" ? "var(--aura-lime)"
                : tone === "white" ? "rgba(255,255,255,0.85)"
                : tone === "muted" ? "var(--fg-3)"
                : "var(--aura-petrol)";
    return h("div", {
      style: {
        fontFamily: "var(--font-eyebrow)",
        fontWeight: 500,
        textTransform: "uppercase",
        letterSpacing: "0.18em",
        fontSize: 12,
        color,
        ...style,
      },
    }, children);
  }

  function Button({ children, variant = "primary", size = "md", as = "button", href, onClick }) {
    const Comp = href ? "a" : as;
    const base = {
      fontFamily: "var(--font-eyebrow)",
      textTransform: "uppercase",
      letterSpacing: "0.14em",
      fontWeight: 500,
      fontSize: size === "sm" ? 11 : 12,
      padding: size === "sm" ? "10px 16px" : "14px 22px",
      border: "none",
      borderRadius: 999,
      cursor: "pointer",
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      textDecoration: "none",
      transition: "transform var(--dur-fast) var(--ease-out), filter var(--dur-fast) var(--ease-out), box-shadow var(--dur-fast) var(--ease-out)",
      whiteSpace: "nowrap",
    };
    const variants = {
      primary: { background: "var(--aura-petrol)", color: "#fff" },
      lime:    { background: "var(--aura-lime)",  color: "var(--petrol-900)" },
      ghost:   { background: "transparent", color: "var(--aura-petrol)", border: "1.5px solid var(--aura-petrol)", padding: size === "sm" ? "9px 15px" : "13px 21px" },
      ghostWhite: { background: "transparent", color: "#fff", border: "1.5px solid rgba(255,255,255,0.4)", padding: size === "sm" ? "9px 15px" : "13px 21px" },
    };
    return h(Comp, {
      href, onClick,
      style: { ...base, ...variants[variant] },
      onMouseEnter: (e) => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.filter = variant === "lime" ? "brightness(1.04)" : "brightness(1.06)"; },
      onMouseLeave: (e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.filter = "none"; },
    }, children);
  }

  function Container({ children, style, narrow }) {
    return h("div", {
      style: {
        maxWidth: narrow ? 980 : 1240,
        margin: "0 auto",
        padding: "0 32px",
        ...style,
      },
    }, children);
  }

  function Tag({ children, tone = "petrol" }) {
    const tones = {
      petrol: { color: "var(--aura-petrol)", border: "1px solid var(--aura-petrol)", background: "transparent" },
      lime:   { color: "var(--petrol-900)", background: "var(--aura-lime)", border: "1px solid var(--aura-lime)" },
      petrolFill: { color: "#fff", background: "var(--aura-petrol)", border: "1px solid var(--aura-petrol)" },
      muted:  { color: "var(--fg-3)", background: "var(--ink-050)", border: "1px solid var(--border-subtle)" },
    };
    return h("span", {
      style: {
        fontFamily: "var(--font-eyebrow)",
        textTransform: "uppercase",
        letterSpacing: "0.18em",
        fontSize: 10,
        padding: "5px 11px",
        borderRadius: 999,
        ...tones[tone],
      },
    }, children);
  }

  // Halftone wave — procedurally generated dot field, matches the brand motif.
  function Halftone({ tone = "light", style, rotate = 0, opacity = 1 }) {
    const color = tone === "light" ? "rgba(255,255,255,0.55)"
                : tone === "lime"  ? "rgba(216,240,136,0.85)"
                : tone === "petrol" ? "rgba(0,104,88,0.6)"
                : "rgba(0,104,88,0.18)";
    const cols = 60, rows = 14;
    const w = 1200, h2 = 280;
    const dots = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const x = (c / (cols - 1)) * w;
        const yBase = (r / (rows - 1)) * h2;
        const phase = (c / cols) * Math.PI * 2.2;
        const y = yBase + Math.sin(phase) * 30;
        const distFromCenter = Math.abs(r - rows / 2 - Math.sin(phase) * 2);
        const fade = Math.max(0, 1 - distFromCenter / (rows / 2));
        const rad = 0.5 + fade * 3.2;
        if (fade < 0.04) continue;
        dots.push(h("circle", { key: `${r}-${c}`, cx: x, cy: y, r: rad, fill: color, opacity: fade }));
      }
    }
    return h("svg", {
      viewBox: `0 0 ${w} ${h2}`,
      preserveAspectRatio: "none",
      style: { display: "block", width: "100%", height: "100%", transform: `rotate(${rotate}deg)`, opacity, pointerEvents: "none", ...style },
    }, dots);
  }

  // Lucide-style icon helper — inline SVG paths, no CDN load needed.
  function Icon({ name, size = 18, color = "currentColor", stroke = 1.5 }) {
    const paths = {
      "arrow-right": "M5 12h14M13 5l7 7-7 7",
      "chevron-down": "M6 9l6 6 6-6",
      "menu": "M3 12h18M3 6h18M3 18h18",
      "x": "M18 6L6 18M6 6l12 12",
      "map-pin": "M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z M12 13a3 3 0 100-6 3 3 0 000 6z",
      "play": "M5 3l14 9-14 9V3z",
      "external-link": "M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3",
      "phone": "M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z",
      "mail": "M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z M22 6l-10 7L2 6",
      "sun": "M12 17a5 5 0 100-10 5 5 0 000 10z M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42",
      "wind": "M9.59 4.59A2 2 0 1111 8H2m10.59 11.41A2 2 0 1014 16H2m15.73-8.27A2.5 2.5 0 1119.5 12H2",
      "zap": "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
    };
    return h("svg", {
      width: size, height: size, viewBox: "0 0 24 24", fill: "none",
      stroke: color, strokeWidth: stroke, strokeLinecap: "round", strokeLinejoin: "round",
      style: { flexShrink: 0 },
    }, h("path", { d: paths[name] || "" }));
  }

  window.AuraUI = { Eyebrow, Button, Container, Tag, Halftone, Icon };
})();
