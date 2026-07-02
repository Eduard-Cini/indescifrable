"""Pipeline offline de la Sección 3 (Gramática): corpus alemán -> ejercicios cloze.

Recorre las frases en alemán de TODAS las lecturas de src/data/lecturas, usa
spaCy (de_core_news_md, con vectores) para localizar un «hueco» por cada uno de
los cuatro temas y genera los distractores con un método HÍBRIDO:

  1. el PARADIGMA morfológico define el CONJUNTO de candidatos plausibles, y
  2. la SIMILITUD COSENO de los vectores spaCy los ORDENA para quedarnos con
     los k «hard negatives» más parecidos al correcto.

Para que la respuesta sea ÚNICA (un cloze sin respuesta única no evalúa nada),
cada tema añade su propio criterio de exclusión de alternativas válidas:
  - declinación: las demás formas del artículo violan caso/género/número.
  - preposición: el pool son las preposiciones del CASO OPUESTO, así el
    artículo visible en la frase descarta los distractores.
  - conjugación: un candidato solo vale como distractor si, re-parseada la
    frase con la sustitución, VIOLA la concordancia (persona/número) o no es
    forma finita; si concuerda (p. ej. otro tiempo: ging→geht) se descarta
    porque también sería una frase válida.
  - separables: se excluyen los prefijos que forman con el mismo verbo otro
    verbo atestiguado en el léxico del corpus (aufmachen vs zumachen).

La selección final es ESTRATIFICADA: round-robin entre fuentes (ordenadas por
nivel) hasta el tope, para que principiante/intermedio/libros aporten todos.

El resultado (src/data/gramatica.json) lo consume src/engine/gramatica.js y la
UI de /gramatica. El frontend nunca calcula coseno: todo ocurre aquí, offline.

Uso:  PYTHONUTF8=1 python gramatica.py [tema ...]
      (sin argumentos procesa los cuatro temas)
"""
import json
import sys
from pathlib import Path

import numpy as np
import spacy

from procesar import normalizar, RAIZ

DIR_LECTURAS = RAIZ / "src" / "data" / "lecturas"
RUTA_SALIDA = RAIZ / "src" / "data" / "gramatica.json"
RUTA_LEXICO = RAIZ / "src" / "data" / "lexico.json"
MODELO = "de_core_news_md"

# Sólo frases legibles como cloze: las de los libros llegan a 40+ tokens.
MAX_TOKENS = 18
TOPE_POR_TEMA = 40
MAX_POR_FUENTE = 12  # cota de candidatos por (tema, fuente) antes de estratificar
N_DISTRACTORES = 3

NIVEL_ORDEN = {"principiante": 0, "intermedio": 1, "avanzado": 2}

# --- Paradigmas (el CONJUNTO de candidatos) ---------------------------------
ARTICULOS = ["der", "die", "das", "den", "dem", "des"]

PREP_DATIVO = {"mit", "nach", "aus", "bei", "zu", "von", "seit", "gegenüber"}
PREP_ACUSATIVO = {"für", "ohne", "gegen", "um", "durch", "bis"}
PREP_RIGEN = {**{p: "dativo" for p in PREP_DATIVO},
              **{p: "acusativo" for p in PREP_ACUSATIVO}}

PREFIJOS_SEPARABLES = list(dict.fromkeys([
    "ab", "an", "auf", "aus", "bei", "ein", "los", "mit", "nach", "vor",
    "zu", "zurück", "zusammen", "fort", "her", "hin", "weg", "weiter",
    "um", "durch", "über", "vorbei", "hinab", "hinein", "herein", "hinaus",
    "heraus", "empor",
]))

