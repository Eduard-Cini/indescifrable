"""Emite src/data/juegos.json: datos de la Sección 4 (juegos de palabras).

Dos pools globales del corpus (los algoritmos viven en src/engine/, aquí
solo se seleccionan las palabras):

- Escalera/Wordle: formas alemanas del léxico con su traducción, longitudes
  3-5. Solo ASCII (sin umlauts ni ß) para que el alumno hispanohablante
  pueda teclearlas. El grafo de Hamming 1, el BFS y la entropía viven en
  src/engine/escalera.js y wordle.js.
- Crucigrama/Sopa: lemas de contenido del corpus (sin palabras funcionales,
  atestiguados >= 2 veces) con la traducción española como pista.

Además, los MISMOS pools POR LECTURA (agrupando las partes de un libro por
título, como hace gramatica.py): el frontend deja jugar con el vocabulario
de una lectura concreta y src/engine/juegos.js decide qué juegos aguanta
cada una (una lectura de principiante rara vez tiene grafo de escalera,
pero casi siempre da para sopa o crucigrama).

Re-ejecutar al añadir lecturas (cambian léxico, frecuencias y pools).

Uso:  PYTHONUTF8=1 python juegos.py
"""
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from procesar import RAIZ, RUTA_LEXICO, normalizar

DIR_LECTURAS = RAIZ / "src" / "data" / "lecturas"

# Mismo criterio de palabra que frecuencias.py / tokenizar() del frontend.
RE_PALABRA = re.compile(r"[^\W\d_][\w'’-]*", re.UNICODE)

NIVEL_ORDEN = {"principiante": 0, "intermedio": 1, "avanzado": 2}

RUTA_FRECUENCIAS = RAIZ / "src" / "data" / "frecuencias.json"
RUTA_JUEGOS = RAIZ / "src" / "data" / "juegos.json"

RE_ASCII = re.compile(r"[a-z]+")
LONGITUDES_ESCALERA = (3, 4, 5)
LONGITUD_CRUCIGRAMA = (4, 9)  # min, max
FRECUENCIA_MINIMA = 2  # el lema debe estar atestiguado más de una vez (pool global)
MAX_CRUCIGRAMA = 400
MAX_CRUCIGRAMA_LECTURA = 120  # por lectura basta un pool corto (se barajan 30)

# Palabras funcionales del alemán: gramaticalmente imprescindibles pero malas
# entradas de crucigrama (la pista «el / la» no enseña nada). Lista curada.
FUNCIONALES = {
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
}


def slug_de(titulo):
    """Mismo slug que slugDeLectura en src/engine/gramatica.js."""
    s = unicodedata.normalize("NFD", str(titulo))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def pools_de(formas, lexico_de, glosa_lema, frecuencias):
    """(escalera, crucigrama) para un conjunto de formas alemanas.

    escalera: forma ASCII L=3-5 -> glosa (para escalera y Wordle).
    crucigrama: lemas de contenido atestiguados en esas formas, con pista
    (para crucigrama y sopa), ordenados por frecuencia global descendente.
    """
    escalera = {str(n): {} for n in LONGITUDES_ESCALERA}
    lemas = set()
    for forma in formas:
        entrada = lexico_de.get(forma)
        if not entrada:
            continue
        es = (entrada.get("es") or "").strip()
        if es and RE_ASCII.fullmatch(forma) and len(forma) in LONGITUDES_ESCALERA:
            escalera[str(len(forma))][forma] = es
        lema = normalizar(entrada.get("lemma") or "")
        if lema:
            lemas.add(lema)

    lo, hi = LONGITUD_CRUCIGRAMA
    candidatos = [
        (frecuencias.get(f"de:{lema}", 0), lema, glosa_lema[lema])
        for lema in lemas
        if lema in glosa_lema
        and RE_ASCII.fullmatch(lema)
        and lo <= len(lema) <= hi
        and lema not in FUNCIONALES
    ]
    candidatos.sort(key=lambda t: (-t[0], t[1]))
    crucigrama = [{"palabra": lema, "pista": es} for _, lema, es in candidatos]
    escalera = {n: dict(sorted(d.items())) for n, d in escalera.items()}
    return escalera, crucigrama


def construir():
    lexico = json.loads(RUTA_LEXICO.read_text(encoding="utf-8"))
    frecuencias = json.loads(RUTA_FRECUENCIAS.read_text(encoding="utf-8"))["lemas"]

    # Léxico alemán forma -> entrada, y glosa por lema (prefiere forma == lema).
    lexico_de = {}
    glosa_lema = {}
    for clave, entrada in sorted(lexico.items()):
        idioma, forma = clave.split(":", 1)
        if idioma != "de":
            continue
        forma = forma.lower()
        lexico_de[forma] = entrada
        es = (entrada.get("es") or "").strip()
        lema = normalizar(entrada.get("lemma") or "")
        if es and lema and (forma == lema or lema not in glosa_lema):
            glosa_lema[lema] = es

    # --- Pools globales (todo el corpus) -----------------------------------
    escalera, crucigrama_todo = pools_de(
        lexico_de.keys(), lexico_de, glosa_lema, frecuencias
    )
    crucigrama = [
        e for e in crucigrama_todo
        if frecuencias.get(f"de:{e['palabra']}", 0) >= FRECUENCIA_MINIMA
    ][:MAX_CRUCIGRAMA]

    # --- Pools por lectura (partes de un libro agrupadas por título) --------
    grupos = {}  # (orden nivel, titulo de) -> {"formas": set, meta}
    for ruta in sorted(DIR_LECTURAS.glob("*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        frases = datos.get("cuerpo", {}).get("de")
        if not frases:
            continue
        nivel = datos.get("nivel", "avanzado")
        titulo = datos.get("titulo", {}).get("de") or datos.get("titulo", {}).get("es", ruta.stem)
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
            if k.startswith("de:"):
                g.setdefault("override", {})[k.split(":", 1)[1].lower()] = entrada

    lecturas = []
    for (_, _), g in sorted(grupos.items()):
        lexico_local = {**lexico_de, **g.get("override", {})}
        esc, cru = pools_de(g["formas"], lexico_local, glosa_lema, frecuencias)
        lecturas.append({
            "slug": slug_de(g["titulo"]),
            "titulo": g["titulo"],
            "nivel": g["nivel"],
            "escalera": esc,
            "crucigrama": cru[:MAX_CRUCIGRAMA_LECTURA],
        })

    salida = {"escalera": escalera, "crucigrama": crucigrama, "lecturas": lecturas}
    RUTA_JUEGOS.write_text(
        json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    resumen = ", ".join(f"L={n}: {len(escalera[str(n)])}" for n in LONGITUDES_ESCALERA)
    print(f"corpus: escalera ({resumen})  crucigrama: {len(crucigrama)} entradas")
    for lec in lecturas:
        tam = ", ".join(f"L={n}: {len(lec['escalera'][str(n)])}" for n in LONGITUDES_ESCALERA)
        print(f"  {lec['nivel']:<12} {lec['titulo']:<28} escalera({tam})  crucigrama: {len(lec['crucigrama'])}")
    print(f"-> {RUTA_JUEGOS.relative_to(RAIZ)}")


if __name__ == "__main__":
    construir()
