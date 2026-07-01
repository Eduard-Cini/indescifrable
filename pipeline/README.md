# Pipeline offline (PLN)

Procesa libros de dominio público a las lecturas JSON que consume el frontend,
usando **spaCy** (segmentación, tokenización, lematización con reconstrucción de
verbos separables alemanes) y **diccionarios FreeDict** por capas para la
traducción por palabra (deu-spa directo, cadena deu-eng→eng-spa, y cabeza de
compuesto; ver `traductor.py`). Cobertura ~92 %. No usa ninguna API en línea.

## Instalación (una vez)

```bash
cd pipeline
python -m pip install -r requirements.txt
python -m spacy download de_core_news_md   # alemán
python -m spacy download en_core_web_sm     # inglés (léxico de textos en inglés)
```

Los diccionarios FreeDict (TEI: `deu-spa`, `deu-eng`, `eng-spa`) van en
`pipeline/diccionarios/` y no se versionan; el script los espera ahí.

> En Windows, `pip-system-certs` (incluido en requirements) hace que `requests`
> use el almacén de certificados del sistema; sin él, la descarga de modelos y
> del diccionario falla con un error SSL.

## Uso

**1. Ingerir un libro** (limpieza → spaCy → lecturas troceadas):

```bash
python fuentes_descargar.py 6651 immensee   # descarga el texto de Gutenberg
PYTHONUTF8=1 python procesar.py immensee     # libro de LIBROS (verwandlung, immensee)
```

**2. Reconstruir el léxico** desde TODAS las lecturas (alemán e inglés):

```bash
PYTHONUTF8=1 python construir_lexico.py
```

Escribe `../src/data/lexico.json` (`idioma:<forma>` → `{ lemma, es }`) partiendo
de `lexico.base.json` (entradas curadas, con prioridad). Idempotente. Informa la
cobertura por lectura. El catálogo del frontend carga los JSON con
`import.meta.glob`, así que no hay que registrar nada a mano.

**3. Traducción por oración de libros (LLM, opcional):** los libros solo traen
el original. Para darles la traducción por frase con un LLM (p. ej. Gemini)
conservando la alineación 1:1:

```bash
PYTHONUTF8=1 python exportar_frases.py verwandlung-01     # -> lista numerada + prompt
# pegar en el LLM, guardar la respuesta en traducciones/verwandlung-01.es.txt
PYTHONUTF8=1 python importar_traduccion.py verwandlung-01 traducciones/verwandlung-01.es.txt
```

`importar_traduccion.py` valida el conteo/numeración: si no cuadra 1:1, no
escribe nada. El frontend activa el ⇄ por frase en cuanto existe `cuerpo.es`.

**3-bis. Traducción por oración con MT offline (sin API):** alternativa
automática al LLM, con opus-mt (Helsinki-NLP) de→es directo. Requiere:
`pip install transformers torch sentencepiece sacremoses` (el modelo ~300 MB se
descarga la primera vez). Alineación 1:1 automática:

```bash
PYTHONUTF8=1 python traducir_mt.py immensee   # traduce todas las partes -> cuerpo.es
```

Calidad menor que un LLM (p. ej. `bestäubt`→«polinizados» en vez de «polvoriento»),
pero sin copia-pega. En el proyecto: *Die Verwandlung* usa Gemini, *Immensee* usa MT.

## Archivos

- `procesar.py` — ingesta de un libro (limpieza → spaCy → lecturas JSON); los
  libros disponibles están en el dict `LIBROS`.
- `fuentes_descargar.py` — descarga un texto de Project Gutenberg a `fuentes/`.
- `construir_lexico.py` — construye el léxico desde todas las lecturas (de + en).
- `mt.py` / `traducir_mt.py` — traducción por frase con MT offline (opus-mt).
- `traductor.py` — traducción por capas (deu-spa → cadena en inglés → compuesto;
  y eng-spa para inglés).
- `leer_diccionario.py` — parser del TEI de FreeDict a `lema → traducción`.
- `diagnostico.py` — informe de cobertura por categoría gramatical.
- `exportar_frases.py` / `importar_traduccion.py` — traducción por oración vía LLM.
- `lexico.base.json` — semilla curada a mano; el léxico se reconstruye desde ella.
- `fuentes/`, `diccionarios/`, `traducciones/` — descargas/intermedios (ignorados).

## Notas de licencia / fuentes

- Textos: Project Gutenberg (dominio público). Cada lectura guarda su `fuente`.
- Diccionarios: [FreeDict](https://freedict.org) deu-spa, deu-eng, eng-spa
  (licencia libre; ver `diccionarios/<par>/COPYING` tras la descarga).
- Modelos spaCy: `de_core_news_md`, `en_core_web_sm` (MIT).

## Verbos separables

spaCy etiqueta el prefijo separable con la dependencia `svp` (p. ej. «vor» en
«… bereitet … vor»). El pipeline lo detecta y reconstruye el lema real
(`vor` + `bereiten` = `vorbereiten`), resolviendo automáticamente el caso que
antes había que corregir a mano.