# --- Metadatos de cada tema (la lección presentada antes de los ejercicios) --
TEMAS = [
    {
        "id": "declinacion",
        "titulo": "Declinación del artículo",
        "nivel": "principiante",
        "resumen": (
            "El artículo definido alemán cambia de forma según el caso "
            "(nominativo para el sujeto, acusativo para el objeto directo, "
            "dativo para el indirecto y tras ciertas preposiciones, genitivo "
            "para la posesión), el género y el número. La tabla completa "
            "tiene 16 casillas pero solo 6 formas distintas: der, die, das, "
            "den, dem, des. Elige la forma que pide la función del "
            "sustantivo en la frase."
        ),
        "tabla": {
            "cabecera": ["Caso", "Masculino", "Femenino", "Neutro", "Plural"],
            "filas": [
                ["Nominativo", "der", "die", "das", "die"],
                ["Acusativo", "den", "die", "das", "die"],
                ["Dativo", "dem", "der", "dem", "den"],
                ["Genitivo", "des", "der", "des", "der"],
            ],
        },
    },
    {
        "id": "conjugacion",
        "titulo": "Conjugación del verbo",
        "nivel": "principiante",
        "resumen": (
            "El verbo finito concuerda en persona y número con el sujeto. "
            "Terminaciones del presente: ich -e, du -st, er/sie/es -t, "
            "wir -en, ihr -t, sie/Sie -en; algunos verbos cambian la vocal "
            "de la raíz en du/er (fahren→fährt, sprechen→sprichst). Hay "
            "verbos irregulares que no cumplen este patrón, como sein "
            "(ich bin, du bist, er ist) o haben (du hast, er hat)."
        ),
        "tabla": {
            "cabecera": ["Persona", "Terminación", "Ejemplo (spielen)"],
            "filas": [
                ["ich", "-e", "spiele"],
                ["du", "-st", "spielst"],
                ["er/sie/es", "-t", "spielt"],
                ["wir / sie / Sie", "-en", "spielen"],
                ["ihr", "-t", "spielt"],
            ],
        },
    },
    {
        "id": "separables",
        "titulo": "Verbos separables",
        "nivel": "principiante",
        "resumen": (
            "Muchos verbos alemanes llevan un prefijo separable (auf-, an-, "
            "vor-, ab-, ein-, hinein-…) que cambia el significado del verbo "
            "base: stehen (estar de pie) → aufstehen (levantarse). En una "
            "oración principal el prefijo se desprende y viaja al final: "
            "aufstehen → «Ich stehe früh auf». Completa con el prefijo que "
            "forma el verbo correcto; la pista te dice cuál es."
        ),
        "tabla": {
            "cabecera": ["Verbo", "Significado", "Prefijo"],
            "filas": [
                ["aufstehen", "levantarse", "auf"],
                ["anrufen", "llamar por teléfono", "an"],
                ["vorbereiten", "preparar", "vor"],
                ["abfahren", "partir / salir", "ab"],
                ["hineingehen", "entrar", "hinein"],
            ],
        },
    },
    {
        "id": "preposicion_caso",
        "titulo": "Preposición y caso",
        "nivel": "intermedio",
        "resumen": (
            "Cada preposición alemana rige un caso fijo: el sustantivo que "
            "la sigue se declina en ese caso. Con dativo: mit, nach, aus, "
            "bei, zu, von, seit. Con acusativo: für, ohne, gegen, um, durch, "
            "bis. En estos ejercicios el artículo que sigue al hueco ya está "
            "declinado: solo una preposición es compatible con ese caso."
        ),
        "tabla": {
            "cabecera": ["Rige dativo", "Rige acusativo"],
            "filas": [
                ["mit, nach, aus", "für, ohne, gegen"],
                ["bei, zu, von, seit", "um, durch, bis"],
            ],
        },
    },
]

CASO_ES = {"Nom": "nominativo", "Acc": "acusativo", "Dat": "dativo", "Gen": "genitivo"}
GENERO_ES = {"Masc": "masculino", "Fem": "femenino", "Neut": "neutro"}
NUMERO_ES = {"Sing": "singular", "Plur": "plural"}


