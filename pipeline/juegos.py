"""Emite src/data/juegos.json: datos de la Sección 4 (juegos de palabras).

La salida está indexada por idioma de estudio: {"de": {...}, "en": {...}}. Cada
bloque de idioma tiene los mismos pools (los algoritmos viven en src/engine/,
aquí solo se seleccionan las palabras):

- Escalera/Wordle: formas del léxico con su traducción, longitudes 3-5, solo
  ASCII (en alemán descarta umlauts/ß para que el alumno hispanohablante pueda
  teclearlas; el inglés ya es ASCII). Grafo de Hamming 1, BFS y entropía viven
  en src/engine/escalera.js y wordle.js.
- Crucigrama/Sopa: lemas de contenido del corpus (sin palabras funcionales,
  atestiguados >= 2 veces) con la traducción española como pista.
- Sudoku de palabras: palabras de 9 letras TODAS DISTINTAS (formas o lemas,
  ASCII) con glosa: los 9 símbolos del sudoku. La generación (backtracking +
  excavado con unicidad) vive en src/engine/sudoku.js.

Además, los MISMOS pools POR LECTURA (agrupando las partes de un libro por
título, como hace gramatica.py): el frontend deja jugar con el vocabulario
de una lectura concreta y src/engine/juegos.js decide qué juegos aguanta
cada una.

Re-ejecutar al añadir lecturas (cambian léxico, frecuencias y pools).

Uso:  PYTHONUTF8=1 python juegos.py
"""
import json
import re
import unicodedata
from pathlib import Path

from procesar import RAIZ, RUTA_LEXICO, normalizar

DIR_LECTURAS = RAIZ / "src" / "data" / "lecturas"

# Mismo criterio de palabra que frecuencias.py / tokenizar() del frontend.
RE_PALABRA = re.compile(r"[^\W\d_][\w'’-]*", re.UNICODE)

NIVEL_ORDEN = {"principiante": 0, "intermedio": 1, "avanzado": 2}

RUTA_FRECUENCIAS = RAIZ / "src" / "data" / "frecuencias.json"
RUTA_JUEGOS = RAIZ / "src" / "data" / "juegos.json"

IDIOMAS = ("de", "en")

RE_ASCII = re.compile(r"[a-z]+")
LONGITUDES_ESCALERA = (3, 4, 5)
LONGITUD_CRUCIGRAMA = (4, 9)  # min, max
FRECUENCIA_MINIMA = 2  # el lema debe estar atestiguado más de una vez (pool global)
MAX_CRUCIGRAMA = 400
MAX_CRUCIGRAMA_LECTURA = 120  # por lectura basta un pool corto (se barajan 30)

