# Metodología de valuación — Desarrollo de proyectos solares/eólicos (AURA Energy)

Contexto: AURA vende **desarrollo** (llevar un proyecto a "ready to build"), no construcción.
El objetivo de este documento es fijar cómo calcular (1) el flujo de fondos del proyecto
construido y (2) cuánto puede cobrar AURA por el desarrollo en sí.

---

## 1. Flujo de fondos del proyecto (VAN, TIR, LCOE)

### Inputs típicos
- Capacidad (MW), Factor de Planta (FP)
- Precio de energía (USD/MWh) — PPA o supuesto de mercado/MATER
- CAPEX (USD) — asumir 100% desembolsado en Año 0 salvo que se indique cronograma de obra
- OPEX anual (USD) — fijo en USD salvo indicación de escalación
- Tasa de descuento (hurdle rate del comprador, no la de AURA)
- Vida útil (típico 30 años)
- Degradación: año 1→2 ~1% (LID), luego ~0,4%/año
- Impuesto a las Ganancias 35%, amortización lineal del CAPEX a 15 años
- IVA: se asume neutro en caja (crédito fiscal 100% recuperable); ingresos/costos modelados netos de IVA. Si se quiere modelar la demora real de recupero del crédito fiscal del CAPEX, avisar — tiene impacto de caja real en los primeros años.
- Ingresos Brutos: generalmente no aplica en este tipo de proyecto (confirmar caso a caso)
- Financiamiento: default 100% equity (TIR de proyecto, sin apalancamiento) salvo que se pida TIR de accionista con deuda

### Cálculo
```
Generación_t = Capacidad_MW × 8760h × FP × (1 - degradación acumulada)
Ingresos_t   = Generación_t × Precio_energía
Amortización_t = CAPEX / años_amortización   (0 después del año de amortización)
EBT_t        = Ingresos_t - OPEX_t - Amortización_t
Impuesto_t   = MAX(EBT_t, 0) × 35%
Utilidad_Neta_t = EBT_t - Impuesto_t
FCF_t        = Utilidad_Neta_t + Amortización_t     (add-back, no cash)
FCF_0        = -CAPEX
VAN          = NPV(tasa_descuento, FCF_0..FCF_n)
TIR          = IRR(FCF_0..FCF_n)
```

### LCOE
```
LCOE = (CAPEX + NPV(tasa, OPEX_1..n)) / NPV(tasa, Generación_1..n)     [USD/MWh]
```
Es el costo "puro" del activo (sin impuesto a las ganancias), útil para comparar contra el
precio de venta de energía o contra otros proyectos — no reemplaza al VAN/TIR para decisiones
de inversión, que sí deben reflejar el efecto fiscal completo.

### Ejemplo de referencia (usado en conversación)
| Escenario | CAPEX | FP | VAN @9% | TIR | LCOE |
|---|---|---|---|---|---|
| A | USD 20MM | 25% | -USD 1.780.325 | 7,88% | USD 49,81/MWh |
| B | USD 18MM | 27% | +USD 1.080.286 | 9,73% | USD 38,66/MWh |

---

## 2. Cuánto puede cobrar AURA por el desarrollo (el fee)

### Idea central
El VAN del proyecto (calculado a la tasa del comprador) **no es el fee de desarrollo**.
Es el excedente que le queda al comprador *después* de exigirse su retorno mínimo. Si AURA
cobra el 100% de ese VAN como fee, el comprador termina invirtiendo su capital para ganar
exactamente su tasa de piso — sin ningún margen por el riesgo real que sigue asumiendo
(construcción, EPC, puesta en marcha, generación real vs. proyectada). Ningún comprador
racional acepta eso.

### Regla de sensibilidad (fee → TIR remanente del comprador)
Si el fee se capitaliza como mayor CAPEX (amortizable a 15 años junto con el resto):
```
CAPEX_total_comprador = CAPEX_construcción + Fee_desarrollo
Recalcular VAN/TIR del punto 1 con CAPEX_total_comprador
```
Esto muestra cuánto cae la TIR del comprador según el fee cobrado — es la base para negociar
el rango de precio (ver ejemplo numérico abajo).

### Dos escenarios de poder de negociación

**A) Con exclusividad de nodo / prioridad de despacho**
El comprador no tiene alternativa equivalente — es este proyecto o ninguno en ese lugar.
AURA puede capturar una porción mucho mayor del VAN, dejando solo el margen mínimo
indispensable por el riesgo de ejecución que sigue siendo del comprador.
→ **Captura estimada: 60–80% del VAN**

**B) Sin exclusividad (replicable por el comprador o por otro desarrollador)**
La referencia de precio es el costo evitado: tiempo, riesgo de rechazo en RENPER/Cammesa,
gestión, costo de oportunidad — no el VAN completo.
→ **Captura estimada: 15–25% del VAN**

