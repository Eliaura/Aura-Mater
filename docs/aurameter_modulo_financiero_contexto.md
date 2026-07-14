# Aurameter — Módulo Financiero: Contexto para desarrollo

## Sobre la app

Aurameter es una app interna (actualmente en Streamlit) que Aura usa para evaluar oportunidades de proyectos renovables (solar, eólico, BESS) en Argentina. Ya tiene módulos de recurso solar/eólico y prospección (este último en desarrollo por Facu, aparte). Este documento cubre el **módulo financiero**, que se suma a lo existente.

**Split de arquitectura decidido:**
- **Streamlit (motor interno):** sigue siendo la herramienta de trabajo diario — cálculos, comparador, sliders. Funciona bien, no se toca la estética, solo se le sigue agregando funcionalidad.
- **Capa de exportación (cara al cliente):** todo lo que se le muestra a inversores/compradores (PDF one-pager, gráficos) necesita identidad visual completa de marca (logo, paleta de colores, tipografía de Aura). Puede resolverse como plantilla HTML/CSS que el motor de Streamlit alimenta con datos y convierte a PDF — no requiere migrar toda la app.
- Decisión: no migrar todo a HTML de una. Empezar por la capa de presentación/exportable, dejando el motor de cálculo en Python/Streamlit.

## Objetivo del módulo financiero

Mostrar a inversores, para cada proyecto de la cartera, si conviene desarrollarlo: caja esperada, rentabilidad (TIR), VAN, LCOE — de forma simplificada, sin volverse una simulación pesada. El cálculo es liviano (aritmética financiera estándar sobre 20-30 flujos anuales), no hay problema de performance.

## Inputs editables (dashboard, vía sliders)

- **Tasa de descuento**
- **CAPEX** ($/MW)
- **OPEX** ($/MW/año o % del CAPEX)
- **Precio de venta de energía** ($/MWh)
- **Plazo del proyecto:** default 30 años, editable a 20 o 25
- **Amortización:** default 15 años, editable a 10 o 20 (parámetro independiente del plazo del proyecto — afecta tratamiento contable/fiscal del CAPEX, no el flujo de caja completo)

## Fijo por default (motor interno, no editable en el dashboard)

- **Factor de capacidad (FC):** sale de una tabla de referencia por zona/tecnología, calibrada con datos propios (ver abajo). No se expone en la UI ni en el exportable — es interno, para que el cálculo sea lo más preciso posible. La distinción "operado real vs. estimado" se comunica verbalmente en persona con el inversor, nunca en pantalla ni en el PDF (evitar que suene a marketing vacío).
- **Degradación anual:** fija por tecnología (ej. ~-0.5%/año en solar). No editable.

## Tabla de referencia de FC (calibración propia)

### Eólico — datos de operación real (no estimados, ya sintonizados)

| Proyecto | Zona | FC operado real |
|---|---|---|
| Jaramillo | Patagonia (Santa Cruz) | 55% |
| Bahía Blanca | Buenos Aires (costa) | 52% |
| Olavarría | Buenos Aires (centro) | 50% |
| Mar del Plata | Buenos Aires (costa) | 49% |
| Vieytes / Verónica | Buenos Aires (norte) | 42% |
| Nogolí | San Luis (Cuyo) | 40% |

Gradiente coherente: Patagonia > costa bonaerense > centro > Cuyo.

**Nota de implementación (2026-07, v3 — versión vigente):** metodología completa en
`aurameter_velocidad_fc_eolico.md` (leer ese doc antes de tocar esto de nuevo). Dos intentos
previos quedaron descartados:
- v1 mapeaba estas anclas a la columna `corredor` del dataset, pero eso es demasiado grosero — el
  corredor `CENTRO`, por ejemplo, agrupa tanto San Luis como nodos de Córdoba (viento bien
  distinto) bajo la misma etiqueta.