# Palabras funcionales por idioma: gramaticalmente imprescindibles pero malas
# entradas de crucigrama (la pista «el / la» no enseña nada). Listas curadas.
FUNCIONALES = {
    "de": {
        # artículos, pronombres y determinantes
        "der", "die", "das", "ein", "eine", "einer", "eines", "kein", "keiner",
        "ich", "du", "er", "sie", "es", "wir", "ihr", "man", "sich", "wer", "was",
        "mein", "dein", "sein", "unser", "euer", "dieser", "jener", "jeder",
        "mancher", "solcher", "welcher", "alle", "aller", "beide", "etwas",
        "nichts", "jemand", "niemand", "einige", "anderer", "all", "derselbe",
        "derjenige", "einander", "irgendein", "irgendwer",
        # preposiciones
        "in", "an", "auf", "aus", "bei", "mit", "nach", "seit", "von", "zu",
        "durch", "ohne", "um", "gegen", "bis", "über", "unter", "vor", "hinter",
        "neben", "zwischen", "für", "wegen", "während", "trotz", "statt", "ab",
        "entlang", "gegenüber", "innerhalb", "außerhalb",
        # conjunciones y partículas
        "und", "oder", "aber", "doch", "denn", "sondern", "dass", "ob", "als",
        "wenn", "weil", "obwohl", "damit", "sodass", "sowie", "sowohl", "weder",
        "noch", "nicht", "auch", "nur", "schon", "sehr", "so", "dann", "da",
        "hier", "dort", "ja", "nein", "mal", "wohl", "zwar", "etwa", "eben",
        "halt", "gar", "erst", "wieder", "immer", "nie", "oft", "bald", "jetzt",
        "nun", "heute", "gestern", "morgen", "wie", "wo", "wann", "warum",
        "wohin", "woher", "je", "desto", "sogar", "beinahe", "fast", "ganz",
        # auxiliares y modales
        "sein", "haben", "werden", "können", "müssen", "wollen", "sollen",
        "dürfen", "mögen", "lassen",
    },
    "en": {
        # artículos y determinantes
        "the", "a", "an", "this", "that", "these", "those", "some", "any", "no",
        "every", "each", "all", "both", "either", "neither", "much", "many",
        "more", "most", "few", "little", "less", "several", "such", "another",
        "other", "same", "own", "enough",
        # pronombres y posesivos
        "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
        "them", "my", "your", "his", "its", "our", "their", "mine", "yours",
        "hers", "ours", "theirs", "myself", "yourself", "himself", "herself",
        "itself", "ourselves", "themselves", "who", "whom", "whose", "which",
        "one", "ones", "someone", "somebody", "something", "anyone", "anybody",
        "anything", "everyone", "everybody", "everything", "nobody", "nothing",
        "none",
        # preposiciones
        "in", "on", "at", "to", "of", "for", "with", "by", "from", "up", "down",
        "over", "under", "above", "below", "into", "onto", "upon", "about",
        "against", "between", "among", "amongst", "through", "throughout",
        "during", "before", "after", "since", "until", "till", "within",
        "without", "along", "across", "behind", "beside", "besides", "near",
        "off", "out", "around", "round", "toward", "towards", "per", "amid",
        "beneath", "beyond", "despite", "unto",
        # conjunciones y partículas
        "and", "or", "but", "nor", "so", "yet", "if", "then", "than", "as",
        "because", "although", "though", "while", "whilst", "whereas", "unless",
        "whether", "when", "where", "why", "how", "once", "not", "only", "just",
        "even", "also", "too", "very", "quite", "rather", "still", "again",
        "ever", "never", "always", "often", "sometimes", "soon", "now", "here",
        "there", "thus", "hence", "therefore", "however", "indeed", "perhaps",
        "maybe", "almost", "already", "yes",
        # auxiliares y modales
        "be", "is", "am", "are", "was", "were", "been", "being", "have", "has",
        "had", "having", "do", "does", "did", "done", "doing", "will", "would",
        "shall", "should", "can", "could", "may", "might", "must", "ought",
        "need", "dare", "let", "get", "got",
    },
}


def slug_de(titulo):
    """Mismo slug que slugDeLectura en src/engine/gramatica.js."""
    s = unicodedata.normalize("NFD", str(titulo))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def es_palabra_sudoku(palabra):
    """9 letras ASCII, todas distintas: los 9 símbolos de un sudoku."""
    return bool(RE_ASCII.fullmatch(palabra)) and len(palabra) == 9 and len(set(palabra)) == 9


def pools(formas, lexico, glosa_lema, frecuencias, idioma):
    """(escalera, crucigrama, sudoku) para un conjunto de formas de un idioma.

    escalera: forma ASCII L=3-5 -> glosa (para escalera y Wordle).
    crucigrama: lemas de contenido atestiguados en esas formas, con pista
    (para crucigrama y sopa), ordenados por frecuencia global descendente.
    sudoku: palabras (formas o lemas) de 9 letras todas distintas, con glosa.
    """
    escalera = {str(n): {} for n in LONGITUDES_ESCALERA}
    lemas = set()
    sudoku = {}
    for forma in formas:
        entrada = lexico.get(forma)
        if not entrada:
            continue
        es = (entrada.get("es") or "").strip()
        if es and RE_ASCII.fullmatch(forma) and len(forma) in LONGITUDES_ESCALERA:
            escalera[str(len(forma))][forma] = es
        if es and es_palabra_sudoku(forma):
            sudoku.setdefault(forma, es)
        lema = normalizar(entrada.get("lemma") or "")
        if lema:
            lemas.add(lema)
            if lema in glosa_lema and es_palabra_sudoku(lema):
                sudoku.setdefault(lema, glosa_lema[lema])

    lo, hi = LONGITUD_CRUCIGRAMA
    funcionales = FUNCIONALES[idioma]
    candidatos = [
        (frecuencias.get(f"{idioma}:{lema}", 0), lema, glosa_lema[lema])
        for lema in lemas
        if lema in glosa_lema
        and RE_ASCII.fullmatch(lema)
        and lo <= len(lema) <= hi
        and lema not in funcionales
    ]
    candidatos.sort(key=lambda t: (-t[0], t[1]))
    crucigrama = [{"palabra": lema, "pista": es} for _, lema, es in candidatos]
    escalera = {n: dict(sorted(d.items())) for n, d in escalera.items()}
    sudoku = [{"palabra": p, "pista": sudoku[p]} for p in sorted(sudoku)]
    return escalera, crucigrama, sudoku


