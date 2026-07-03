# indescifrable — plataforma de idiomas (tesis)

Sitio de aprendizaje de idiomas (es/en/de) como tesis en **matemática algorítmica**.
La aportación es el modelado matemático/algorítmico; el sitio es el vehículo.
Cuatro vertientes: (1) **Lectura** ✅, (2) **Repaso espaciado** ✅ (SM-2 en producción +
comparación Leitner/Markov por simulación), (3) **Gramática cloze** ✅ (spaCy + distractores
híbridos paradigma/coseno), (4) **Juegos** ✅ (Codenames + escalera BFS + crucigrama
backtracking + Wordle entropía + sopa de letras + sudoku de palabras).

## Estado actual (hecho)
- **Sección Lectura completa**: biblioteca (idioma/nivel), lector con traducción por
  palabra (léxico) y por frase (marcador ⇄), bolsa de palabras persistente, progreso,
  libros troceados por partes con navegación.
- **Pipeline PLN** (`pipeline/`): ingiere libros de Gutenberg, spaCy segmenta/lematiza
  (verbos separables vía dependencia `svp`), traducción por palabra con FreeDict por capas
  (directo → cadena de→en→es → compuesto), y por frase con LLM (Gemini) o MT (opus-mt).
- **Contenido**: 9 lecturas cortas trilingües (principiante/intermedio) + 2 libros avanzados:
  *Die Verwandlung* (Kafka, frase por **Gemini**) e *Immensee* (Storm, frase por **MT opus-mt**).
- **Sección Repaso (motor + UI)**: SM-2 puro en `src/engine/srs.js` (estado `srs` dentro de
  cada entrada de la bolsa; `ahora` inyectable → determinista y simulable). UI en `/repaso`
  (`src/secciones/repaso/`): tarjeta palabra→traducción, 4 niveles estilo Anki
  (otraVez=2/difícil=3/bien=4/fácil=5), falladas se reciclan en la sesión, tope 10 nuevas.
  Decisión del usuario: **SM-2 único en producción**; Leitner solo para comparar por simulación.
- **Modelo de conocimiento + repaso previo**: `src/engine/conocimiento.js` estima P(conocer)
  por palabra (marcada conocida 0.95 · retrievability e^(−t/S) si tiene SRS · 0.2 en bolsa
  sin repasar · prior logístico sobre Zipf del corpus si nunca vista). Al abrir una lectura,
  el Lector interpone `RepasoPrevio` con las menos probables (tope: 5/12/20 por nivel),
  saltable, máx. 1 vez/día/lectura (`repasoPrevio.v1`); «ya la conocía» → `conocidas.v1`.
  Frecuencias del corpus: `pipeline/frecuencias.py` → `src/data/frecuencias.json` (chunk aparte).
- **Comparación Leitner vs SM-2** (núcleo matemático): `src/engine/leitner.js` (5 cajas +
  cadena de Markov: matriz, estacionaria π, E[repasos hasta caja 5] = Σ p^(−j), días, tasa
  1/Σ π·I) y `simulacion/comparar.mjs` (`npm run simular`): alumno sintético e^(−Δ/S) sobre
  los motores reales → `docs/datos-simulacion.json`. Resultado: Leitner retiene ~5 pp más
  pero cuesta ~50% más presentaciones (techo de caja 5 = sobre-repaso); SM-2 justificado.
- **Sección Gramática (pipeline + motor + UI)**: ejercicios cloze de alemán por tema
  (declinación del artículo, preposición+caso, conjugación, verbos separables), organizados
  como lección (regla + tabla) → práctica. Temas con nivel (declinación/conjugación/separables
  = principiante; preposición+caso = intermedio). Navegación **por lectura** con títulos en
  ALEMÁN: /gramatica lista las lecturas (orden principiante→avanzado, chip de nivel, palomita
  ✓ al completar); /gramatica/:lectura es el ÍNDICE de temas de esa lectura (el usuario elige
  cuál practicar; palomita por tema terminado); /gramatica/:lectura/:tema corre la tanda con
  la regla desplegable. La palomita exige tanda PERFECTA: al terminar una ronda con todas
  correctas se marca `lectura|tema` en `gramatica.completados.v1` (clave estable, sobrevive a
  regenerar ids); lectura completada = todos sus temas con palomita. `pipeline/gramatica.py` genera 157 ejercicios
  desde TODAS las lecturas (selección estratificada round-robin por fuente) con distractores
  **híbridos**: el paradigma morfológico define el conjunto y la similitud coseno de los
  vectores spaCy lo ordena (hard negatives). Unicidad de respuesta garantizada por filtros:
  concordancia violada por re-parseo con sustitución (conjugación), pool del caso opuesto +
  marca de caso visible (preposición), verbo atestiguado en el léxico (separables).
  Motor puro `src/engine/gramatica.js` (sesión/opciones deterministas por semilla; normaliza
  el LCG de board.js a [0,1)); UI en `/gramatica` (`src/secciones/gramatica/`), JSON por
  dynamic import (chunk aparte).
