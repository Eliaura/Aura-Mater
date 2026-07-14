# -*- coding: utf-8 -*-
"""Generador del reporte PDF con identidad visual de AURA Energy.
Arma un HTML autocontenido (fuentes/logo/badges embebidos en base64, sin
dependencias externas en tiempo de render) y lo imprime a PDF con Chromium
via Playwright.

Estructura del reporte:
  1. Caratula (marca, full-bleed, solar/eolico segun la cartera)
  2. Comparativa: tabla comparativa + mapa de ubicacion + supuestos financieros
     + metodologia + disclaimers (Ingresos Brutos, CAPEX/OPEX, Ref A)
  3. Una pagina por proyecto (no debe superar una pagina A4)
"""
import base64
import datetime
import functools
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(BASE_DIR, "assets", "brand")


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


_ASSETS = {}


def _cargar_assets():
    if _ASSETS:
        return
    _ASSETS["sora"] = _b64(os.path.join(BRAND_DIR, "fonts", "Sora-Bold.otf"))
    _ASSETS["sweet"] = _b64(os.path.join(BRAND_DIR, "fonts", "SweetSansProMedium.otf"))
    _ASSETS["opensans"] = _b64(os.path.join(BRAND_DIR, "fonts", "OpenSans-VariableFont_wdth,wght.ttf"))
    _ASSETS["logo_petrol"] = _b64(os.path.join(BRAND_DIR, "assets", "logos", "logo_03_cropped.png"))
    _ASSETS["logo_blanco"] = _b64(os.path.join(BRAND_DIR, "assets", "logos", "logo_01_cropped.png"))
    _ASSETS["badge_solar"] = _b64(os.path.join(BRAND_DIR, "assets", "elementos", "solar_blanco_cropped.png"))
    _ASSETS["badge_eolico"] = _b64(os.path.join(BRAND_DIR, "assets", "elementos", "eolico_blanco_cropped.png"))
    _ASSETS["badge_mixto"] = _b64(os.path.join(BRAND_DIR, "assets", "elementos", "energia_blanco_cropped.png"))


def _fmt_money(v):
    return f"${v:,.0f}" if v is not None else "N/D"


def _fmt_tir(v):
    return f"{v*100:.1f}%" if v is not None else "N/D"


def _fmt_lcoe(v):
    return f"${v:.1f}/MWh" if v is not None else "N/D"


def _fmt_fc(v):
    return f"{v*100:.2f}%" if v is not None else "N/D"


def _fmt_payback(v):
    return f"{v:.1f} años" if v is not None else "N/D"


def _fmt_gen(v):
    return f"{v:,.0f} MWh/MW/año" if v is not None else "N/D"


def _tech_label(tech):
    return "Solar fotovoltaico" if tech == "solar" else "Eólico"


def _recurso_label(p):
    return f'{p["rec"]:.1f} m/s (viento)' if p["tech"] == "eolica" else f'{p["rec"]:.0f} kWh/m²/año (GHI)'


def _recurso_corto(p):
    return f'{p["rec"]:.1f} m/s' if p["tech"] == "eolica" else f'{p["rec"]:.0f}'


# ================== HALFTONE (motivo de marca, ver ui.js del design handoff) ==================
def _halftone_svg(color="rgba(255,255,255,0.35)", width=1200, height=280, cols=60, rows=14):
    dots = []
    for r in range(rows):
        for c in range(cols):
            x = (c / (cols - 1)) * width
            y_base = (r / (rows - 1)) * height
            phase = (c / cols) * math.pi * 2.2
            y = y_base + math.sin(phase) * 30
            dist_from_center = abs(r - rows / 2 - math.sin(phase) * 2)
            fade = max(0.0, 1 - dist_from_center / (rows / 2))
            if fade < 0.04:
                continue
            rad = 0.5 + fade * 3.2
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.2f}" fill="{color}" opacity="{fade:.2f}"/>')
    return (f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
            f'style="display:block;width:100%;height:100%">' + "".join(dots) + "</svg>")


