# -*- coding: utf-8 -*-
"""Generador del reporte PDF con identidad visual de AURA Energy.
Arma un HTML autocontenido (fuentes/logo embebidos en base64, sin dependencias
externas en tiempo de render) y lo imprime a PDF con Chromium via Playwright.
"""
import base64
import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(BASE_DIR, "assets", "brand")


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


_FONT_SORA = None
_FONT_SWEET = None
_FONT_OPENSANS = None
_LOGO_PETROL = None


def _cargar_assets():
    global _FONT_SORA, _FONT_SWEET, _FONT_OPENSANS, _LOGO_PETROL
    if _FONT_SORA is None:
        _FONT_SORA = _b64(os.path.join(BRAND_DIR, "fonts", "Sora-Bold.otf"))
        _FONT_SWEET = _b64(os.path.join(BRAND_DIR, "fonts", "SweetSansProMedium.otf"))
        _FONT_OPENSANS = _b64(os.path.join(BRAND_DIR, "fonts", "OpenSans-VariableFont_wdth,wght.ttf"))
        _LOGO_PETROL = _b64(os.path.join(BRAND_DIR, "assets", "logos", "logo_03_cropped.png"))


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


def _mapa_ubicacion_png_b64(proyectos):
    """Mapa estatico (Plotly Scattergeo + kaleido) con la ubicacion de los proyectos
    seleccionados, para la portada del reporte. Sin depender de tiles/CDN externos."""
    import plotly.graph_objects as go
    con_coords = [p for p in proyectos if p.get("lat") is not None and p.get("lon") is not None]
    if not con_coords:
        return None
    fig = go.Figure(go.Scattergeo(
        lon=[p["lon"] for p in con_coords], lat=[p["lat"] for p in con_coords],
        text=[p["nombre"] for p in con_coords], mode="markers+text",
        marker=dict(size=11, color="#006858", line=dict(width=1, color="#ffffff")),
        textposition="top center",
        textfont=dict(family="Open Sans, sans-serif", size=12, color="#003a31"),
    ))
    geos = dict(scope="south america", showland=True, landcolor="#f2f4f3",
                showcountries=True, countrycolor="#c5ccca", countrywidth=1,
                showocean=True, oceancolor="#ffffff", showlakes=False, showrivers=False,
                resolution=50, showframe=False)
    if len(con_coords) > 1:
        geos["fitbounds"] = "locations"
    else:
        geos.update(center={"lat": -38, "lon": -65}, projection_scale=4)
    fig.update_geos(**geos)
    fig.update_layout(width=620, height=520, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="white")
    png_bytes = fig.to_image(format="png", scale=2)
    return base64.b64encode(png_bytes).decode("ascii")


def _svg_flujo(df_flujos, width=660, height=200):
    """Grafico de barras del flujo de caja operativo (FCF, años 1..plazo). El año 0 (CAPEX)
    queda afuera a proposito: mezclarlo aplasta la escala y esconde la variacion operativa
    (se muestra aparte como KPI 'CAPEX estimado')."""
    df_op = df_flujos[df_flujos["anio"] > 0]
    vals = df_op["fcf"].tolist()
    anios = df_op["anio"].tolist()
    n = len(vals)
    vmax, vmin = max(vals), min(vals)
    span = max(vmax - vmin, 1.0)
    pad_l, pad_r, pad_t, pad_b = 4, 4, 8, 20
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    gap = plot_w / n
    bar_w = max(gap * 0.62, 1.5)

    def y_of(v):
        return pad_t + (vmax - v) / span * plot_h

    zero_y = y_of(0)
    bars = []
    for i, (a, v) in enumerate(zip(anios, vals)):
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
    return (
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<line x1="{pad_l}" y1="{zero_y:.1f}" x2="{width-pad_r}" y2="{zero_y:.1f}" stroke="#c5ccca" stroke-width="1"/>'
        + "".join(bars) + "".join(labels) +
        "</svg>"
    )


def _tabla_flujo_html(df_flujos):
    filas = []
    for r in df_flujos.itertuples():
        clase = "neg" if r.fcf < 0 else ""
        filas.append(
            f'<tr class="{clase}"><td>{int(r.anio)}</td>'
            f'<td>{r.energia_mwh:,.0f}</td><td>{r.ingreso:,.0f}</td>'
            f'<td>{r.opex:,.0f}</td><td>{r.fcf:,.0f}</td></tr>'
        )
    return (
        '<table class="datos flujo"><thead><tr>'
        '<th>Año</th><th>Energía (MWh)</th><th>Ingreso (USD)</th>'
        '<th>OPEX (USD)</th><th>FCF (USD)</th></tr></thead><tbody>'
        + "".join(filas) + "</tbody></table>"
    )


