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
python -m spacy download de_core_news_md
```

Los diccionarios FreeDict (TEI: `deu-spa`, `deu-eng`, `eng-spa`) van en
`pipeline/diccionarios/` y no se versionan; el script los espera ahí.

> En Windows, `pip-system-certs` (incluido en requirements) hace que `requests`
> use el almacén de certificados del sistema; sin él, la descarga de modelos y
> del diccionario falla con un error SSL.

## Uso

```bash
PYTHONUTF8=1 python procesar.py
```

Descarga (si hace falta) el diccionario FreeDict deu-spa y el libro configurado
en `CONFIG` (dentro de `procesar.py`), y escribe:

- `../src/data/lecturas/<id>-NN.json` — el libro troceado en partes.
- `../src/data/lexico.json` — fusiona las formas nuevas (clave `de:<forma>` →
  `{ lemma, es }`). Las entradas curadas a mano tienen prioridad.

El catálogo del frontend (`src/data/lecturas/index.js`) carga todos los JSON
automáticamente con `import.meta.glob`, así que no hay que registrar nada a mano.

## Archivos

- `procesar.py` — pipeline principal (limpieza → spaCy → JSON).
- `traductor.py` — traducción por capas (deu-spa → cadena en inglés → compuesto).
- `leer_diccionario.py` — parser del TEI de FreeDict a `lema → traducción`.
- `diagnostico.py` — informe de cobertura por categoría gramatical.
- `lexico.base.json` — semilla curada a mano; el léxico se reconstruye desde ella.
- `requirements.txt` — dependencias de Python.
- `fuentes/`, `diccionarios/` — descargas (ignoradas por git).

## Notas de licencia / fuentes

- Textos: Project Gutenberg (dominio público). Cada lectura guarda su `fuente`.
- Diccionarios: [FreeDict](https://freedict.org) deu-spa, deu-eng, eng-spa
  (licencia libre; ver `diccionarios/<par>/COPYING` tras la descarga).
- Modelos spaCy: `de_core_news_md` (MIT).

## Verbos separables

spaCy etiqueta el prefijo separable con la dependencia `svp` (p. ej. «vor» en
«… bereitet … vor»). El pipeline lo detecta y reconstruye el lema real
(`vor` + `bereiten` = `vorbereiten`), resolviendo automáticamente el caso que
antes había que corregir a mano.
