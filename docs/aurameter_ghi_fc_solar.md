# Aurameter — Relación GHI vs. FC (Solar)

Este documento complementa `aurameter_modulo_financiero_contexto.md` y `aurameter_velocidad_fc_eolico.md`. Detalla la relación entre irradiancia (GHI) y FC en los proyectos solares reales de referencia, para extrapolar a sitios nuevos sin dato de operación propio.

## Datos crudos (operación real)

| Proyecto | Ubicación | GHI (kWh/m²/año) | FC operado real |
|---|---|---|---|
| PS La Aconquija | Pie de Médano, Catamarca (NOA) | 2390 | 35% |
| Nogolí (solar) | San Luis (Cuyo) | 1975 | 29.5% |

**Nota:** confirmar si "Nogolí" solar es el mismo predio que el proyecto eólico Nogolí (San Luis, FC eólico 40%) o un sitio distinto con el mismo nombre de referencia — evitar confundir ambos datasets en el código.

## Relación FC/GHI

| Proyecto | GHI | FC | FC/GHI |
|---|---|---|---|
| PS La Aconquija | 2390 | 35% | 0.01464 |
| Nogolí (solar) | 1975 | 29.5% | 0.01494 |

El ratio es prácticamente constante entre los dos sitios (diferencia ~2%), consistente con una relación lineal — a diferencia del caso eólico, el FC solar no tiene efecto de saturación por curva de potencia plana; la energía generada es aproximadamente proporcional a la irradiancia incidente. El clipping por sobredimensionamiento DC/AC ya está incorporado en el PR de diseño de cada proyecto (81.9% en el caso de Aconquija, ver `aurameter_modulo_financiero_contexto.md`), no es necesario modelarlo aparte en esta relación.

## Fórmula de extrapolación

Con ratio promedio k ≈ 0.0148 (promedio de los dos puntos):

```
FC_estimado = GHI_sitio_nuevo × k
```

Con k = 0.0148 (redondeado), o interpolando linealmente entre los dos puntos conocidos (2390→35%, 1975→29.5%) para sitios dentro de ese rango de GHI.

## Límites de validez

- Solo 2 puntos de calibración — la linealidad es plausible por la física del panel solar, pero conviene sumar un tercer proyecto real (si existe) para confirmar la pendiente con más confianza antes de confiar en la extrapolación fuera del rango 1975–2390 kWh/m²/año.
- Fuera de ese rango (GHI muy bajo o muy alto respecto a estos dos sitios), la relación lineal debería mantenerse razonablemente bien dado el mecanismo físico, pero no hay dato propio que lo confirme — tratar como estimación de menor confianza.
- Esta relación no reemplaza un cálculo de PVsyst/PVcase para un proyecto que pasa a evaluación seria; es una herramienta de cribado rápido (screening) en etapa de prospección.
- Igual que en el módulo eólico y financiero: esta tabla y sus ratios son de uso interno del motor de cálculo, no se muestran en el exportable ni en la UI de cara al inversor.