# ================== MAPA DE UBICACION (portada de la comparativa) ==================
def _mapa_ubicacion_png_b64(proyectos):
    """Mapa estatico (Plotly Scattergeo + kaleido), sin depender de tiles/CDN externos.
    Fuerza un area minima visible para que el contorno del pais se vea aunque los
    proyectos esten muy agrupados (si no, con fitbounds muy ajustado solo se ven los
    puntos sobre un fondo gris, sin referencia geografica)."""
    import plotly.graph_objects as go
    con_coords = [p for p in proyectos if p.get("lat") is not None and p.get("lon") is not None]
    if not con_coords:
        return None
    lats = [p["lat"] for p in con_coords]
    lons = [p["lon"] for p in con_coords]
    fig = go.Figure(go.Scattergeo(
        lon=lons, lat=lats,
        text=[p["nombre"] for p in con_coords], mode="markers+text",
        marker=dict(size=11, color="#006858", line=dict(width=1, color="#ffffff")),
        textposition="top center",
        textfont=dict(family="Open Sans, sans-serif", size=12, color="#003a31"),
    ))
    geos = dict(scope="south america", showland=True, landcolor="#f2f4f3",
                showcountries=True, countrycolor="#c5ccca", countrywidth=1,
                showsubunits=True, subunitcolor="#d9dedc", subunitwidth=0.7,
                showocean=True, oceancolor="#ffffff", showlakes=False, showrivers=False,
                resolution=50, showframe=False)
    # Area minima de +-4 grados alrededor del centro, para que siempre se vea contorno/pais
    lat_c, lon_c = sum(lats) / len(lats), sum(lons) / len(lons)
    lat_span = max(max(lats) - min(lats), 8.0)
    lon_span = max(max(lons) - min(lons), 8.0)
    pad = 1.4
    geos["lataxis_range"] = [lat_c - lat_span / 2 * pad, lat_c + lat_span / 2 * pad]
    geos["lonaxis_range"] = [lon_c - lon_span / 2 * pad, lon_c + lon_span / 2 * pad]
    fig.update_geos(**geos)
    fig.update_layout(width=620, height=520, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="white")
    png_bytes = fig.to_image(format="png", scale=2)
    return base64.b64encode(png_bytes).decode("ascii")


# ================== GRAFICO DE FLUJO DE CAJA ACUMULADO ==================
def _svg_flujo_acumulado(df_flujos, width=660, height=210):
    """Flujo de caja ACUMULADO: arranca en -CAPEX (año 0, para abajo) y sube a medida
    que se acumulan los FCF anuales. Resalta el año exacto de payback (cruce de cero:
    ahi termina de pagarse la inversion y el proyecto empieza a dejar ganancia neta)."""
    cum = df_flujos["fcf"].cumsum().tolist()
    anios = df_flujos["anio"].tolist()
    n = len(cum)
    vmax, vmin = max(cum), min(cum)
    span = max(vmax - vmin, 1.0)
    label_h = 16
    pad_l, pad_r, pad_t, pad_b = 6, 6, label_h + 6, 20
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    gap = plot_w / n
    bar_w = max(gap * 0.6, 1.2)

    def y_of(v):
        return pad_t + (vmax - v) / span * plot_h

    zero_y = y_of(0)
    payback_x, payback_anio = None, None
    for i in range(1, n):
        if cum[i - 1] < 0 <= cum[i]:
            delta = cum[i] - cum[i - 1]
            frac = (-cum[i - 1] / delta) if delta else 0.0
            payback_x = pad_l + (i - 1 + frac) * gap + gap / 2
            payback_anio = anios[i - 1] + frac
            break

    bars = []
    for i, (a, v) in enumerate(zip(anios, cum)):
        x = pad_l + i * gap + (gap - bar_w) / 2
        yv = y_of(v)
        top, h = (min(zero_y, yv), abs(yv - zero_y))
        color = "#006858" if v >= 0 else "#B23A3A"
        bars.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bar_w:.1f}" height="{max(h,0.6):.1f}" fill="{color}" rx="0.6"/>')

    labels = []
    step = 5 if n > 12 else 1
    for i, a in enumerate(anios):
        if a % step == 0:
            x = pad_l + i * gap + gap / 2
            labels.append(f'<text x="{x:.1f}" y="{height-4}" font-size="7.5" fill="#5a6663" text-anchor="middle" font-family="Open Sans, sans-serif">{a}</text>')

    payback_marker = ""
    if payback_x is not None:
        payback_marker = (
            f'<line x1="{payback_x:.1f}" y1="{pad_t}" x2="{payback_x:.1f}" y2="{height-pad_b}" '
            f'stroke="#9bb84e" stroke-width="1.5" stroke-dasharray="3,2"/>'
            f'<text x="{payback_x:.1f}" y="{label_h-2}" font-size="8.5" fill="#003a31" text-anchor="middle" '
            f'font-weight="700" font-family="Open Sans, sans-serif">Payback: {payback_anio:.1f} años</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<line x1="{pad_l}" y1="{zero_y:.1f}" x2="{width-pad_r}" y2="{zero_y:.1f}" stroke="#c5ccca" stroke-width="1"/>'
        + "".join(bars) + "".join(labels) + payback_marker +
        "</svg>"
    )