def construir_idioma(idioma, lexico, frecuencias):
    """Bloque de juegos.json para un idioma: pools globales + por lectura."""
    # Léxico del idioma forma -> entrada, y glosa por lema (prefiere forma == lema).
    lexico_idioma = {}
    glosa_lema = {}
    for clave, entrada in sorted(lexico.items()):
        lang, forma = clave.split(":", 1)
        if lang != idioma:
            continue
        forma = forma.lower()
        lexico_idioma[forma] = entrada
        es = (entrada.get("es") or "").strip()
        lema = normalizar(entrada.get("lemma") or "")
        if es and lema and (forma == lema or lema not in glosa_lema):
            glosa_lema[lema] = es

    # --- Pools globales (todo el corpus del idioma) ------------------------
    escalera, crucigrama_todo, sudoku = pools(
        lexico_idioma.keys(), lexico_idioma, glosa_lema, frecuencias, idioma
    )
    crucigrama = [
        e for e in crucigrama_todo
        if frecuencias.get(f"{idioma}:{e['palabra']}", 0) >= FRECUENCIA_MINIMA
    ][:MAX_CRUCIGRAMA]

    # --- Pools por lectura (partes de un libro agrupadas por título) --------
    grupos = {}  # (orden nivel, titulo) -> {"formas": set, meta}
    for ruta in sorted(DIR_LECTURAS.glob("*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        frases = datos.get("cuerpo", {}).get(idioma)
        if not frases:
            continue
        nivel = datos.get("nivel", "avanzado")
        titulos = datos.get("titulo", {})
        titulo = titulos.get(idioma) or titulos.get("es") or ruta.stem
        clave = (NIVEL_ORDEN.get(nivel, 9), titulo)
        g = grupos.setdefault(clave, {"titulo": titulo, "nivel": nivel, "formas": set()})
        override = datos.get("lexico", {})
        for frase in frases:
            for m in RE_PALABRA.finditer(frase):
                forma = normalizar(m.group())
                if forma:
                    g["formas"].add(forma)
        # El override por lectura manda sobre el léxico global (como el Lector);
        # solo afecta a la glosa, la clave sigue siendo la forma normalizada.
        for k, entrada in override.items():
            if k.startswith(f"{idioma}:"):
                g.setdefault("override", {})[k.split(":", 1)[1].lower()] = entrada

    lecturas = []
    for (_, _), g in sorted(grupos.items()):
        lexico_local = {**lexico_idioma, **g.get("override", {})}
        esc, cru, sud = pools(g["formas"], lexico_local, glosa_lema, frecuencias, idioma)
        lecturas.append({
            "slug": slug_de(g["titulo"]),
            "titulo": g["titulo"],
            "nivel": g["nivel"],
            "escalera": esc,
            "crucigrama": cru[:MAX_CRUCIGRAMA_LECTURA],
            "sudoku": sud,
        })

    return {
        "escalera": escalera,
        "crucigrama": crucigrama,
        "sudoku": sudoku,
        "lecturas": lecturas,
    }


def construir():
    lexico = json.loads(RUTA_LEXICO.read_text(encoding="utf-8"))
    frecuencias = json.loads(RUTA_FRECUENCIAS.read_text(encoding="utf-8"))["lemas"]

    salida = {idioma: construir_idioma(idioma, lexico, frecuencias) for idioma in IDIOMAS}

    RUTA_JUEGOS.write_text(
        json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    for idioma in IDIOMAS:
        bloque = salida[idioma]
        esc = bloque["escalera"]
        resumen = ", ".join(f"L={n}: {len(esc[str(n)])}" for n in LONGITUDES_ESCALERA)
        print(f"[{idioma}] corpus: escalera ({resumen})  "
              f"crucigrama: {len(bloque['crucigrama'])}  sudoku: {len(bloque['sudoku'])}")
        for lec in bloque["lecturas"]:
            tam = ", ".join(f"L={n}: {len(lec['escalera'][str(n)])}" for n in LONGITUDES_ESCALERA)
            print(f"  {lec['nivel']:<12} {lec['titulo']:<30} escalera({tam})  "
                  f"crucigrama: {len(lec['crucigrama'])}  sudoku: {len(lec['sudoku'])}")
    print(f"-> {RUTA_JUEGOS.relative_to(RAIZ)}")


if __name__ == "__main__":
    construir()
