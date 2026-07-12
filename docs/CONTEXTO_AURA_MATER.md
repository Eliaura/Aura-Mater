# AURA Energy — Buscador de Oportunidades MATER — Contexto para Claude Code

## Qué es esto
Herramienta interna (NO se comparte con clientes/terceros) de AURA Energy Solutions
(consultora renovables, Argentina, co-fundada por Elías Melken y Facundo Manuelli) que
analiza el Anexo 3 de Cammesa (capacidad de conexión MATER) para solar y eólica, la
rankea por recurso natural + potencia disponible, la segmenta para uso comercial, y la
expone en un dashboard Streamlit interactivo. Es la ventaja competitiva de AURA frente a
competidores como Anabatica y Aires Renewables — nunca se comparte externamente.

## Archivo actual
`aura.py` — app Streamlit única (~318 líneas + datasets embebidos, ~300KB). Corre con
`streamlit run aura.py`. Contiene TODO: solar + eólica + modo actual + modo prospección,
en un solo archivo con datasets embebidos como listas de diccionarios Python.

## Fuentes de datos originales (en /mnt/user-data/uploads/ de la sesión anterior, pedir de nuevo si hace falta)
- `MATER_Referencial_A_2T2026.xlsx` y `MATER_Pleno_2T2026.xlsx` — 2T2026 CONFIRMADO por
  Cammesa. Hoja 'ANEXO 3.1', ~877 filas, 12 columnas, ~299 celdas combinadas (merged cells).
  Columnas: A=corredor(header, no siempre presente), B=ID, C=Nombre, D=Tipo (EETT/Línea),
  E=Nivel de tensión (kV, numérico limpio: 500/330/220/132/66/33/13.2), F=PDI, G-L=L1..L6
  (límites de capacidad en texto tipo "100 MW" o "20 MW + 50 MW (#2)").
- `Circular_N__04_-_Adjunto_1_-_ANEXO_3_-_Nodos_Propuestos.xlsx` — 255 nodos SADI con
  coordenadas reales (ID col B, LAT col E, LON col F, CONEXION EN col H, PROVINCIA col D,
  REGION col C). IDs en esquema DISTINTO al Anexo 3 MATER — el cruce es por NOMBRE de
  estación normalizado + validación de bounding box por corredor (para evitar falsos
  positivos de nombres homónimos en regiones distintas).
- `ARG_wind-speed_100m.tif` — GeoTIFF Global Wind Atlas, velocidad viento a 100m,
  Argentina completa. 8377×14660 px, EPSG:4326, resolución 0.0025° (250m). Se lee con
  `rasterio` (`src.index(lon,lat)` → pixel → `band[row,col]`). nodata=nan.

## Lógica de negocio validada (NO cambiar sin confirmar con el usuario)

### Parser de celdas combinadas
`build_merged_map(ws)` mapea cada (row,col) al valor de la celda origen del merge.
Cada fila es INDEPENDIENTE: capacidad = min(PDI, L1..L6 de ESA fila con merges resueltos).
Solo se cuentan filas con Tipo=EETT y PDI>0. NO hay propagación entre filas.

### Capacidad por tecnología — formato "base MW + adicional MW (#N)"
- El número BASE (antes del +) sirve para CUALQUIER tecnología.
- El ADICIONAL (después del +) es EXCLUSIVO: #1 = solar exclusivo, #2 = eólico exclusivo.
- `cap_solar(texto) = base + (#1 si existe)`
- `cap_eolica(texto) = base + (#2 si existe)`
- Ejemplos: "100" → solar 100/eólica 100. "0+200(#1)" → solar 200/eólica 0.
  "20+50(#2)" → solar 20/eólica 70.

### Capacidad ejecutable (modo actual)
`cap_ejecutable = MAX(cap_Ref_A, cap_Pleno)`. Pleno despacha 100% (más escaso, ~133
nodos). Ref A despacha 92% (más volumen, ~422 nodos). La app tiene selector triple:
"Ejecutable (MAX)" / "Solo Pleno (100%)" / "Solo Ref A (92%)".