# --- Utilidades vectoriales (el COSENO ordena el pool) -----------------------
def coseno(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def ordenar_por_coseno(nlp, objetivo_vec, candidatos):
    """Ordena `candidatos` (strings) por similitud coseno DESC contra el
    vector objetivo: primero los más parecidos (hard negatives)."""
    puntuados = [(coseno(objetivo_vec, nlp.vocab[c].vector), c) for c in candidatos]
    puntuados.sort(key=lambda x: (-x[0], x[1]))
    return [c for _, c in puntuados]


def con_mayuscula_como(modelo, palabra):
    """Copia la capitalización de `modelo` (p. ej. artículo al inicio de frase)."""
    return palabra.capitalize() if modelo[:1].isupper() else palabra


def hueco(frase, token, respuesta):
    """Parte la frase alrededor del token: (antes, respuesta, despues)."""
    i = token.idx
    return frase[:i], respuesta, frase[i + len(token.text):]


def _token_sustituido(nlp, antes, forma, despues):
    """Re-parsea la frase con `forma` en el hueco y devuelve su token."""
    doc2 = nlp(antes + forma + despues)
    for t2 in doc2:
        if t2.idx == len(antes):
            return t2
    return None


def viola_concordancia(nlp, antes, forma, despues, persona, numero):
    """True si `forma` en el hueco NO es una frase válida: o no es forma
    finita, o su persona/número no concuerdan con el sujeto original. Si
    concuerda en todo (p. ej. mismo verbo en otro tiempo), sería una frase
    correcta y NO sirve como distractor."""
    t2 = _token_sustituido(nlp, antes, forma, despues)
    if t2 is None:
        return False  # tokenización imprevisible: mejor descartarlo
    if "Fin" not in t2.morph.get("VerbForm"):
        return True  # infinitivo/participio en posición finita: agramatical
    return (t2.morph.get("Person") != persona
            or t2.morph.get("Number") != numero)


# --- Generadores por tema ----------------------------------------------------
# Cada generador emite candidatos {antes, respuesta, despues, distractores,
# pista} para una frase ya parseada. `ctx` lleva nlp y los índices del léxico.

def gen_declinacion(ctx, frase, doc):
    nlp = ctx["nlp"]
    for t in doc:
        if t.pos_ != "DET" or t.lemma_ != "der":
            continue
        base = normalizar(t.text)
        if base not in ARTICULOS:
            continue
        caso = t.morph.get("Case")
        genero = t.morph.get("Gender")
        numero = t.morph.get("Number")
        pool = [con_mayuscula_como(t.text, a) for a in ARTICULOS if a != base]
        distractores = ordenar_por_coseno(nlp, t.vector, pool)[:N_DISTRACTORES]
        partes = [CASO_ES.get(caso[0]) if caso else None,
                  GENERO_ES.get(genero[0]) if genero else None,
                  NUMERO_ES.get(numero[0]) if numero else None]
        pista = " · ".join(p for p in partes if p)
        antes, resp, despues = hueco(frase, t, t.text)
        yield {
            "antes": antes, "respuesta": resp, "despues": despues,
            "distractores": distractores,
            "pista": (pista.capitalize() if pista else "Artículo definido") + ".",
        }


def gen_preposicion(ctx, frase, doc):
    nlp = ctx["nlp"]
    for t in doc:
        if t.pos_ != "ADP":
            continue
        base = normalizar(t.text)
        if base not in PREP_RIGEN:
            continue
        # El caso debe ser VISIBLE en el sintagma (artículo, adjetivo declinado
        # o pronombre): sin marca («um sieben Uhr») cualquier preposición del
        # otro caso también daría una frase válida y el cloze sería ambiguo.
        if not any(c is not t and c.pos_ in ("DET", "ADJ", "PRON")
                   and c.morph.get("Case") for c in t.subtree):
            continue
        # Pool = preposiciones del CASO OPUESTO: el artículo declinado que
        # sigue al hueco las descarta, así la respuesta es única por gramática.
        caso = PREP_RIGEN[base]
        rivales = PREP_ACUSATIVO if caso == "dativo" else PREP_DATIVO
        pool = [con_mayuscula_como(t.text, p) for p in rivales]
        distractores = ordenar_por_coseno(nlp, t.vector, pool)[:N_DISTRACTORES]
        antes, resp, despues = hueco(frase, t, t.text)
        yield {
            "antes": antes, "respuesta": resp, "despues": despues,
            "distractores": distractores,
            "pista": f"«{base}» rige {caso}: mira el caso del artículo que sigue al hueco.",
        }


def gen_conjugacion(ctx, frase, doc):
    nlp = ctx["nlp"]
    for t in doc:
        if t.pos_ not in ("VERB", "AUX"):
            continue
        if "Fin" not in t.morph.get("VerbForm"):
            continue
        base = normalizar(t.text)
        otras = [f for f in ctx["formas_por_lema"].get(t.lemma_, ()) if f != base]
        if len(otras) < N_DISTRACTORES:
            continue  # sin paradigma suficiente en el corpus
        persona = t.morph.get("Person")
        numero = t.morph.get("Number")
        antes, resp, despues = hueco(frase, t, t.text)
        # Coseno ordena; la sustitución valida: solo cuentan las formas que
        # rompen la concordancia (las que concuerdan serían frases válidas).
        distractores = []
        for f in ordenar_por_coseno(nlp, t.vector, otras):
            forma = con_mayuscula_como(t.text, f)
            if viola_concordancia(nlp, antes, forma, despues, persona, numero):
                distractores.append(forma)
            if len(distractores) == N_DISTRACTORES:
                break
        if len(distractores) < N_DISTRACTORES:
            continue
        etiqueta = " ".join(e for e in (
            f"{persona[0]}ª persona" if persona else "",
            NUMERO_ES.get(numero[0], "") if numero else "",
        ) if e)
        yield {
            "antes": antes, "respuesta": resp, "despues": despues,
            "distractores": distractores,
            "pista": ((etiqueta or f"Conjuga «{t.lemma_}»")
                      + f" · verbo «{t.lemma_}»."),
        }


def gen_separables(ctx, frase, doc):
    nlp = ctx["nlp"]
    for t in doc:
        if t.dep_ != "svp":
            continue
        base = normalizar(t.text)
        verbo = base + t.head.lemma_  # reconstrucción del lema (vor+bereiten)
        # La respuesta debe formar un verbo atestiguado en el léxico: descarta
        # los svp espurios del parser («gab die Hand darauf» ≠ *daraufgeben).
        if normalizar(verbo) not in ctx["lemas"]:
            continue
        # Se excluyen los prefijos que forman OTRO verbo atestiguado en el
        # corpus (aufmachen vs zumachen: ambos válidos → zu no puede ser
        # distractor de auf). Lo no atestiguado se asume agramatical.
        pool = [p for p in PREFIJOS_SEPARABLES
                if p != base and (p + t.head.lemma_) not in ctx["lemas"]]
        distractores = ordenar_por_coseno(nlp, t.vector, pool)[:N_DISTRACTORES]
        if len(distractores) < N_DISTRACTORES:
            continue
        antes, resp, despues = hueco(frase, t, t.text)
        yield {
            "antes": antes, "respuesta": resp, "despues": despues,
            "distractores": distractores,
            "pista": f"Verbo separable «{verbo}»: el prefijo va al final.",
        }


GENERADORES = {
    "declinacion": gen_declinacion,
    "conjugacion": gen_conjugacion,
    "separables": gen_separables,
    "preposicion_caso": gen_preposicion,
}


# --- Corpus e índices ---------------------------------------------------------
def indices_lexico():
    """Del léxico global: lema alemán -> {formas vistas} y el set de lemas."""
    lexico = json.loads(RUTA_LEXICO.read_text(encoding="utf-8"))
    formas = {}
    lemas = set()
    for clave, entrada in lexico.items():
        if not clave.startswith("de:"):
            continue
        forma = clave.split(":", 1)[1]
        lema = entrada["lemma"]
        formas.setdefault(lema, set()).add(forma)
        lemas.add(normalizar(lema))
    return formas, lemas


def frases_alemanas():
    """(frase, fuente, nivel) de todas las lecturas con cuerpo en alemán."""
    for ruta in sorted(DIR_LECTURAS.glob("*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        frases = datos.get("cuerpo", {}).get("de")
        if not frases:
            continue
        nivel = datos.get("nivel", "avanzado")
        titulo = datos.get("titulo", {}).get("es") or datos.get("titulo", {}).get("de", ruta.stem)
        fuente = f"{nivel} · {titulo}".strip(" ·")
        for frase in frases:
            yield frase, fuente, nivel


def estratificar(por_fuente, orden_fuentes, tope):
    """Round-robin entre fuentes (ya ordenadas) hasta `tope` ejercicios:
    todas las lecturas aportan antes de que una fuente repita."""
    colas = {f: list(por_fuente[f]) for f in orden_fuentes}
    salida = []
    while len(salida) < tope and any(colas.values()):
        for f in orden_fuentes:
            if colas[f] and len(salida) < tope:
                salida.append(colas[f].pop(0))
    return salida


def generar(temas):
    print(f"Cargando spaCy ({MODELO})...")
    nlp = spacy.load(MODELO)
    formas_por_lema, lemas = indices_lexico()
    ctx = {"nlp": nlp, "formas_por_lema": formas_por_lema, "lemas": lemas}

    candidatos = {t: {} for t in temas}   # tema -> fuente -> [ejercicio]
    vistos = {t: set() for t in temas}    # dedupe por (antes, respuesta, despues)
    nivel_de = {}                          # fuente -> nivel (para ordenar)

    for frase, fuente, nivel in frases_alemanas():
        if len(frase.split()) > MAX_TOKENS:
            continue  # prefiltro barato antes de parsear
        doc = nlp(frase)
        if len(doc) > MAX_TOKENS + 6:
            continue
        nivel_de[fuente] = nivel
        for tema in temas:
            cola = candidatos[tema].setdefault(fuente, [])
            if len(cola) >= MAX_POR_FUENTE:
                continue
            for ej in GENERADORES[tema](ctx, frase, doc):
                clave = (ej["antes"], ej["respuesta"], ej["despues"])
                if clave in vistos[tema] or not ej["distractores"]:
                    continue
                vistos[tema].add(clave)
                ej["fuente"] = fuente
                ej["nivel"] = nivel
                cola.append(ej)
                if len(cola) >= MAX_POR_FUENTE:
                    break

    ejercicios = {}
    for tema in temas:
        orden = sorted(candidatos[tema],
                       key=lambda f: (NIVEL_ORDEN.get(nivel_de.get(f), 9), f))
        elegidos = estratificar(candidatos[tema], orden, TOPE_POR_TEMA)
        # Orden pedagógico de salida: primero las lecturas fáciles, agrupadas
        # por lectura (la estratificación ya decidió CUÁLES entran; esto solo
        # decide en qué orden se presentan).
        elegidos.sort(key=lambda e: (NIVEL_ORDEN.get(e["nivel"], 9), e["fuente"]))
        for i, ej in enumerate(elegidos, start=1):
            ej["id"] = f"{tema}-{i:02d}"
        ejercicios[tema] = elegidos

    salida = {
        "_nota": (
            "Generado por pipeline/gramatica.py (spaCy + distractores híbridos "
            "paradigma/coseno). Editar a mano se pierde al regenerar."
        ),
        "temas": [t for t in TEMAS if t["id"] in temas],
        "ejercicios": ejercicios,
    }
    RUTA_SALIDA.write_text(
        json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for tema in temas:
        fuentes = sorted({e["fuente"] for e in ejercicios[tema]})
        print(f"  {tema:18} {len(ejercicios[tema]):3} ejercicios de {len(fuentes)} fuentes")
    print(f"-> {RUTA_SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    pedidos = sys.argv[1:] or list(GENERADORES)
    desconocidos = [t for t in pedidos if t not in GENERADORES]
    if desconocidos:
        raise SystemExit(f"Temas desconocidos: {desconocidos}. Opciones: {list(GENERADORES)}")
    generar(pedidos)