def _tabla_flujo_condensada_html(df_flujos, paso=5, hasta_anual=10):
    """Solo año / energia / ingresos / FCF (sin OPEX): todos los años del 1 al `hasta_anual`
    y de ahi en mas cada `paso` años, para que entre en una sola pagina - es tabla de
    respaldo, el grafico es el protagonista."""
    filas = []
    for r in df_flujos.itertuples():
        if r.anio > hasta_anual and r.anio % paso != 0:
            continue
        clase = "neg" if r.fcf < 0 else ""
        filas.append(
            f'<tr class="{clase}"><td>{int(r.anio)}</td>'
            f'<td>{r.energia_mwh:,.0f}</td><td>{r.ingreso:,.0f}</td><td>{r.fcf:,.0f}</td></tr>'
        )
    return (
        '<table class="datos flujo"><thead><tr>'
        '<th>Año</th><th>Energía (MWh)</th><th>Ingresos (USD)</th><th>FCF acumulable (USD)</th>'
        '</tr></thead><tbody>' + "".join(filas) + "</tbody></table>"
    )


def _css(f):
    return f"""
@font-face {{ font-family:"Sora"; src:url(data:font/otf;base64,{f['sora']}) format("opentype"); font-weight:700; }}
@font-face {{ font-family:"SweetSansPro"; src:url(data:font/otf;base64,{f['sweet']}) format("opentype"); font-weight:500; }}
@font-face {{ font-family:"Open Sans"; src:url(data:font/ttf;base64,{f['opensans']}) format("truetype-variations"); font-weight:300 800; }}

:root {{
  --aura-petrol:#006858; --aura-lime:#D8F088;
  --petrol-950:#002a23; --petrol-900:#003a31; --petrol-800:#004d40; --petrol-700:#006858;
  --petrol-200:#cfe6e0; --petrol-100:#e8f2ee; --petrol-050:#f3f8f6;
  --ink-900:#14181a; --ink-700:#2c3331; --ink-500:#5a6663; --ink-200:#c5ccca; --ink-100:#e6e9e8; --ink-050:#f2f4f3;
  --paper:#ffffff;
  --font-display:"Sora","Helvetica Neue",sans-serif;
  --font-eyebrow:"SweetSansPro","Sora",sans-serif;
  --font-body:"Open Sans",sans-serif;
}}
* {{ box-sizing:border-box; }}
@page {{ size:A4; margin:16mm 15mm 14mm 15mm; }}
body {{ font-family:var(--font-body); color:var(--ink-900); margin:0; font-size:11.5px; line-height:1.5; }}
h1,h2,h3 {{ font-family:var(--font-display); font-weight:700; margin:0; color:var(--ink-900); letter-spacing:-0.01em; }}
.eyebrow {{ font-family:var(--font-eyebrow); font-weight:500; text-transform:uppercase; letter-spacing:0.16em; font-size:10px; color:var(--aura-petrol); margin:0 0 8px; }}
.meta {{ font-family:var(--font-body); font-size:11px; color:var(--ink-500); }}
.pagebreak {{ page-break-before: always; }}
.tag {{ display:inline-block; font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.14em; font-size:9px;
  padding:3px 10px; border-radius:999px; border:1px solid var(--aura-petrol); color:var(--aura-petrol); }}
.tag.fill {{ background:var(--aura-petrol); color:#fff; border-color:var(--aura-petrol); }}

/* ---- Caratula: pagina full-bleed, se come los margenes de @page a proposito ---- */
.caratula {{
  page-break-after: always;
  margin: -16mm -15mm 0 -15mm;
  width: 210mm; height: 297mm; padding: 22mm 18mm;
  background: var(--petrol-900); color: #fff;
  position: relative; overflow: hidden;
}}
.caratula-halftone {{ position:absolute; top:56mm; left:0; width:100%; height:60mm; opacity:0.8; }}
.caratula-badge {{ position:absolute; right:-14mm; bottom:-8mm; width:130mm; opacity:0.30; }}
.caratula-badge img {{ width:100%; display:block; }}
.caratula-logo {{ height:30px; position:relative; z-index:2; }}
.caratula-body {{ position:relative; z-index:2; margin-top:90mm; }}
.caratula-body .eyebrow {{ color:var(--aura-lime); }}
.caratula-body h1 {{ color:#fff; font-size:40px; line-height:1.06; max-width:145mm; margin-bottom:16px; }}
.caratula-body .sub {{ font-size:13.5px; color:rgba(255,255,255,0.78); max-width:120mm; line-height:1.6; }}
.caratula-footer {{ position:absolute; left:18mm; bottom:14mm; right:18mm; z-index:2;
  display:flex; justify-content:space-between; align-items:center;
  border-top:1px solid rgba(255,255,255,0.2); padding-top:10px;
  font-size:9.5px; color:rgba(255,255,255,0.6); }}

/* ---- Comparativa ---- */
.comparativa-page h1 {{ font-size:26px; margin-bottom:4px; }}
.comparativa-page .sub {{ font-size:12px; color:var(--ink-500); margin-bottom:18px; }}
.seccion-titulo {{ font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.14em; font-size:9.5px;
  color:var(--ink-900); border-bottom:1px solid var(--ink-200); padding-bottom:5px; margin:20px 0 10px; }}

table.comparativa {{ width:100%; border-collapse:collapse; font-size:10px; margin-top:4px; }}
table.comparativa th {{ text-align:left; font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.06em;
  font-size:8px; color:var(--ink-500); padding:6px 7px; border-bottom:1.5px solid var(--ink-900); white-space:nowrap; }}
table.comparativa td {{ padding:7px 7px; border-bottom:1px solid var(--ink-100); }}
table.comparativa td.destacado {{ color:var(--aura-petrol); font-weight:700; }}
table.comparativa tr:last-child td {{ border-bottom:1.5px solid var(--ink-900); }}
table.comparativa td a {{ color:var(--aura-petrol); text-decoration:none; white-space:nowrap; }}

.portada-grid {{ display:flex; gap:26px; align-items:flex-start; margin-top:6px; }}
.portada-mapa {{ flex:0 0 230px; }}
.portada-mapa img {{ width:100%; border-radius:8px; border:1px solid var(--ink-100); display:block; }}
.portada-supuestos {{ flex:1; }}
table.supuestos-cover td {{ padding:5px 0; border-bottom:1px solid var(--ink-050); font-size:10.5px; }}
table.supuestos-cover td:first-child {{ color:var(--ink-500); width:55%; }}
table.supuestos-cover td:last-child {{ font-weight:600; color:var(--ink-900); }}

.disclaimers p {{ font-size:9.5px; color:var(--ink-700); line-height:1.6; margin:0 0 9px; }}
.disclaimers b {{ color:var(--ink-900); }}
.confidencial {{ margin-top:18px; padding-top:12px; border-top:1px solid var(--ink-100); font-size:9px; color:var(--ink-500); }}

/* ---- Pagina de proyecto (una sola pagina, compacta) ---- */
.proyecto-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:2px; }}
.proyecto-header h2 {{ font-size:22px; }}
.proyecto-meta {{ font-size:10.5px; color:var(--ink-500); margin-top:3px; }}
.proyecto-logo {{ height:14px; opacity:0.85; }}

.kpi-strip {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:16px 0 14px; }}
.kpi {{ border-left:2px solid var(--aura-petrol); padding-left:10px; }}
.kpi-label {{ font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.14em; font-size:7.5px; color:var(--ink-500); margin-bottom:5px; }}
.kpi-value {{ font-family:var(--font-display); font-weight:700; font-size:19px; color:var(--aura-petrol); line-height:1; }}

table.datos {{ width:100%; border-collapse:collapse; font-size:10px; margin-bottom:10px; }}
table.datos th {{ text-align:left; font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.06em;
  font-size:7.5px; color:var(--ink-500); padding:4px 7px; border-bottom:1px solid var(--ink-200); }}
table.datos td {{ padding:3.5px 7px; border-bottom:1px solid var(--ink-050); }}
table.datos.flujo td, table.datos.flujo th {{ text-align:right; }}
table.datos.flujo th:first-child, table.datos.flujo td:first-child {{ text-align:left; }}
table.datos.flujo tr.neg td {{ color:#B23A3A; }}

.chart-wrap {{ margin-bottom:2px; }}
.disclaimer {{ font-size:8px; color:var(--ink-500); margin-top:8px; line-height:1.5; }}
.refa-note {{ font-size:8.5px; color:#8a6d1a; background:#FBF3DA; border-radius:6px; padding:6px 9px; margin-top:8px; }}
"""


