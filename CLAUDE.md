# indescifrable — plataforma de idiomas (tesis)

Sitio de aprendizaje de idiomas (es/en/de) como tesis en **matemática algorítmica**.
La aportación es el modelado matemático/algorítmico; el sitio es el vehículo.
Cuatro vertientes: (1) **Lectura** ✅, (2) **Repaso espaciado** ✅ (SM-2 en producción +
comparación Leitner/Markov por simulación), (3) **Gramática cloze** ✅ (spaCy + distractores
híbridos paradigma/coseno), (4) Juegos (Codenames ✅).

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
  = principiante; preposición+caso = intermedio). Navegación **por lectura**: /gramatica lista
  las lecturas del corpus (orden principiante→avanzado, chip de nivel y palomita ✓ al completar);
  /gramatica/:lectura recorre TODOS sus ejercicios agrupados por tema en orden de dificultad,
  con la regla del tema desplegable. Aciertos persistidos en `gramatica.hechos.v1` con clave
  estable fuente|antes|respuesta (sobrevive a regenerar ids). `pipeline/gramatica.py` genera 157 ejercicios
  desde TODAS las lecturas (selección estratificada round-robin por fuente) con distractores
  **híbridos**: el paradigma morfológico define el conjunto y la similitud coseno de los
  vectores spaCy lo ordena (hard negatives). Unicidad de respuesta garantizada por filtros:
  concordancia violada por re-parseo con sustitución (conjugación), pool del caso opuesto +
  marca de caso visible (preposición), verbo atestiguado en el léxico (separables).
  Motor puro `src/engine/gramatica.js` (sesión/opciones deterministas por semilla; normaliza
  el LCG de board.js a [0,1)); UI en `/gramatica` (`src/secciones/gramatica/`), JSON por
  dynamic import (chunk aparte).
- **Motor puro + Vitest** (61 tests): `src/engine/` (board LCG, bolsa, progreso, srs, conocimiento, leitner, gramatica).
- **Docs** en `docs/*.pdf` (cada portada rotulada con su sección; cada uno con su `generar_*.py`):
  - **Sección 1 — Lectura**: `documentacion-tecnica`, `plan-de-aprendizaje`, `reporte-metricas`.
  - **Sección 2 — Repaso**: `documentacion-repaso` (técnica), `metricas-repaso` (simulación + Markov + modelo de conocimiento), `ruta-aprendizaje-repaso` (auto-estudio).
  - **Sección 3 — Gramática**: `documentacion-seccion3` (técnica), `metricas-seccion3` (distractores híbridos, filtros de unicidad, conteos del corpus).

## Arquitectura (3 piezas separadas)
1. `pipeline/` Python (offline, una vez) → escribe JSON en `src/data/`.
2. `src/engine/` JS puro (testeable) — bolsa, tablero, progreso, srs (SM-2), conocimiento, leitner, gramatica (+ simulación en `simulacion/`).
3. Frontend React 19 + Vite 8 + react-router 7 — solo presenta. **Sin APIs en vivo**;
   estado en `localStorage`. Catálogo se autocarga con `import.meta.glob`.

## Comandos
Frontend: `npm run dev` · `npm run build` · `npm test` · `npm run simular` (SM-2 vs Leitner → docs/datos-simulacion.json).
Pipeline (**usar PowerShell**, con `$env:PYTHONUTF8=1`):
- Ingerir libro: `python pipeline/procesar.py <libro>` (libros en dict `LIBROS`; añadir texto con `fuentes_descargar.py <id> <nombre>`).
- Léxico (todas las lecturas): `python pipeline/construir_lexico.py`.
- Frecuencias por lema (para el modelo de conocimiento): `python pipeline/frecuencias.py` (re-ejecutar al añadir lecturas).
- Overrides separables (principiante/intermedio, curados a mano): `python pipeline/overrides_lecturas.py`.
- Ejercicios de gramática (todas las lecturas de): `python pipeline/gramatica.py [tema ...]` → `src/data/gramatica.json` (re-ejecutar al añadir lecturas).
- Frase por MT: `python pipeline/traducir_mt.py <prefijo>`.
- Frase por LLM: `exportar_frases.py <id>` → pegar en Gemini → `importar_traduccion.py <id> <archivo>` (valida 1:1).
- Regenerar PDFs: `python docs/generar_*.py` (el de `reporte-metricas` carga opus-mt para recalcular chrF; tarda ~1 min).

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
2. Menores: léxico por token (ambigüedad total), dividir léxico/lecturas para peso, más juegos (word ladder BFS, crucigrama backtracking), opcional FSRS/retención objetivo en la simulación (ejercicios en ruta-aprendizaje-repaso.pdf).

## Cómo continuar en una sesión nueva
Este archivo se carga solo. Para la Sección 1 revisar `docs/documentacion-tecnica.pdf` y
`docs/plan-de-aprendizaje.pdf`; para la Sección 2, `docs/documentacion-repaso.pdf` y
`docs/ruta-aprendizaje-repaso.pdf`; para la Sección 3, `docs/documentacion-seccion3.pdf` y
`docs/metricas-seccion3.pdf`. Pedir a Claude que confirme el estado con `git log --oneline -10`.