def _css(fuentes):
    return f"""
@font-face {{ font-family:"Sora"; src:url(data:font/otf;base64,{fuentes['sora']}) format("opentype"); font-weight:700; }}
@font-face {{ font-family:"SweetSansPro"; src:url(data:font/otf;base64,{fuentes['sweet']}) format("opentype"); font-weight:500; }}
@font-face {{ font-family:"Open Sans"; src:url(data:font/ttf;base64,{fuentes['opensans']}) format("truetype-variations"); font-weight:300 800; }}

:root {{
  --aura-petrol:#006858; --aura-lime:#D8F088;
  --petrol-900:#003a31; --petrol-700:#006858; --petrol-200:#cfe6e0; --petrol-100:#e8f2ee; --petrol-050:#f3f8f6;
  --ink-900:#14181a; --ink-700:#2c3331; --ink-500:#5a6663; --ink-200:#c5ccca; --ink-100:#e6e9e8; --ink-050:#f2f4f3;
  --paper:#ffffff;
  --font-display:"Sora","Helvetica Neue",sans-serif;
  --font-eyebrow:"SweetSansPro","Sora",sans-serif;
  --font-body:"Open Sans",sans-serif;
}}
* {{ box-sizing:border-box; }}
@page {{ size:A4; margin:16mm 15mm 14mm 15mm; }}
body {{ font-family:var(--font-body); color:var(--ink-900); margin:0; font-size:12px; line-height:1.5; }}
h1,h2,h3 {{ font-family:var(--font-display); font-weight:700; margin:0; color:var(--ink-900); letter-spacing:-0.01em; }}
.eyebrow {{ font-family:var(--font-eyebrow); font-weight:500; text-transform:uppercase; letter-spacing:0.16em; font-size:10px; color:var(--aura-petrol); margin:0 0 8px; }}
.meta {{ font-family:var(--font-body); font-size:11px; color:var(--ink-500); }}
.pagebreak {{ page-break-before: always; }}
.tag {{ display:inline-block; font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.14em; font-size:9px;
  padding:3px 10px; border-radius:999px; border:1px solid var(--aura-petrol); color:var(--aura-petrol); }}
.tag.fill {{ background:var(--aura-petrol); color:#fff; border-color:var(--aura-petrol); }}

/* ---- Portada ---- */
.portada {{ page-break-after: always; }}
.portada .logo {{ height:34px; margin-bottom:64px; display:block; }}
.portada h1 {{ font-size:38px; line-height:1.08; max-width:480px; margin-bottom:14px; }}
.portada .sub {{ font-size:13px; color:var(--ink-500); max-width:440px; margin-bottom:36px; }}
.metodologia {{ margin-top:28px; padding-top:18px; border-top:1px solid var(--ink-100); max-width:520px; }}
.metodologia .eyebrow {{ margin-bottom:10px; }}
.metodologia p {{ font-size:10.5px; color:var(--ink-700); line-height:1.6; margin:0 0 8px; }}
.confidencial {{ margin-top:24px; padding-top:14px; border-top:1px solid var(--ink-100); font-size:9.5px; color:var(--ink-500); }}

/* ---- Mapa + supuestos en la portada ---- */
.portada-grid {{ display:flex; gap:28px; align-items:flex-start; margin-top:28px; }}
.portada-mapa {{ flex:0 0 240px; }}
.portada-mapa img {{ width:100%; border-radius:8px; border:1px solid var(--ink-100); display:block; }}
.portada-supuestos {{ flex:1; }}
table.supuestos-cover td {{ padding:5px 0; border-bottom:1px solid var(--ink-050); font-size:10.5px; }}
table.supuestos-cover td:first-child {{ color:var(--ink-500); width:55%; }}
table.supuestos-cover td:last-child {{ font-weight:600; color:var(--ink-900); }}

/* ---- Tabla comparativa portada ---- */
table.comparativa {{ width:100%; border-collapse:collapse; font-size:10.5px; margin-top:8px; }}
table.comparativa th {{ text-align:left; font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.08em;
  font-size:8.5px; color:var(--ink-500); padding:6px 8px; border-bottom:1.5px solid var(--ink-900); white-space:nowrap; }}
table.comparativa td {{ padding:7px 8px; border-bottom:1px solid var(--ink-100); }}
table.comparativa td.destacado {{ color:var(--aura-petrol); font-weight:700; }}
table.comparativa tr:last-child td {{ border-bottom:1.5px solid var(--ink-900); }}

/* ---- Pagina de proyecto ---- */
.proyecto-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px; }}
.proyecto-header h2 {{ font-size:24px; }}
.proyecto-meta {{ font-size:11px; color:var(--ink-500); margin-top:4px; }}
.proyecto-logo {{ height:16px; opacity:0.85; }}

.kpi-strip {{ display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin:22px 0 20px; }}
.kpi {{ border-left:2px solid var(--aura-petrol); padding-left:12px; }}
.kpi-label {{ font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.14em; font-size:8px; color:var(--ink-500); margin-bottom:6px; }}
.kpi-value {{ font-family:var(--font-display); font-weight:700; font-size:22px; color:var(--aura-petrol); line-height:1; }}

table.datos {{ width:100%; border-collapse:collapse; font-size:10.5px; margin-bottom:16px; }}
table.datos th {{ text-align:left; font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.06em;
  font-size:8px; color:var(--ink-500); padding:5px 8px; border-bottom:1px solid var(--ink-200); }}
table.datos td {{ padding:5px 8px; border-bottom:1px solid var(--ink-050); }}
table.datos.flujo td, table.datos.flujo th {{ text-align:right; }}
table.datos.flujo th:first-child, table.datos.flujo td:first-child {{ text-align:left; }}
table.datos.flujo tr.neg td {{ color:#B23A3A; }}

.seccion-titulo {{ font-family:var(--font-eyebrow); text-transform:uppercase; letter-spacing:0.14em; font-size:9.5px;
  color:var(--ink-900); border-bottom:1px solid var(--ink-200); padding-bottom:5px; margin:18px 0 10px; }}

.chart-wrap {{ margin-bottom:6px; }}

.footer {{ position:fixed; bottom:-8mm; left:0; right:0; font-size:8.5px; color:var(--ink-500);
  display:flex; justify-content:space-between; border-top:1px solid var(--ink-100); padding-top:6px; }}

.disclaimer {{ font-size:8.5px; color:var(--ink-500); margin-top:10px; }}
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
        ("IVA", "Considerado (recupero segun debito fiscal, maximo 3 años)" if fs.get("considerar_iva") else "Eficiente (sin efecto de caja)"),
    ]
    filas_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in filas)
    return f'<table class="datos supuestos-cover"><tbody>{filas_html}</tbody></table>'


def _tabla_comparativa_html(proyectos):
    filas = []
    campos = [
        ("Proyecto", lambda p: p["nombre"], False),
        ("Tecnología", lambda p: _tech_label(p["tech"]), False),
        ("Corredor", lambda p: p["corredor"], False),
        ("Potencia (MW)", lambda p: f'{p["cap"]:.0f}', False),
        ("VAN (USD)", lambda p: _fmt_money(p.get("van")), "van"),
        ("TIR", lambda p: _fmt_tir(p.get("tir")), "tir"),
        ("LCOE (USD/MWh)", lambda p: _fmt_lcoe(p.get("lcoe")), "lcoe_min"),
        ("Payback", lambda p: _fmt_payback(p.get("payback")), "payback_min"),
    ]
    mejor_van = max((p.get("van") for p in proyectos if p.get("van") is not None), default=None)
    mejor_tir = max((p.get("tir") for p in proyectos if p.get("tir") is not None), default=None)
    mejor_lcoe = min((p.get("lcoe") for p in proyectos if p.get("lcoe") is not None), default=None)
    mejor_payback = min((p.get("payback") for p in proyectos if p.get("payback") is not None), default=None)
    mejores = {"van": mejor_van, "tir": mejor_tir, "lcoe_min": mejor_lcoe, "payback_min": mejor_payback}

    hay_comparacion = len(proyectos) > 1
    head = "<tr>" + "".join(f"<th>{c[0]}</th>" for c in campos) + "</tr>"
    for p in proyectos:
        celdas = []
        for _, fmt, criterio in campos:
            destacado = ""
            if hay_comparacion and criterio and mejores.get(criterio) is not None:
                campo_val = {"van": p.get("van"), "tir": p.get("tir"), "lcoe_min": p.get("lcoe"), "payback_min": p.get("payback")}[criterio]
                if campo_val == mejores[criterio]:
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
        ("PAYBACK", _fmt_payback(p.get("payback"))),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-label">{k}</div><div class="kpi-value">{v}</div></div>'
        for k, v in kpis
    )
    datos_filas = [
        ("Recurso natural", _recurso_label(p)),
        ("Factor de planta estimado", _fmt_fc(p.get("fc_fin"))),
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
        chart_html = f'<div class="chart-wrap">{_svg_flujo(df_flujos)}</div>'
        tabla_flujo = _tabla_flujo_html(df_flujos)

    return f"""
