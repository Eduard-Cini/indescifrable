"""Pipeline offline: libro (texto plano PD) -> lecturas JSON + léxico.

Usa spaCy para segmentar en frases, tokenizar y lematizar (reconstruyendo los
verbos separables del alemán a partir de la dependencia `svp`), y diccionarios
FreeDict para la traducción por palabra (deu-spa directo + cadena
deu-eng->eng-spa + cabeza de compuesto; ver traductor.py). Exporta al formato
que consume el frontend: src/data/lecturas/<id>.json y src/data/lexico.json.

Para libros en inglés (idioma "en") la traducción por palabra es directa con
eng-spa y no hay verbos separables que reconstruir.

Uso:  PYTHONUTF8=1 python procesar.py <libro>   (p. ej. verwandlung, timemachine)
"""
import json
import re
import sys
from pathlib import Path

import spacy

RAIZ = Path(__file__).resolve().parents[1]
DIR_LECTURAS = RAIZ / "src" / "data" / "lecturas"
RUTA_LEXICO = RAIZ / "src" / "data" / "lexico.json"
FUENTES = Path(__file__).parent / "fuentes"

# --- Libros disponibles -----------------------------------------------------
LIBROS = {
    "verwandlung": {
        "id_base": "verwandlung",
        "idioma": "de",
        "nivel": "avanzado",
        "autor": "Franz Kafka",
        "titulo": {"de": "Die Verwandlung", "es": "La metamorfosis"},
        "fuente": (
            "«Die Verwandlung», Franz Kafka (1915; dominio público). "
            "Texto: Project Gutenberg, https://www.gutenberg.org/ebooks/22367. "
            "Procesado con spaCy; traducción por frase con Gemini; traducción "
            "por palabra con diccionarios FreeDict (https://freedict.org)."
        ),
        "archivo": FUENTES / "verwandlung.txt",
        "inicio": "Als Gregor Samsa",
        "frases_por_parte": 90,
    },
    "immensee": {
        "id_base": "immensee",
        "idioma": "de",
        "nivel": "avanzado",
        "autor": "Theodor Storm",
        "titulo": {"de": "Immensee", "es": "Immensee"},
        "fuente": (
            "«Immensee», Theodor Storm (1849; dominio público). "
            "Texto: Project Gutenberg, https://www.gutenberg.org/ebooks/6651. "
            "Procesado con spaCy; traducción por frase con MT offline "
            "(opus-mt de-es, Helsinki-NLP); traducción por palabra con FreeDict."
        ),
        "archivo": FUENTES / "immensee.txt",
        "inicio": "An einem Spätherbstnachmittage",
        "frases_por_parte": 90,
    },
    "timemachine": {
        "id_base": "timemachine",
        "idioma": "en",
        "nivel": "intermedio",
        "autor": "H. G. Wells",
        "titulo": {"en": "The Time Machine", "es": "La máquina del tiempo"},
        "fuente": (
            "«The Time Machine», H. G. Wells (1895; dominio público). "
            "Texto: Project Gutenberg, https://www.gutenberg.org/ebooks/35. "
            "Procesado con spaCy; traducción por frase con MT offline "
            "(opus-mt en-es, Helsinki-NLP); traducción por palabra con FreeDict."
        ),
        "archivo": FUENTES / "timemachine.txt",
        "inicio": "The Time Traveller (for so",
        "frases_por_parte": 90,
    },
    "christmascarol": {
        "id_base": "christmascarol",
        "idioma": "en",
        "nivel": "intermedio",
        "autor": "Charles Dickens",
        "titulo": {"en": "A Christmas Carol", "es": "Canción de Navidad"},
        "fuente": (
            "«A Christmas Carol», Charles Dickens (1843; dominio público). "
            "Texto: Project Gutenberg, https://www.gutenberg.org/ebooks/46. "
            "Procesado con spaCy; traducción por frase con MT offline "
            "(opus-mt en-es, Helsinki-NLP); traducción por palabra con FreeDict."
        ),
        "archivo": FUENTES / "christmascarol.txt",
        "inicio": "MARLEY was dead",
        "frases_por_parte": 90,
    },
    "usher": {
        "id_base": "usher",
        "idioma": "en",
        "nivel": "avanzado",
        "autor": "Edgar Allan Poe",
        "titulo": {"en": "The Fall of the House of Usher", "es": "La caída de la Casa Usher"},
        "fuente": (
            "«The Fall of the House of Usher», Edgar Allan Poe (1839; dominio público). "
            "Texto: Project Gutenberg, https://www.gutenberg.org/ebooks/932. "
            "Procesado con spaCy; traducción por frase con MT offline "
            "(opus-mt en-es, Helsinki-NLP); traducción por palabra con FreeDict."
        ),
        "archivo": FUENTES / "usher.txt",
        "inicio": "During the whole of a dull",
        "frases_por_parte": 90,
    },
    "deathinvenice": {
        "id_base": "deathinvenice",
        "idioma": "en",
        "nivel": "avanzado",
        "autor": "Thomas Mann",
        "titulo": {"en": "Death in Venice", "es": "La muerte en Venecia"},
        "fuente": (
            "«Death in Venice», Thomas Mann (1912; trad. inglesa de Kenneth Burke, "
            "1925; dominio público). Texto: Project Gutenberg, "
            "https://www.gutenberg.org/ebooks/66073. Procesado con spaCy; traducción "
            "por frase con MT offline (opus-mt en-es, Helsinki-NLP); traducción por "
            "palabra con FreeDict."
        ),
        "archivo": FUENTES / "deathinvenice.txt",
        "inicio": "On a spring afternoon",
        "frases_por_parte": 90,
    },
    # --- Español como lengua de estudio (libros difíciles; se ingiere un
    # FRAGMENTO acotado por `max_chars`, no la obra entera). La glosa por
    # palabra (definición de voces raras) la añade el pipeline de léxico es. ---
    "quijote": {
        "id_base": "quijote",
        "idioma": "es",
        "nivel": "avanzado",
        "autor": "Miguel de Cervantes",
        "titulo": {"es": "Don Quijote de la Mancha (selección)"},
        "fuente": (
            "«El ingenioso hidalgo don Quijote de la Mancha», Miguel de "
            "Cervantes (1605; dominio público). Texto: Project Gutenberg, "
            "https://www.gutenberg.org/ebooks/2000. Selección de los primeros "
            "capítulos, procesada con spaCy; glosa de voces poco comunes en "
            "español."
        ),
        "archivo": FUENTES / "quijote.txt",
        "inicio": "En un lugar de la Mancha, de cuyo nombre no quiero acordarme",
        "frases_por_parte": 90,
        "max_chars": 45000,
    },
    "buscon": {
        "id_base": "buscon",
        "idioma": "es",
        "nivel": "avanzado",
        "autor": "Francisco de Quevedo",
        "titulo": {"es": "La vida del Buscón (selección)"},
        "fuente": (
            "«Historia de la vida del Buscón», Francisco de Quevedo (1626; "
            "dominio público). Texto: Project Gutenberg, "
            "https://www.gutenberg.org/ebooks/32315. Selección procesada con "
            "spaCy; glosa de voces poco comunes en español."
        ),
        "archivo": FUENTES / "buscon.txt",
        "inicio": "Yo, señora, soy de Segovia",
        "frases_por_parte": 90,
        "max_chars": 45000,
    },
    "facundo": {
        "id_base": "facundo",
        "idioma": "es",
        "nivel": "avanzado",
        "autor": "Domingo F. Sarmiento",
        "titulo": {"es": "Facundo (selección)"},
        "fuente": (
            "«Facundo. Civilización y barbarie», Domingo Faustino Sarmiento "
            "(1845; dominio público). Texto: Project Gutenberg, "
            "https://www.gutenberg.org/ebooks/33267. Selección procesada con "
            "spaCy; glosa de voces poco comunes y regionalismos rioplatenses."
        ),
        "archivo": FUENTES / "facundo.txt",
        "inicio": "Sombra terrible de Facundo, voy a evocarte",
        "frases_por_parte": 90,
        "max_chars": 45000,
    },
    "tradiciones": {
        "id_base": "tradiciones",
        "idioma": "es",
        "nivel": "avanzado",
        "autor": "Ricardo Palma",
        "titulo": {"es": "Tradiciones peruanas (selección)"},
        "fuente": (
            "«Tradiciones peruanas», Ricardo Palma (s. XIX; dominio público). "
            "Texto: Project Gutenberg, https://www.gutenberg.org/ebooks/21282. "
            "Selección de las primeras tradiciones, procesada con spaCy; glosa "
            "de voces poco comunes y peruanismos."
        ),
        "archivo": FUENTES / "tradiciones.txt",
        "inicio": "Esta tradición no tiene otra fuente",
        "frases_por_parte": 90,
        "max_chars": 45000,
    },
}