- v2 usaba una curva potencial `FC = A × viento^N` ajustada por regresión log-log sobre los
  vientos SIN normalizar por altura de buje (cada proyecto real mide a una altura distinta,
  85-130m) y con datos de Vivoratá que no correspondían a esta tabla.

La versión vigente normaliza el viento de cada ancla real a 100 m (ley de potencia, exponente
0.14) para que sea comparable con la columna `viento` del dataset (que ya viene a 100m, Global
Wind Atlas): Jaramillo 10.74 m/s, Bahía Blanca 9.16, Olavarría 8.48, Mar del Plata 8.19, Vieytes
7.80, Nogolí 8.02. El ratio FC/viento³ NO es constante (la turbina satura en potencia nominal a
partir de cierto viento) — se usa una curva partida: por debajo de ~8.40 m/s (donde la fórmula
cúbica cruza el 50% de Olavarría), `FC = ratio_promedio × viento³` con el ratio promediado sobre
Olavarría/Mar del Plata/Vieytes/Nogolí (~0.00084, la banda de mejor consistencia de datos); por
encima de eso (tipo Patagonia/costa alta) se interpola directo entre Olavarría→Bahía Blanca→
Jaramillo en vez de extrapolar la cúbica (que sobreestimaría). Precisión priorizada en ≥7.5 m/s
(zona económicamente ejecutable en Argentina); por debajo de eso el viento no da retorno viable
de todos modos, así que la imprecisión ahí no cambia ninguna decisión real.

Nota clave: en eólica, el FC **calculado** (informes tipo SMEC/Mott MacDonald) suele sobreestimar 2-3% respecto al FC **operado real**. Los valores de la tabla de arriba ya son reales de campo, no requieren ajuste. Para proyectos nuevos sin dato de operación, aplicar ese ajuste a la baja sobre el valor calculado.

Las pérdidas eólicas de referencia (Mott MacDonald, turbina Vestas V162) son **contractuales** (garantía técnica), no una simple estimación:

- Disponibilidad — WTG: 0.970, Balance of Plant: 0.997, Red: 0.992
- WTG Performance — curva de potencia: 0.985, sub-óptimo: 0.995, histéresis: 0.999
- Ambiental — degradación no-icing: 0.995, degradación por icing: 1.000
- Eléctrico — transmisión: 0.985
- Curtailment (temperatura, sombras/hielo, gestión de sector de viento, capacidad de exportación, ambiental, precios negativos): mayormente 1.000, temperatura 0.990
- **Total losses: 0.912**
- Fuente: Mott MacDonald

### Solar — FC calculado vs. operado

| Proyecto | Zona | FC calculado | FC operado |
|---|---|---|---|
| Negocio | — | 28.6% | ~31% |
| Catamarca (Alumbrera-Bracho) | NOA | 35% | (probablemente mayor, sin confirmar) |

**Nota de implementación (2026-07, v2 — versión vigente):** metodología completa en
`aurameter_ghi_fc_solar.md` (leer ese doc antes de tocar esto de nuevo). Anclas: Nogolí/San Luis
(GHI 1975, FC 29.5% chequeado) y PS La Aconquija (GHI 2390, FC 35% calculado por consultora de
primera línea — coincide con la fila "Catamarca (Alumbrera-Bracho)" de arriba, y es un proyecto
DISTINTO del Nogolí eólico aunque comparta nombre de referencia). El ratio FC/GHI es
prácticamente constante entre ambos sitios (~1.46-1.49%) — a diferencia del caso eólico, la
energía solar es aprox. proporcional a la irradiancia incidente, sin efecto de saturación por
curva de potencia. Por eso la fórmula es **FC = GHI × k** (proporcional, sin ordenada al origen),
con k = promedio de ambos ratios (~0.0148), no una recta con intercept. Un intento previo asumió
que estas dos referencias eran con estructura fija y les sumó un uplift de tracker — eso estaba
mal (ya son valores con tracker) e inflaba el FC, se descartó. La ancla de Misiones (28.6%/~31%,
simulada por Facu para 3 plantas) queda fuera del ajuste por tener menor confianza que las dos
anclas nuevas, pero sigue siendo una referencia razonable de sanity-check.