<section class="proyecto pagebreak">
  <div class="proyecto-header">
    <div>
      <span class="tag fill">{tag_tech}</span>
      <h2 style="margin-top:8px">{p['nombre']}</h2>
      <div class="proyecto-meta">{p['corredor']} &nbsp;·&nbsp; {p['tension']:.1f} kV &nbsp;·&nbsp; {p['cap']:.0f} MW</div>
    </div>
    <img class="proyecto-logo" src="data:image/png;base64,{logo_b64}">
  </div>

  <div class="kpi-strip">{kpi_html}</div>

  <div class="seccion-titulo">Supuestos y generación</div>
  {tabla_datos}

  <div class="seccion-titulo">Flujo de caja proyectado</div>
  {chart_html}
  {tabla_flujo}

  <p class="disclaimer">Estimación preliminar a fines de evaluación. Factor de planta calibrado con datos propios de
  AURA Energy; CAPEX, OPEX y precio de energía son supuestos editables, no un presupuesto cerrado. No constituye
  una oferta ni un compromiso de inversión.</p>
</section>
"""


def generar_html_reporte(proyectos):
    """proyectos: lista de dicts (mismo formato que st.session_state['seleccion_nodos'].values()),
    cada uno debe incluir '_df_flujos' (DataFrame ya calculado) para poder graficar el flujo."""
    _cargar_assets()
    fuentes = {"sora": _FONT_SORA, "sweet": _FONT_SWEET, "opensans": _FONT_OPENSANS}
    fecha = datetime.date.today().strftime("%d/%m/%Y")
    n = len(proyectos)
    titulo = proyectos[0]["nombre"] if n == 1 else f"Cartera de {n} proyectos"
    mapa_b64 = _mapa_ubicacion_png_b64(proyectos)

    portada = f"""
