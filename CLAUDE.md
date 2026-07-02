# indescifrable — plataforma de idiomas (tesis)

Sitio de aprendizaje de idiomas (es/en/de) como tesis en **matemática algorítmica**.
La aportación es el modelado matemático/algorítmico; el sitio es el vehículo.
Cuatro vertientes: (1) **Lectura** ✅, (2) Repaso espaciado (Leitner/SM-2) ⏳,
(3) Gramática cloze con spaCy ⏳, (4) Juegos (Codenames ✅).

## Estado actual (hecho)
- **Sección Lectura completa**: biblioteca (idioma/nivel), lector con traducción por
  palabra (léxico) y por frase (marcador ⇄), bolsa de palabras persistente, progreso,
  libros troceados por partes con navegación.
- **Pipeline PLN** (`pipeline/`): ingiere libros de Gutenberg, spaCy segmenta/lematiza
  (verbos separables vía dependencia `svp`), traducción por palabra con FreeDict por capas
  (directo → cadena de→en→es → compuesto), y por frase con LLM (Gemini) o MT (opus-mt).
- **Contenido**: 9 lecturas cortas trilingües (principiante/intermedio) + 2 libros avanzados:
  *Die Verwandlung* (Kafka, frase por **Gemini**) e *Immensee* (Storm, frase por **MT opus-mt**).
- **Motor puro + Vitest** (17 tests): `src/engine/` (board LCG, bolsa, progreso).
- **Docs** en `docs/*.pdf`: técnica, plan-de-aprendizaje, reporte-metricas (+ sus `generar_*.py`).

## Arquitectura (3 piezas separadas)
1. `pipeline/` Python (offline, una vez) → escribe JSON en `src/data/`.
2. `src/engine/` JS puro (testeable) — bolsa, tablero, progreso.
3. Frontend React 19 + Vite 8 + react-router 7 — solo presenta. **Sin APIs en vivo**;
   estado en `localStorage`. Catálogo se autocarga con `import.meta.glob`.

## Comandos
Frontend: `npm run dev` · `npm run build` · `npm test`.
Pipeline (**usar PowerShell**, con `$env:PYTHONUTF8=1`):
- Ingerir libro: `python pipeline/procesar.py <libro>` (libros en dict `LIBROS`; añadir texto con `fuentes_descargar.py <id> <nombre>`).
- Léxico (todas las lecturas): `python pipeline/construir_lexico.py`.
- Overrides separables (principiante/intermedio, curados a mano): `python pipeline/overrides_lecturas.py`.
- Frase por MT: `python pipeline/traducir_mt.py <prefijo>`.
- Frase por LLM: `exportar_frases.py <id>` → pegar en Gemini → `importar_traduccion.py <id> <archivo>` (valida 1:1).
- Regenerar PDFs: `python docs/generar_*.py`.

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
1. **Sección 2 — Repaso espaciado**: Leitner como cadena de Markov + SM-2 (comparar por simulación; opcional FSRS). Es el **núcleo matemático** de la tesis. Opera sobre la bolsa (`localStorage 'bolsa.v1'`); las entradas ya están listas para recibir estado SRS.
2. **Sección 3 — Gramática**: cloze con spaCy Matcher/DependencyMatcher sobre los textos; distractores por similitud coseno (embeddings).
3. Menores: léxico por token (ambigüedad total), dividir léxico/lecturas para peso, más juegos (word ladder BFS, crucigrama backtracking).

## Cómo continuar en una sesión nueva
Este archivo se carga solo. Además, revisar `docs/documentacion-tecnica.pdf` (cómo está resuelto todo)
y `docs/plan-de-aprendizaje.pdf`. Pedir a Claude que confirme el estado con `git log --oneline -10`.