- **Sección Juegos (pipeline + motores + UI)**: navegación POR JUEGO en dos niveles
  (decisión del usuario): /juegos lista los juegos + Codenames (intacto en
  /juegos/codenames); /juegos/:juego es el ÍNDICE de vocabularios de ese juego («Todo el
  corpus» + solo las lecturas que lo aguantan, chip de nivel); /juegos/:juego/:lectura juega
  con ese pool. La disponibilidad es un CRITERIO FORMAL por juego en `src/engine/juegos.js`
  (escalera: ∃ par a distancia ≥3 en el grafo; wordle: ≥12 palabras en alguna longitud;
  crucigrama/sopa: ≥6 entradas; sudoku: ≥1 palabra de 9 letras TODAS distintas;
  `lecturasConJuego` filtra el índice), y los selectores solo
  ofrecen combinaciones jugables (`pasosDisponibles`, `longitudes*`, `tamanosTablero`).
  Resultado medido: principiante → crucigrama+sopa; intermedio → +wordle (y escalera si el
  grafo da); avanzado/corpus → los cuatro. **Escalera de palabras**:
  `src/engine/escalera.js` — grafo de Hamming 1 por cubetas comodín O(n·L), BFS de camino
  mínimo, retos deterministas por semilla a distancia EXACTA (selector 3-5 letras y 3-6
  pasos; pista/deshacer/rendirse; glosa española por peldaño). **Crucigrama**
  (/juegos/crucigrama): `src/engine/crucigrama.js` — backtracking (anclaje en cruces,
  más-cruces-primero, presupuesto 5.000 nodos con degradación n→n−1), numeración clásica;
  palabra alemana + pista española; cuadrícula interactiva (foco direccional, click alterna
  H/V). **Adivina la palabra** (/juegos/wordle): `src/engine/wordle.js` — feedback con
  letras repetidas en DOS pasadas (verdes consumen primero), `filtrarConsistentes` por
  definición (mismo patrón en cada intento) y entropía de Shannon de la partición que induce
  un intento; UI con glosa por intento, contador «quedan N posibles», pista opcional (la
  traducción del secreto) y colores sólidos de alto contraste; intentos restringidos al
  corpus (o a la lectura). **Sopa de letras** (/juegos/sopa): `src/engine/sopa.js` — colocación
  aleatorizada con reintentos (solo →, ↓, ↘; solapes compatibles), relleno muestreando la
  distribución de letras del pool, selección por dos clicks (inicio/fin, válida al revés);
  pistas en español, palabras en alemán. **Sudoku de palabras** (/juegos/sudoku):
  `src/engine/sudoku.js` — solución 9×9 por backtracking barajado, EXCAVADO CON UNICIDAD
  (contador de soluciones con MRV, corte en 2) y biyección dígito→letra por fila: una fila
  esconde una palabra de 9 letras distintas que se revela con su traducción; dificultad =
  casillas dadas (fácil 40 / intermedio 32 / difícil 26), medido 100% unicidad y ≤66
  ms/tablero. Datos: `pipeline/juegos.py` → `src/data/juegos.json`
  (escalera/wordle: formas ASCII L=3-5 con glosa — sin umlauts por tecleo; crucigrama/sopa:
  400 lemas frecuencia ≥2 sin funcionales; sudoku: 40 palabras de 9 letras distintas; y los
  MISMOS pools POR LECTURA, partes de libro agrupadas por título y override léxico de la
  lectura aplicado), chunk aparte por dynamic import. Métricas
  reales: `npm run simular-juegos` (`simulacion/juegos-stats.mjs` corre los motores de
  producción → `docs/datos-juegos.json`; backtracking y sopa 100% éxito; componente gigante
  62/115/64 por longitud; wordle: mejor 1er intento «nahe»/«heran» 4.2/5.6 bits, solver
  voraz 3.4/3.0 intentos medios, ≥99% en ≤6). `board.js` exporta `crearGeneradorNormalizado`
  (antes helper privado de gramatica.js) y los imports internos del engine llevan extensión
  `.js` (los usa node).
- **Motor puro + Vitest** (157 tests): `src/engine/` (board LCG, bolsa, progreso, srs, conocimiento, leitner, gramatica, escalera, crucigrama, wordle, sopa, sudoku, juegos ← pools/disponibilidad).
- **Docs** en `docs/*.pdf` — REGLA: cada sección lleva SIEMPRE tres documentos con la sección
  en el nombre (`documentacion-seccionN`, `metricas-seccionN`, `autoaprendizaje-seccionN`),
  cada uno con su `generar_*.py` homónimo y la portada rotulada con la sección:
  - **Sección 1 — Lectura**: `documentacion-seccion1`, `metricas-seccion1` (cobertura, chrF; carga opus-mt al regenerar), `autoaprendizaje-seccion1`.
  - **Sección 2 — Repaso**: `documentacion-seccion2`, `metricas-seccion2` (simulación + Markov + modelo de conocimiento), `autoaprendizaje-seccion2`.
  - **Sección 3 — Gramática**: `documentacion-seccion3`, `metricas-seccion3` (distractores híbridos, filtros de unicidad, conteos del corpus), `autoaprendizaje-seccion3`.
  - **Sección 4 — Juegos**: `documentacion-seccion4`, `metricas-seccion4` (grafo de Hamming del corpus, éxito del backtracking, entropía del Wordle, disponibilidad por lectura; lee `docs/datos-juegos.json` → correr antes `npm run simular-juegos`), `autoaprendizaje-seccion4`.

