"""Pipeline offline: libro (texto plano PD) -> lecturas JSON + léxico.

Usa spaCy para segmentar en frases, tokenizar y lematizar (reconstruyendo los
verbos separables del alemán a partir de la dependencia `svp`), y FreeDict
deu-spa para la traducción por palabra. Exporta al formato que consume el
frontend: src/data/lecturas/<id>.json y entradas en src/data/lexico.json.

Uso:  PYTHONUTF8=1 python procesar.py
"""
import json
import re
import unicodedata
from pathlib import Path

import spacy

from leer_diccionario import cargar_diccionario

RAIZ = Path(__file__).resolve().parents[1]
DIR_LECTURAS = RAIZ / "src" / "data" / "lecturas"
RUTA_LEXICO = RAIZ / "src" / "data" / "lexico.json"

# --- Libro a procesar -------------------------------------------------------
CONFIG = {
    "id_base": "verwandlung",
    "idioma": "de",
    "nivel": "avanzado",
    "autor": "Franz Kafka",
    "titulo": {"de": "Die Verwandlung", "es": "La metamorfosis"},
    "fuente": (
        "«Die Verwandlung», Franz Kafka (1915; dominio público). "
        "Texto: Project Gutenberg, https://www.gutenberg.org/ebooks/22367. "
        "Procesado con spaCy; traducción por palabra de FreeDict deu-spa "
        "(https://freedict.org)."
    ),
    "archivo": Path(__file__).parent / "fuentes" / "verwandlung.txt",
    "inicio": "Als Gregor Samsa",
    "frases_por_parte": 90,
}

MODELO = "de_core_news_sm"


def extraer_contenido(ruta, inicio):
    """Quita el boilerplate de Gutenberg y las páginas previas al texto."""
    txt = Path(ruta).read_text(encoding="utf-8")
    fin = txt.find("*** END")
    if fin != -1:
        txt = txt[:fin]
    i = txt.find(inicio)
    if i != -1:
        txt = txt[i:]
    return txt


def limpiar_texto(texto):
    """El texto de Gutenberg viene doble-espaciado (una línea en blanco entre
    cada línea envuelta). Quitamos los marcadores de capítulo (numerales
    romanos) y unimos todo en un flujo continuo para que spaCy segmente por
    frases reales, no por saltos de línea."""
    lineas = [
        l for l in texto.splitlines()
        if not re.fullmatch(r"\s*[IVXLC]+\.?\s*", l)
    ]
    return re.sub(r"\s+", " ", " ".join(lineas)).strip()


def normalizar(superficie):
    return re.sub(
        r"^[^\w]+|[^\w]+$", "", superficie.strip().lower(), flags=re.UNICODE
    )


def lemas_con_separables(doc):
    """Mapa índice_de_token -> lema, reuniendo prefijos separables (svp)."""
    lemas = {t.i: t.lemma_ for t in doc}
    for t in doc:
        if t.dep_ == "svp":  # prefijo verbal separable, p.ej. "vor" de "bereitet ... vor"
            reconstruido = t.text.lower() + t.head.lemma_
            lemas[t.head.i] = reconstruido
            lemas[t.i] = reconstruido
    return lemas


def procesar():
    print(f"Cargando spaCy ({MODELO}) y FreeDict deu-spa...")
    nlp = spacy.load(MODELO)
    dic = cargar_diccionario()
    print(f"  diccionario: {len(dic)} lemas")

    contenido = limpiar_texto(extraer_contenido(CONFIG["archivo"], CONFIG["inicio"]))
    nlp.max_length = max(nlp.max_length, len(contenido) + 100)
    doc = nlp(contenido)
    lemas = lemas_con_separables(doc)

    frases = [s.text.strip() for s in doc.sents if s.text.strip()]

    lexico = {}
    for t in doc:
        if not t.is_alpha:
            continue
        clave = f"de:{normalizar(t.text)}"
        if clave == "de:" or clave in lexico:
            continue
        lema = lemas[t.i]
        entrada = {"lemma": lema}
        trad = dic.get(lema.lower())
        if trad:
            entrada["es"] = trad
        lexico[clave] = entrada

    print(f"  frases: {len(frases)}  |  formas en léxico: {len(lexico)}")
    con_trad = sum(1 for v in lexico.values() if "es" in v)
    print(f"  con traducción: {con_trad} ({100*con_trad//max(1,len(lexico))}%)")

    escribir_lecturas(frases)
    fusionar_lexico(lexico)


def escribir_lecturas(frases):
    n = CONFIG["frases_por_parte"]
    partes = [frases[i : i + n] for i in range(0, len(frases), n)]
    total = len(partes)
    idioma = CONFIG["idioma"]
    for idx, parte in enumerate(partes, start=1):
        etiqueta = f" (Parte {idx}/{total})"
        lectura = {
            "id": f"{CONFIG['id_base']}-{idx:02d}",
            "nivel": CONFIG["nivel"],
            "autor": CONFIG["autor"],
            "titulo": {k: v + etiqueta for k, v in CONFIG["titulo"].items()},
            "fuente": CONFIG["fuente"],
            "cuerpo": {idioma: parte},
        }
        destino = DIR_LECTURAS / f"{CONFIG['id_base']}-{idx:02d}.json"
        destino.write_text(
            json.dumps(lectura, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"  escritas {total} lecturas en {DIR_LECTURAS}")
    return total


def fusionar_lexico(nuevos):
    existentes = {}
    if RUTA_LEXICO.exists():
        existentes = json.loads(RUTA_LEXICO.read_text(encoding="utf-8"))
    # las entradas ya presentes (curadas a mano) tienen prioridad
    fusion = dict(nuevos)
    fusion.update(existentes)
    fusion = dict(sorted(fusion.items()))
    RUTA_LEXICO.write_text(
        json.dumps(fusion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  léxico fusionado: {len(fusion)} entradas -> {RUTA_LEXICO}")


if __name__ == "__main__":
    procesar()
