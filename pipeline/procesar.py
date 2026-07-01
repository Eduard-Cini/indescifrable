"""Pipeline offline: libro (texto plano PD) -> lecturas JSON + léxico.

Usa spaCy para segmentar en frases, tokenizar y lematizar (reconstruyendo los
verbos separables del alemán a partir de la dependencia `svp`), y diccionarios
FreeDict para la traducción por palabra (deu-spa directo + cadena
deu-eng->eng-spa + cabeza de compuesto; ver traductor.py). Exporta al formato
que consume el frontend: src/data/lecturas/<id>.json y src/data/lexico.json.

Uso:  PYTHONUTF8=1 python procesar.py
"""
import json
import re
from pathlib import Path

import spacy

from traductor import Traductor

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
        "Procesado con spaCy; traducción por palabra con diccionarios FreeDict "
        "(deu-spa y cadena deu-eng→eng-spa, https://freedict.org)."
    ),
    "archivo": Path(__file__).parent / "fuentes" / "verwandlung.txt",
    "inicio": "Als Gregor Samsa",
    "frases_por_parte": 90,
}

MODELO = "de_core_news_md"
RUTA_BASE = Path(__file__).parent / "lexico.base.json"


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
    print(f"Cargando spaCy ({MODELO}) y diccionarios FreeDict...")
    nlp = spacy.load(MODELO)
    tr = Traductor()
    print(f"  diccionarios: deu-spa={tr.tamanos()[0]} deu-eng={tr.tamanos()[1]} eng-spa={tr.tamanos()[2]}")

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
        trad = tr.traducir(lema, t.text)
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
        lectura = {
            "id": f"{CONFIG['id_base']}-{idx:02d}",
            "nivel": CONFIG["nivel"],
            "autor": CONFIG["autor"],
            "libro": CONFIG["id_base"],
            "parte": idx,
            "partes": total,
            "titulo": dict(CONFIG["titulo"]),
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
    # Reconstruye el léxico desde la base curada a mano (semilla estable), de
    # modo que re-ejecutar el pipeline sea idempotente y no arrastre entradas
    # obsoletas. Las entradas de la base tienen prioridad sobre las generadas.
    base = json.loads(RUTA_BASE.read_text(encoding="utf-8")) if RUTA_BASE.exists() else {}
    fusion = dict(nuevos)
    fusion.update(base)
    fusion = dict(sorted(fusion.items()))
    RUTA_LEXICO.write_text(
        json.dumps(fusion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  léxico: {len(nuevos)} del libro + {len(base)} base = {len(fusion)} -> {RUTA_LEXICO.name}")


if __name__ == "__main__":
    procesar()