def _tabla_supuestos_html(proyectos):
    fs = next((p.get("fin_snapshot") for p in proyectos if p.get("fin_snapshot")), None)
    if not fs:
        return "<p class=\"meta\">Sin supuestos financieros registrados.</p>"
    filas = [
        ("Tasa de descuento", f'{fs["tasa"]*100:.1f}%'),
        ("CAPEX", f'${fs["capex_mw"]:,.0f}/MW'),
        ("OPEX", f'${fs["opex_mw"]:,.0f}/MW/año'),
        ("Precio de energía", f'${fs["precio_mwh"]:.0f}/MWh'),
        ("Plazo del proyecto", f'{fs["plazo"]} años'),
        ("Amortización", f'{fs["amortizacion"]} años'),
        ("IVA", "Considerado (recupero según débito fiscal, máximo 3 años)" if fs.get("considerar_iva") else "Eficiente (sin efecto de caja)"),
        ("Ingresos Brutos", "No aplica (ver disclaimer)"),
    ]
    filas_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in filas)
    return f'<table class="datos supuestos-cover"><tbody>{filas_html}</tbody></table>'


def _gmaps_link(p):
    if p.get("lat") is None or p.get("lon") is None:
        return "-"
    url = f"https://www.google.com/maps?q={p['lat']},{p['lon']}"
    return f'<a href="{url}" target="_blank">📍 Ver en mapa</a>'