Las pérdidas solares (PS Aconquija) son **estimadas por especialistas** — buena referencia técnica, aunque con más margen que el caso eólico contractual:

- Sombras lejanas: 1.3%, sombras cercanas: 1.2%
- Angulares y espectrales: 0.8%, polvo y suciedad: 2.0%
- Nivel de irradiancia: 0.2%, temperatura: 3.2%
- Calidad de módulos: -0.4%, LID: 1.0%
- Mismatch: 0.9%, mismatch parte posterior: 0.4%
- Cableado CC: 1.0%, eficiencia del inversor: 1.3%, clipping en el inversor: 4.3%
- Cableado CA: 0.7%, transformador BT-MT: 0.9%, cableado MT: 0.5%, auxiliares: 0.5%
- **PR de diseño: 81.9%**
- Indisponibilidad adicional (BoP, evacuación subestación, evacuación red nacional): 1.0% total
- Fuente: cálculo propio, PS Aconquija

### Cómo se usa esta tabla

- Para un proyecto con dato de operación real disponible: usar ese valor directo.
- Para un proyecto nuevo sin dato propio: interpolar por zona más cercana en la tabla de referencia.
- El detalle de pérdidas (tablas de arriba) queda documentado como metodología/trazabilidad interna, para poder rechequear la referencia en cualquier momento — no se muestra en el exportable al cliente.

## Funcionalidades del módulo

1. **Dashboard con sliders** — inputs editables de la lista de arriba, resultado de TIR/VAN/LCOE en tiempo real. La sensibilidad (ej. "¿qué pasa si baja el precio de energía 10%?") sale gratis de esta misma interacción, no requiere un módulo aparte.
2. **Comparador multi-proyecto** — estilo páginas de comparación de productos (ej. Apple): columnas por proyecto, filas por métrica (CAPEX/MW, TIR, VAN, LCOE, plazo, tecnología), destacando visualmente el mejor valor de cada fila. Pensado para 2-4 proyectos en paralelo.
3. **Exportable (one-pager PDF)** — por proyecto, con identidad visual de Aura: recurso, CAPEX, TIR, VAN, LCOE, plazo, amortización. Sin mención de fuente del FC (real vs. estimado) — solo resultados limpios.

## Explícitamente fuera de scope (por ahora)

- Simulador de modelos de venta de energía (PPA fijo vs. spot vs. contrato con exportador) — buena idea pero para una herramienta aparte, complejizaría demasiado este módulo.
- Cualquier indicador visible en la UI o el PDF que distinga "FC operado real" vs. "FC estimado" — esa distinción es un activo comercial que se comunica en persona, no un feature de la app.
- Módulo de prospección — lo está armando Facu por separado, no es parte de este alcance.
- Tracker regulatorio/CAMMESA y sección de testimonios/track record — no aplican a este módulo.

## Cálculo financiero (lógica)

Por año, desde año 1 hasta el plazo elegido (20/25/30):

1. Energía anual = Potencia (MW) × FC × 8760 h, ajustada por degradación acumulada
2. Ingreso anual = Energía × Precio de venta
3. Flujo neto anual = Ingreso − OPEX
4. Año 0 = −CAPEX total (Potencia × CAPEX/MW)
5. **VAN** = NPV(tasa de descuento, flujos)
6. **TIR** = IRR(flujos)
7. **LCOE** = (CAPEX + Σ OPEX descontado) / Σ energía descontada

La amortización (10/15/20 años, default 15) es un parámetro contable/fiscal independiente del plazo del proyecto — no altera el flujo de caja bruto, pero sí puede afectar el cálculo de impuestos si se modela esa capa (a definir con Claude Code si se incluye tratamiento impositivo en esta primera versión o no).