## Arquitectura (3 piezas separadas)
1. `pipeline/` Python (offline, una vez) → escribe JSON en `src/data/`.
2. `src/engine/` JS puro (testeable) — bolsa, tablero, progreso, srs (SM-2), conocimiento, leitner, gramatica (+ simulación en `simulacion/`).
3. Frontend React 19 + Vite 8 + react-router 7 — solo presenta. **Sin APIs en vivo**;
   estado en `localStorage`. Catálogo se autocarga con `import.meta.glob`.

## Comandos
Frontend: `npm run dev` · `npm run build` · `npm test` · `npm run simular` (SM-2 vs Leitner → docs/datos-simulacion.json) · `npm run simular-juegos` (estadísticas de juegos → docs/datos-juegos.json).
Pipeline (**usar PowerShell**, con `$env:PYTHONUTF8=1`):
- Ingerir libro: `python pipeline/procesar.py <libro>` (libros en dict `LIBROS`; añadir texto con `fuentes_descargar.py <id> <nombre>`).
- Léxico (todas las lecturas): `python pipeline/construir_lexico.py`.
- Frecuencias por lema (para el modelo de conocimiento): `python pipeline/frecuencias.py` (re-ejecutar al añadir lecturas).
- Overrides separables (principiante/intermedio, curados a mano): `python pipeline/overrides_lecturas.py`.
- Ejercicios de gramática (todas las lecturas de): `python pipeline/gramatica.py [tema ...]` → `src/data/gramatica.json` (re-ejecutar al añadir lecturas).
- Datos de juegos (escalera + crucigrama): `python pipeline/juegos.py` → `src/data/juegos.json` (re-ejecutar al añadir lecturas).
- Frase por MT: `python pipeline/traducir_mt.py <prefijo>`.
- Frase por LLM: `exportar_frases.py <id>` → pegar en Gemini → `importar_traduccion.py <id> <archivo>` (valida 1:1).
- Regenerar PDFs: `python docs/generar_*.py` (el de `metricas-seccion1` carga opus-mt para recalcular chrF; tarda ~1 min).

## Trampas del entorno (IMPORTANTES)
- **git SSL**: usa `http.sslBackend schannel` (almacén de Windows). **Python SSL**: `pip-system-certs`.
- **Siempre** `$env:PYTHONUTF8=1` (umlauts) y `json.dump(..., ensure_ascii=False)`.
- **Usar PowerShell**: el Bash de esta sesión se quedó sin PATH.
- Modelos/diccionarios pesados (spaCy, FreeDict, opus-mt/torch) **no** van en git (gitignore en `pipeline/`). Se documentan y se cachean fuera del repo. Solo se versiona el JSON de salida.
- Instalar MT: `pip install transformers torch sentencepiece sacremoses` + modelo Helsinki-NLP/opus-mt-de-es (se baja solo).

## Decisiones clave
- Texto **paralelo alineado** para traducir la frase; **léxico** (idioma:forma→{lemma,es}) para la palabra.
- El léxico global no desambigua por contexto ("nahm"=annehmen vs nehmen) → **overrides por lectura** (`reading.lexico`, tiene prioridad en el Lector). Solución general futura: léxico por token.
- Léxico grande cargado con **dynamic import** (fuera del bundle inicial).
- Cobertura por palabra: 100% principiante/intermedio, ~92-94% libros. MT vs Gemini: chrF 61.9.

## Próximo trabajo (prioridad)
1. Menores de gramática: más temas (orden de palabras/verbo en 2ª posición, Konjunktiv),
   progreso persistente por tema en localStorage, ejercicios también en inglés.
2. Menores: léxico por token (ambigüedad total), dividir léxico/lecturas para peso, opcional FSRS/retención objetivo en la simulación (ejercicios en autoaprendizaje-seccion2.pdf).
3. Menores de juegos: reto diario (semilla = fecha), crucigrama/sopa con la bolsa del usuario como pool (el Codenames YA acepta la bolsa como vocabulario, opción «Mi bolsa» en Landing.jsx), umlauts como ae/oe/ue en la escalera (experimentos en autoaprendizaje-seccion4.pdf).

## Cómo continuar en una sesión nueva
Este archivo se carga solo. Cada sección tiene sus tres PDFs en `docs/`
(`documentacion-seccionN`, `metricas-seccionN`, `autoaprendizaje-seccionN`); empezar por la
documentación técnica de la sección que toque. Pedir a Claude que confirme el estado con
`git log --oneline -10`.