def _tabla_comparativa_html(proyectos):
    campos = [
        ("Proyecto", lambda p: p["nombre"], None),
        ("Tecnología", lambda p: _tech_label(p["tech"]), None),
        ("Corredor", lambda p: p["corredor"], None),
        ("Ubicación", _gmaps_link, None),
        ("Potencia (MW)", lambda p: f'{p["cap"]:.0f}', None),
        ("GHI / Viento", _recurso_corto, None),
        ("FC recurso", lambda p: _fmt_fc(p.get("fc_bruto")), None),
        ("FC", lambda p: _fmt_fc(p.get("fc_fin")), "fc_max"),
        ("TIR", lambda p: _fmt_tir(p.get("tir")), "tir_max"),
        ("LCOE (USD/MWh)", lambda p: _fmt_lcoe(p.get("lcoe")), "lcoe_min"),
        ("Retorno de inversión", lambda p: _fmt_payback(p.get("payback")), "payback_min"),
    ]
    campo_valor = {
        "fc_max": lambda p: p.get("fc_fin"), "tir_max": lambda p: p.get("tir"),
        "lcoe_min": lambda p: p.get("lcoe"), "payback_min": lambda p: p.get("payback"),
    }
    mejores = {}
    for key, getter in campo_valor.items():
        vals = [getter(p) for p in proyectos if getter(p) is not None]
        if not vals:
            mejores[key] = None
        else:
            mejores[key] = max(vals) if key in ("fc_max", "tir_max") else min(vals)

    hay_comparacion = len(proyectos) > 1
    head = "<tr>" + "".join(f"<th>{c[0]}</th>" for c in campos) + "</tr>"
    filas = []
    for p in proyectos:
        celdas = []
        for _, fmt, criterio in campos:
            destacado = ""
            if hay_comparacion and criterio and mejores.get(criterio) is not None:
                if campo_valor[criterio](p) == mejores[criterio]:
                    destacado = ' class="destacado"'
            celdas.append(f"<td{destacado}>{fmt(p)}</td>")
        filas.append("<tr>" + "".join(celdas) + "</tr>")
    return f'<table class="comparativa"><thead>{head}</thead><tbody>{"".join(filas)}</tbody></table>'


