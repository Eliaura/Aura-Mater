# Aurameter — Relación Velocidad de Viento vs. FC (Eólico)

Este documento complementa `aurameter_modulo_financiero_contexto.md`. Detalla el análisis de la relación entre velocidad de viento y FC en los proyectos eólicos reales de referencia, pensado para extrapolar (hacia arriba y abajo) a sitios nuevos sin dato de operación propio.

## Datos crudos (operación real)

| Proyecto | Zona | V media (m/s) | Altura buje | FC operado real |
|---|---|---|---|---|
| Jaramillo | Patagonia (Santa Cruz) | 10.5 | 85 m | 55% |
| Bahía Blanca | Buenos Aires (costa) | 9.5 | 130 m | 52% |
| Olavarría | Buenos Aires (centro) | 8.7 | 120 m | 50% |
| Mar del Plata | Buenos Aires (costa) | 8.5 | 130 m | 49% |
| Vieytes / Verónica | Buenos Aires (norte) | 8.0 | 120 m | 42% |
| Nogolí | San Luis (Cuyo) | 7.9 | 90 m | 40% |

## Normalización de altura

Las alturas de buje difieren entre proyectos (85–130 m), y la velocidad de viento crece con la altura (wind shear). Para comparar los sitios en igualdad de condiciones, se normalizó cada V a 100 m usando una ley de potencia estándar con exponente α = 0.14 (típico de terreno abierto).

**Nota:** α = 0.14 es un supuesto genérico. En Patagonia, con mayor rugosidad/turbulencia, el exponente real podría ser distinto — si se dispone de dato medido de shear por sitio, usarlo en vez de este supuesto.

Fórmula: `V_100 = V_medida × (100 / altura_medida)^0.14`

| Proyecto | V a 100 m (m/s) | FC real | V³ (100m) | FC / V³ |
|---|---|---|---|---|
| Jaramillo | 10.74 | 55% | 1239.3 | 0.000444 |
| Bahía Blanca | 9.16 | 52% | 767.9 | 0.000677 |
| Olavarría | 8.48 | 50% | 610.0 | 0.000820 |
| Mar del Plata | 8.19 | 49% | 549.9 | 0.000891 |
| Vieytes | 7.80 | 42% | 474.2 | 0.000886 |
| Nogolí | 8.02 | 40% | 515.3 | 0.000776 |

## Interpretación (importante para la lógica de extrapolación)

El ratio FC/V³ **no es constante** entre sitios — esto es esperable físicamente, no es ruido de datos:

- En sitios de viento alto (Jaramillo, Bahía Blanca, >9 m/s a 100m), el ratio cae notablemente (0.00044–0.00068). La turbina pasa más tiempo cerca de potencia nominal (rated), donde la curva de potencia se aplana y el FC deja de crecer con V³.
- En sitios de viento medio (Olavarría, Mar del Plata, Vieytes, Nogolí, ~7.8–8.5 m/s a 100m), el ratio es más consistente entre sí (0.00078–0.00089), porque la turbina pasa más tiempo en el tramo "cúbico" de la curva de potencia (entre cut-in y rated).

## Reglas de extrapolación sugeridas

1. **Rango 7.5–8.7 m/s (a 100m):** usar el ratio promedio de esa banda (~0.00082–0.00086, promedio de Olavarría/Mar del Plata/Vieytes/Nogolí) para estimar FC a partir de V³ de un sitio nuevo. Este es el rango con mejor consistencia de datos.
2. **>9 m/s (a 100m), tipo Patagonia:** NO extrapolar con relación cúbica genérica — el FC crece mucho más lento de lo que V³ sugeriría por la saturación de la curva de potencia. Anclarse directamente a Jaramillo o Bahía Blanca como referencia comparativa, no a una fórmula.
3. **<7.5 m/s (a 100m):** tampoco extrapolar con este ratio sin cautela — cerca del cut-in la curva de potencia cae de forma más abrupta de lo que un ajuste cúbico predice. Estos sitios probablemente ni siquiera sean viables, pero si se evalúan, tratar con más margen de error.
4. En todos los casos, esta es una extrapolación gruesa para cribado rápido de cartera (screening), no reemplaza un estudio de recurso específico (SMEC, curva de potencia real de la turbina propuesta) cuando el proyecto pasa a evaluación seria.

## Dependencias no capturadas por este modelo simplificado

La relación V-FC real depende también de:
- Curva de potencia específica de cada modelo de turbina (dato no controlado entre estos proyectos — podrían tener turbinas distintas)
- Densidad del aire (altitud, temperatura)
- Largo de pala / diámetro de rotor
- Potencia nominal de la máquina

Este modelo (ratio FC/V³ por banda de velocidad) es una aproximación práctica basada en datos reales propios, útil para descartar/priorizar sitios en etapa de prospección — no para reemplazar el cálculo técnico detallado cuando un proyecto se vuelve candidato serio.