### Los 4 grupos de exportación (columna L6, NO por corredor sino por grupo compartido)
Se identifican por el TEXTO del límite L6 (no por el nombre del corredor):
1. **CENTRO-CUYO-NOA**: "20 MW + 50 MW (#2)" → 354 nodos, comparten NOA/Cuyo/Centro.
   Solar L6=20, Eólica L6=70 (20 base + 50 del #2 eólico).
2. **MISIONES-NEA-LITORAL**: "640 MW" → 193 nodos. Igual para ambas tecnologías. Sin
   nodos topeados (el corredor ya está sobredimensionado).
3. **PATAGONIA-PBA**: "0 MW + 200 MW (#1)" → 172 nodos, comparten Costa Atlántica/
   Patagonia/PBA Centro-Sur. Solar L6=200, Eólica L6=0 (los 200MW son #1 solar exclusivo).
4. **COMAHUE**: "100 MW" → 104 nodos, solo Comahue. Igual para ambas.

### El cuello de botella maestro de la Patagonia (IMPORTANTE, recién resuelto)
La Patagonia tiene el MEJOR viento del país (hasta 12.6 m/s en Pampa del Castillo,
>10 m/s en toda la zona de Comodoro Rivadavia) pero solo 8 nodos tienen PDI>0, y TODOS
están bloqueados en 0 MW por una cascada de límites intermedios cuyo denominador común
es "COR. PATAGONIA 500 kV = 0 MW". Es decir: la Patagonia está construida pero sin la
línea de 500kV que la conecta al resto del SADI. En el modo prospección hay un control
dedicado ("🌊 Corredor Patagonia 500 kV", separado de los 4 grupos L6) que, al levantarse,
abre esos 8 nodos con 870 MW total: Río Santa Cruz 500kV (300MW, 9.2 m/s), Santa Cruz
Norte (200MW), Puerto Madryn 500 (117MW, 8.7 m/s), Sierra Grande (50MW, 8.4 m/s), San
Antonio Oeste (18MW, 8.2 m/s), Futaleufú, El Coihue, Río Santa Cruz 132kV. Estos nodos
tienen flag `bloqueo_patagonia=True` en el dataset — cuando ese flag es True, el control
del corredor Patagonia SUSTITUYE (no se suma a) el L6 normal del grupo PATAGONIA-PBA,
porque en la realidad haría falta abrir ambos a la vez y así se simula esa apertura
conjunta con un solo control.

### Ranking
- **Solar**: lineal. `score = (peso_GHI/100)×GHI_norm + (peso_MW/100)×MW_norm`. Peso GHI
  por defecto: 80% (modo actual) / 90% (modo prospección).
- **Eólica**: ponderado por v³ porque energía ∝ velocidad³. `score = (peso_viento/100)×
  norm(viento³) + (peso_MW/100)×MW_norm`. Peso viento por defecto: 85% (actual) / 90%
  (prospección).
- Ambos pesos son sliders ajustables en vivo en el sidebar.

### Segmentación AURA
⭐ Desarrollar (AURA) si cap ≤ umbral (default 50 MW, ajustable) — proyectos chicos que
AURA puede desarrollar directo. 🤝 Ofrecer a terceros si cap > umbral — proyectos grandes
para ofrecer a EPCs con capital.

### Nivel de tensión (AGREGADO EN ESTA SESIÓN — crítico para viabilidad real)
Columna E del Anexo 3 = nivel de tensión del nodo en kV. Valores posibles en todo el
SADI: **500, 330, 220, 132, 66, 33, 13.2** (no hay otros niveles, confirmado). Se extrajo
para el 100% de los 505 nodos de ambos datasets (solar y eólica) y quedó como campo
`tension` (float) en cada nodo.

**Por qué importa**: un nodo con pocos MW en un nivel de tensión muy alto (500/330 kV) es
técnicamente inviable de conectar en la práctica — esos niveles están pensados para
cientos/miles de MW. Ejemplo real detectado: "NUEVA SAN JUAN 500 KV" (id 6400) aparecía
como top-ranking con 20 MW y GHI 2150, pero es inviable en 500kV; el nodo homónimo
"NUEVA SAN JUAN 132 KV" (id 6390, mismo lugar físico, otro nivel de tensión) es el que
habría que evaluar en la práctica. El Anexo 3 tiene VARIOS nodos con el mismo nombre de
localidad pero distinto ID y distinta tensión (son transformadores en cascada del mismo
lugar).

**Implementación actual**: filtro de pulsadores multi-select (`st.pills`) en el sidebar,
con los 7 niveles como opciones, default = todos seleccionados. Se aplica como
`df = df[df["tension"].isin(sel_tension)]` tanto en modo actual como en modo prospección.
La tensión también se muestra como badge en las tarjetas de ranking, columna en la tabla,
y campo en el hover del mapa.

**Pendiente de decidir con el usuario** (mencionado pero no implementado): quizás
conviene una regla de negocio que penalice o filtre por defecto combinaciones MW-chicos +
tensión-alta que son estructuralmente inviables (ej. reglas tipo "en 500kV solo tiene
sentido evaluar >100MW"). El usuario prefirió manejarlo él mismo con los pulsadores por
ahora, no automatizarlo todavía.

## Estructura de la app (aura.py)

```
SOLAR = [...]   # 505 nodos, dataset embebido como lista de dicts
EOLICA = [...]  # 505 nodos, dataset embebido como lista de dicts

# Ambos dicts por nodo tienen estas claves:
# id, nombre, corredor, lat, lon, tension,
# cap_refa, cap_pleno, cap_ejec,          <- modo actual (3 niveles de despacho)
# min_sin_l6, grupo, l6_actual, cap_actual, <- modo prospección
# ghi                                      <- solo SOLAR
# viento, v_fuente('real'/'estimado'), bloqueo_patagonia  <- solo EOLICA

# Sidebar con DOS switches:
# 1. Tecnología: "☀️ Solar" / "💨 Eolica"  → determina THEME (colores), dataset, recurso
# 2. Vista: "📊 Oportunidades actuales" / "🔮 Prospección futura"

# Modo actual: selector triple despacho, filtro corredor, filtro tensión (nuevo),
#   slider pesos ranking, umbral segmentación. 4 tabs: Mapa/Ranking/Por corredor/Tabla.
# Modo prospección: 4 number_input de L6 (uno por grupo export), control Corredor
#   Patagonia 500kV (solo eólica), filtro tensión (nuevo), slider pesos.
#   3 tabs: Nodos que se liberan/Mapa/Tabla.
```

## Calidad de los datos de viento (eólica)
- 378 de 505 nodos (74%) tienen viento REAL extraído del Global Wind Atlas mediante
  coordenadas geolocalizadas (validadas o asignadas manualmente por localidad conocida).
- El resto tiene viento ESTIMADO por promedio de corredor (fallback, marcado con 📍 en
  vs 📡 para real). Diccionario `VIENTO_CORREDOR` con promedios validados: Costa
  Atlántica 8.0, PBA Centro-Sur 7.0, Comahue 7.2, BsAs 6.7, Litoral 6.5, NEA 6.3,
  Centro 6.0, GBA 6.5, Misiones 5.1, NOA 4.5, Cuyo 4.3, Patagonia 9.0 m/s.
- Precisión honesta: las coordenadas asignadas manualmente son a nivel de LOCALIDAD, no
  la traza exacta de cada estación transformadora. Error esperado ±0.5-1 m/s en zonas de
  relieve fuerte (sierras, cordillera). Sirve muy bien para rankear/priorizar zonas; para
  la decisión final de un sitio específico puntual, conviene lectura de precisión o
  medición en sitio.
- Se corrigieron manualmente casos de geolocalización errónea que caían en píxeles de
  cordillera dando valores imposibles (ej. "El Sosneado" daba 13.1 m/s, corregido a 8.0
  reubicando la coordenada al valle).

## Historial de fixes importantes en esta sesión (para no repetir errores)
1. **Comahue tenía viento estimado plano (7.2 m/s) en 59 de 63 nodos** porque solo 4
   tenían coordenadas del archivo de Cammesa. Se asignaron coordenadas reales a 54 nodos
   más (localidades conocidas del sistema neuquino/rionegrino/pampeano) y se extrajo
   viento real, revelando rango real de 3.7 a 11.2 m/s (los nodos cordilleranos como Pío
   Protto y Pilcaniyeu son excepcionales).
2. **Patagonia invisible en toda la app**, sobre todo en prospección. Causa raíz: cascada
   de límites en 0 con "COR. PATAGONIA 500 kV" como cuello de botella común a los 8 únicos
   nodos con PDI>0. Resuelto con control dedicado (ver sección arriba).
3. **Mapa con problemas de tamaño/escala**: se corrigió con `.clip(lower=5)` en el tamaño
   de burbuja (evita fallos con capacidad 0) y `range_color` fijo para viento (3-12 m/s)
   para que el color sea comparable entre escenarios.
4. **Ranking por corredor invertido**: Plotly con barras horizontales necesita
   `sort_values(ascending=True)` + `yaxis={"categoryorder":"total ascending"}` para que
   el corredor más grande quede arriba visualmente. Ya corregido.
5. **Zoom con scroll del mouse**: agregado `config={"scrollZoom": True}` en todos los
   `st.plotly_chart` de mapas (variable `MAP_CONFIG` reutilizada).

## Técnicas de edición usadas (útiles para Claude Code)
- Los datasets se manipulan con `content.find('SOLAR = [')` / `content.find('    return
  pd.DataFrame(SOLAR)')` para delimitar el bloque, luego `ast.literal_eval()` para
  parsear la lista de dicts de forma segura (NUNCA `exec()` reutilizando namespace entre
  archivos — causa bugs sutiles de variables pisadas), se modifica en memoria, y se
  reescribe con `repr(lista)`. Siempre validar con `ast.parse()` antes de guardar.
- pip: usar `pip install <pkg> --break-system-packages`.
- rasterio ya está instalado en el entorno (`rasterio==1.5.0`).

## Pendientes explícitos que el usuario quiere retomar
1. **Decidir HTML vs Streamlit** para el entregable final (ver análisis arriba — mi
   recomendación fue quedarse en Streamlit por ahora dado que es interna y los datos de
   Cammesa se actualizan trimestralmente).
2. **Identidad visual AURA**: el usuario va a proveer la base de diseño gráfico de la
   marca (colores, tipografías, logo) para reemplazar la paleta genérica actual
   (azul=solar, verde/teal=eólica) por la identidad real de AURA Energy.
3. **Posible regla de negocio tensión×MW**: definir si conviene un filtro/penalización
   automática para combinaciones estructuralmente inviables (poco MW en tensión muy alta),
   o dejarlo 100% manual con los pulsadores (decisión actual del usuario).
4. **Refinar coordenadas**: a medida que el usuario consiga coordenadas más precisas
   (traza exacta de ET en vez de localidad), reemplazar en el dataset para mejorar
   precisión del viento en zonas de relieve.
5. **Actualización trimestral**: cuando salga el próximo corte de Cammesa (3T2026), habrá
   que re-correr todo el pipeline de parseo con los archivos nuevos.
6. **Exportables con identidad de marca AURA** (ej. "ficha de oportunidad" en PDF para
   llevar a reuniones con EPCs, con logo/colores/tipografía de AURA): Streamlit no genera
   esto nativamente con buen resultado — el camino recomendado es generar un documento
   PDF/HTML aparte (vía `reportlab`, `weasyprint`, o similar) alimentado por los datos que
   la app ya calcula (nodo, score, capacidad, recurso, tensión), siguiendo el mismo patrón
   que ya se usó para el Excel `MATER_Solar_2T2026_v10.xlsx` (lógica en Python, archivo de
   salida con diseño propio separado de la UI de análisis). Esto es un dato adicional a
   favor de considerar HTML para el front en algún momento, si los exportables con marca
   se vuelven un objetivo central y no solo algo ocasional.

## Archivos de referencia adicionales generados en sesiones previas (pueden no estar ya
disponibles, pedir de nuevo si hace falta)
- `MATER_Solar_2T2026_v10.xlsx` — Excel completo con fórmulas dinámicas, 505 filas,
  hoja Parámetros para ajustar pesos, hoja Metodología. Generado con openpyxl,
  validado con script de recálculo, 0 errores de fórmula.
- Las 4 apps Streamlit sueltas anteriores a la unificación (aura_solar_actual.py,
  aura_solar_futuro.py, aura_eolica_actual.py, aura_eolica_futuro.py) — ya obsoletas,
  reemplazadas por aura.py, pero pueden servir de referencia si hace falta ver una
  versión más simple de la lógica de un solo modo.

## Idioma y contexto de comunicación
El usuario (Elías) se comunica en español. Prefiere que Claude ejecute con dirección
clara en vez de sugerir proactivamente — dar recomendaciones técnicas honestas cuando se
piden, pero no añadir alcance no solicitado. Sesiones de trabajo técnico intenso,
iterativas, con verificación de cada paso antes de avanzar al siguiente.