def _pagina_proyecto_html(p, logo_b64):
    tag_tech = "SOLAR" if p["tech"] == "solar" else "EÓLICO"
    kpis = [
        ("VAN", _fmt_money(p.get("van"))),
        ("TIR", _fmt_tir(p.get("tir"))),
        ("LCOE", _fmt_lcoe(p.get("lcoe"))),
        ("RETORNO DE INVERSIÓN", _fmt_payback(p.get("payback"))),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-label">{k}</div><div class="kpi-value">{v}</div></div>'
        for k, v in kpis
    )
    fc_nota = " (sobre MWac inyectados a la red)" if p["tech"] == "solar" else ""
    ref_a = p.get("ref_a_dependiente")
    fc_recurso_fila = [("Factor de planta de recurso", _fmt_fc(p.get("fc_bruto")))] if ref_a else []
    datos_filas = [
        ("Recurso natural", _recurso_label(p)),
        *fc_recurso_fila,
        (f"Factor de planta estimado{fc_nota}", _fmt_fc(p.get("fc_fin"))),
        ("Generación específica", _fmt_gen(p.get("gen_especifica"))),
        ("CAPEX estimado", _fmt_money(p.get("capex_total"))),
        ("OPEX estimado (anual)", _fmt_money(p.get("opex_anual"))),
        ("Ingresos anuales (año 1)", _fmt_money(p.get("ingreso_anual"))),
    ]
    tabla_datos = "<table class=\"datos\"><tbody>" + "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in datos_filas
    ) + "</tbody></table>"

    chart_html = ""
    tabla_flujo = ""
    df_flujos = p.get("_df_flujos")
    if df_flujos is not None:
        chart_html = f'<div class="chart-wrap">{_svg_flujo_acumulado(df_flujos)}</div>'
        tabla_flujo = _tabla_flujo_condensada_html(df_flujos)

    refa_html = ""
    if ref_a:
        tir_mejora = p.get("tir_sin_curtailment")
        mejora_txt = (f' Sin ese descuento, la TIR estimada pasaría de {_fmt_tir(p.get("tir"))} a '
                      f'{_fmt_tir(tir_mejora)}.') if tir_mejora is not None else ""
        refa_html = ('<div class="refa-note"><b>Ref A:</b> este nodo depende de capacidad de despacho Ref A, que solo '
                     'garantiza 92% de disponibilidad. Se aplicó un descuento del 8% sobre la energía como caso '
                     f'conservador (el peor escenario) — en la práctica podría despacharse más energía que la modelada.{mejora_txt}</div>')

    return f"""
<section class="proyecto pagebreak">
  <div class="proyecto-header">
    <div>
      <span class="tag fill">{tag_tech}</span>
      <h2 style="margin-top:6px">{p['nombre']}</h2>
      <div class="proyecto-meta">{p['corredor']} &nbsp;·&nbsp; {p['tension']:.1f} kV &nbsp;·&nbsp; {p['cap']:.0f} MW</div>
    </div>
    <img class="proyecto-logo" src="data:image/png;base64,{logo_b64}">
  </div>

  <div class="kpi-strip">{kpi_html}</div>

  <div class="seccion-titulo">Supuestos y generación</div>
  {tabla_datos}

  <div class="seccion-titulo">Flujo de caja acumulado</div>
  {chart_html}
  {tabla_flujo}
  {refa_html}

  <p class="disclaimer">Estimación preliminar a fines de evaluación. Factor de planta calibrado con datos propios de
  AURA Energy; CAPEX, OPEX y precio de energía son supuestos editables, no un presupuesto cerrado. No constituye
  una oferta ni un compromiso de inversión.</p>
</section>
"""


def _badge_para(proyectos):
    techs = {p["tech"] for p in proyectos}
    if techs == {"solar"}:
        return _ASSETS["badge_solar"], "solar fotovoltaico"
    if techs == {"eolica"}:
        return _ASSETS["badge_eolico"], "eólico"
    return _ASSETS["badge_mixto"], "solar y eólico"