CONFIG = None  # lo fija procesar(nombre)
# Modelo de spaCy por idioma del libro (solo se usa para segmentar en frases).
MODELOS = {"de": "de_core_news_md", "en": "en_core_web_sm", "es": "es_core_news_md"}
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


def _es_titulo(linea):
    """Marcador de capítulo: numeral romano o línea corta TODO EN MAYÚSCULAS
    (p. ej. «DER ALTE», «DIE KINDER» en Immensee)."""
    l = linea.strip()
    if re.fullmatch(r"[IVXLC]+\.?", l):
        return True
    letras = [c for c in l if c.isalpha()]
    return bool(letras) and l == l.upper() and len(l) <= 40


def limpiar_texto(texto):
    """El texto de Gutenberg viene doble-espaciado (una línea en blanco entre
    cada línea envuelta). Quitamos los marcadores de capítulo y unimos todo en
    un flujo continuo para que spaCy segmente por frases reales, no por saltos
    de línea."""
    lineas = [l for l in texto.splitlines() if not _es_titulo(l)]
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


def procesar(nombre):
    global CONFIG
    CONFIG = LIBROS[nombre]
    modelo = MODELOS[CONFIG["idioma"]]
    print(f"Libro: {nombre}. Cargando spaCy ({modelo})...")
    nlp = spacy.load(modelo)

    contenido = limpiar_texto(extraer_contenido(CONFIG["archivo"], CONFIG["inicio"]))
    # Fragmento: para obras enormes (Quijote) se ingiere solo un tramo inicial.
    if CONFIG.get("max_chars"):
        contenido = contenido[:CONFIG["max_chars"]]
    nlp.max_length = max(nlp.max_length, len(contenido) + 100)
    doc = nlp(contenido)

    frases = [s.text.strip() for s in doc.sents if s.text.strip()]
    print(f"  frases: {len(frases)}")

    escribir_lecturas(frases)
    print("  → ahora ejecuta construir_lexico.py para reconstruir el léxico "
          "con TODAS las lecturas.")


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


if __name__ == "__main__":
    nombre = sys.argv[1] if len(sys.argv) > 1 else "verwandlung"
    if nombre not in LIBROS:
        raise SystemExit(f"Libro desconocido: {nombre}. Opciones: {list(LIBROS)}")
    procesar(nombre)