<section class="portada">
  <img class="logo" src="data:image/png;base64,{_LOGO_PETROL}">
  <div class="eyebrow">REPORTE DE EVALUACIÓN · CONFIDENCIAL</div>
  <h1>{titulo}</h1>
  <div class="sub">Evaluación financiera preliminar de oportunidades de desarrollo solar y eólico,
  generada el {fecha}.</div>
  {_tabla_comparativa_html(proyectos)}
  <div class="portada-grid">
    <div class="portada-mapa">{f'<img src="data:image/png;base64,{mapa_b64}">' if mapa_b64 else ''}</div>
    <div class="portada-supuestos">
      <div class="eyebrow">Supuestos financieros considerados</div>
      {_tabla_supuestos_html(proyectos)}
    </div>
  </div>
  <div class="metodologia">
    <div class="eyebrow">Metodología</div>
    <p>El factor de planta de cada proyecto surge de una calibración propia de AURA Energy con datos
    de operación real y de irradiancia satelital (NASA POWER), aplicada a la ubicación exacta de cada
    nodo. El flujo de fondos se proyecta a valores constantes con impuesto a las ganancias (35%),
    amortización lineal del CAPEX y degradación anual del activo, descontado a la tasa indicada en cada
    ficha.</p>
  </div>
  <div class="confidencial">AURA Energy Solutions · Este documento es confidencial y fue preparado
  exclusivamente para la contraparte destinataria. Prohibida su redistribución sin autorización.</div>
</section>
"""
    paginas = "".join(_pagina_proyecto_html(p, _LOGO_PETROL) for p in proyectos)

    return f"""<!DOCTYPE html>
<html lang="es-AR"><head><meta charset="utf-8"><style>{_css(fuentes)}</style></head>
<body>{portada}{paginas}</body></html>"""


def generar_pdf_bytes(html):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        pdf_bytes = page.pdf(format="A4", print_background=True,
                              margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
        browser.close()
    return pdf_bytes