### Ejemplo numérico (Escenario B del punto 1: CAPEX 18MM, FP 27%, VAN=1,08MM)
| Fee desarrollo | Captura % VAN | Contexto |
|---|---|---|
| USD 200-300k | ~20-30% | sin exclusividad — deja TIR remanente ~9,5-9,6% |
| USD 650-870k | ~60-80% | con exclusividad de nodo |
| USD 1.080.000 | 100% | ⚠️ deja al comprador en TIR ≈ piso (9,17%), sin margen por riesgo — no vendible |

### Advertencia sobre la tasa de descuento
Todo lo anterior depende de la tasa de descuento asumida (la del comprador, no la de AURA).
AURA no conoce con certeza la tasa que el comprador va a exigir — sesgo clásico del
desarrollador es sobrevaluar su propio proyecto usando una tasa optimista. Mitigantes:
1. Correr el modelo a varias tasas (9%, 11%, 13%, 15%) para obtener un rango, no un número único.
2. Anclar también en comparables de mercado (USD/MW de transacciones reales) como check
   independiente del DCF.
3. Preferir estructuras variables (SPV 90/10, earn-outs atados a hitos como RENPER o COD)
   sobre un fee fijo cerrado con una sola tasa asumida — protege a AURA de haberse
   equivocado en la tasa, en cualquier dirección.

---

## 3. Tratamiento de IVA (parametrizable — pendiente de implementar en el programa)

### Concepto
El IVA no impacta el EBT ni el impuesto a las ganancias — es un ítem de caja/balance, no de
resultado. El único efecto real es de **timing**: el CAPEX se paga con 21% de IVA adicional
(crédito fiscal), y ese crédito se recupera progresivamente compensando el IVA débito fiscal
generado por la venta de energía. Mientras dura el recupero, esa plata está inmovilizada —
es un costo financiero, no impositivo.

**Simplificación adoptada** (a refinar más adelante si hace falta mayor precisión): el crédito
fiscal de IVA se recupera en partes iguales a lo largo de N años (parametrizable: 1, 2 o 3),
como un ingreso de caja adicional en esos años. No se modela la mecánica exacta de netear
contra el débito fiscal real de cada período — es una aproximación.

### Toggle: `considerar_iva` (boolean)
- **IVA eficiente (`considerar_iva = False`)** — default actual del modelo. No se agrega
  ningún efecto de IVA al flujo de fondos (se asume que otro negocio del comprador absorbe el
  crédito fiscal sin problema financiero — ej. empresa con IVA débito fiscal alto por otras
  operaciones). Es el comportamiento que el modelo ya tiene hoy.
- **Considerar IVA (`considerar_iva = True`)** — agrega el efecto financiero del recupero.

### Fórmulas (cuando `considerar_iva = True`)
```
tasa_iva        = 21%                      (input, editable)
n_recupero       = 1, 2 o 3 años            (input, editable — selector)
IVA_credito_capex = CAPEX × tasa_iva

FCF_0 = -CAPEX - IVA_credito_capex          (se paga el IVA junto con el CAPEX, año 0)

Recupero_IVA_t = IVA_credito_capex / n_recupero   para t = 1..n_recupero
Recupero_IVA_t = 0                                para t > n_recupero

FCF_t = Utilidad_Neta_t + Amortización_t + Recupero_IVA_t     (t = 1..vida_útil)
```
El resto del modelo (EBT, impuesto a las ganancias, amortización) **no cambia** — el IVA no
entra en esas líneas.

### Sensibilidad de referencia (Escenario B: CAPEX 18MM, FP 27%, resto de supuestos igual)
| Modo | VAN @9% | TIR |
|---|---|---|
| IVA eficiente (no considerar) | USD 1.080.286 | 9,73% |
| Considerar IVA, recupero 1 año | USD 768.176 | 9,50% |
| Considerar IVA, recupero 2 años | USD 625.006 | 9,40% |
| Considerar IVA, recupero 3 años | USD 489.717 | 9,31% |

### Implementación sugerida (UI/Excel)
- Un switch/checkbox "Considerar IVA" (default: apagado = IVA eficiente)
- Si está activado, un selector de plazo de recupero (1 / 2 / 3 años)
- La tasa de IVA (21%) queda como input editable por si cambia
- Todo lo demás del modelo (generación, ingresos, OPEX, amortización, impuesto a las
  ganancias, VAN, TIR, LCOE) se recalcula igual que hoy, solo se le suma el efecto de caja
  descripto arriba a las filas de FCF cuando el switch está activado

---

## 4. Checklist de inputs a confirmar antes de correr el modelo para un proyecto real
- [ ] Precio de energía (PPA firmado o supuesto — y a qué tasa lo indexa, si aplica)
- [ ] CAPEX definitivo y cronograma de desembolso (100% año 0 vs. distribuido en obra)
- [ ] Tasa de descuento a usar — ¿la del comprador real, o rango de sensibilidad?
- [ ] ¿Hay exclusividad de nodo / prioridad de despacho confirmada, o es replicable?
- [ ] Estructura de fee: fijo vs. variable/earn-out vs. SPV 90/10
- [ ] Estado de madurez del desarrollo (afecta tanto el % de captura como el riesgo residual
      que asume el comprador)