def generar_html_reporte(proyectos):
    """proyectos: lista de dicts (mismo formato que st.session_state['seleccion_nodos'].values()),
    cada uno debe incluir '_df_flujos' (DataFrame ya calculado) para poder graficar el flujo."""
    _cargar_assets()
    fecha = datetime.date.today().strftime("%d/%m/%Y")
    n = len(proyectos)
    titulo = proyectos[0]["nombre"] if n == 1 else f"Cartera de {n} proyectos"
    badge_b64, tech_palabra = _badge_para(proyectos)
    mapa_b64 = _mapa_ubicacion_png_b64(proyectos)
    hay_refa = any(p.get("ref_a_dependiente") for p in proyectos)

    caratula = f"""
<section class="caratula">
  <div class="caratula-halftone">{_halftone_svg()}</div>
  <div class="caratula-badge"><img src="data:image/png;base64,{badge_b64}"></div>
  <img class="caratula-logo" src="data:image/png;base64,{_ASSETS['logo_blanco']}">
  <div class="caratula-body">
    <div class="eyebrow">REPORTE DE EVALUACIÓN · CONFIDENCIAL</div>
    <h1>{titulo}</h1>
    <div class="sub">Evaluación financiera preliminar de oportunidades de desarrollo {tech_palabra}
    en Argentina, preparada por AURA Energy.</div>
  </div>
  <div class="caratula-footer"><span>AURA Energy</span><span>{fecha}</span></div>
</section>
"""

    refa_disclaimer = ""
    if hay_refa:
        refa_disclaimer = ('<p><b>Curtailment Ref A:</b> los proyectos marcados "Ref A" en sus fichas dependen de '
                            'capacidad de despacho Ref A, que solo garantiza 92% de disponibilidad. Se aplicó un '
                            'descuento del 8% sobre la energía como caso conservador (el peor escenario posible) — '
                            'en la práctica podría despacharse más energía que la modelada.</p>')

    comparativa = f"""
<section class="pagebreak comparativa-page">
  <div class="eyebrow">CARTERA EVALUADA</div>
  <h1>Comparativa de proyectos</h1>
  <div class="sub">Generado el {fecha} · {n} proyecto(s) seleccionado(s)</div>

  {_tabla_comparativa_html(proyectos)}

  <div class="seccion-titulo">Ubicación y supuestos financieros</div>
  <div class="portada-grid">
    <div class="portada-mapa">{f'<img src="data:image/png;base64,{mapa_b64}">' if mapa_b64 else ''}</div>
    <div class="portada-supuestos">{_tabla_supuestos_html(proyectos)}</div>
  </div>

  <div class="seccion-titulo">Metodología y alcance</div>
  <div class="disclaimers">
    <p>El factor de planta de cada proyecto surge de una calibración propia de AURA Energy con datos de operación
    real y de irradiancia satelital (NASA POWER), aplicada a la ubicación exacta de cada nodo. El flujo de fondos
    se proyecta a valores constantes con impuesto a las ganancias (35%), amortización lineal del CAPEX y
    degradación anual del activo, descontado a la tasa indicada arriba.</p>
    <p><b>CAPEX y OPEX:</b> estimados en base a proyectos comparables desarrollados por AURA. El CAPEX contempla
    equipo principal (paneles o aerogeneradores, inversores/transformadores, estructuras o torres, cableado),
    obra civil y electromecánica, ingeniería, permisos y conexión a red. El OPEX contempla operación y
    mantenimiento: salarios, mantenimiento correctivo, limpieza de paneles o servicio de aerogeneradores,
    repuestos, administración, vigilancia y canon de conexión. No son presupuestos cerrados para un sitio
    puntual.</p>
    <p><b>Ingresos Brutos:</b> no se modela este impuesto provincial. Los proyectos de generación a partir de
    fuentes renovables adheridos a la Ley 27.191 (Régimen de Fomento Nacional para el uso de Fuentes Renovables
    de Energía) están exentos en las jurisdicciones que adhirieron al régimen.</p>
    {refa_disclaimer}
  </div>

  <div class="confidencial">AURA Energy · Este documento es confidencial y fue preparado exclusivamente
  para la contraparte destinataria. Prohibida su redistribución sin autorización. Estimación preliminar, no
  constituye una oferta ni un compromiso de inversión.</div>
</section>
"""

    paginas = "".join(_pagina_proyecto_html(p, _ASSETS["logo_petrol"]) for p in proyectos)

    return f"""<!DOCTYPE html>
<html lang="es-AR"><head><meta charset="utf-8"><style>{_css(_ASSETS)}</style></head>
<body>{caratula}{comparativa}{paginas}</body></html>"""


@functools.lru_cache(maxsize=1)
def _instalar_chromium():
    """Streamlit Community Cloud solo corre `pip install -r requirements.txt` en el build,
    no el `playwright install chromium` que baja el binario del navegador. Se instala en el
    primer uso (una sola vez por contenedor, cacheado) en vez de en cada arranque de la app."""
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"],
                   check=False, capture_output=True, timeout=300)
    return True


def generar_pdf_bytes(html):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            _instalar_chromium()
            browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        pdf_bytes = page.pdf(format="A4", print_background=True,
                              margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
        browser.close()
    return pdf_bytes
