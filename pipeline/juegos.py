"""Emite src/data/juegos.json: datos de la Sección 4 (juegos de palabras).

Dos juegos del frontend consumen este JSON (los algoritmos viven en
src/engine/, aquí solo se seleccionan las palabras del corpus):

- Escalera de palabras (BFS): formas alemanas del léxico con su traducción,
  longitudes 3-5. Solo ASCII (sin umlauts ni ß) para que el alumno
  hispanohablante pueda teclearlas. El grafo de Hamming 1 y la búsqueda del
  camino mínimo se construyen en src/engine/escalera.js.
- Crucigrama (backtracking): lemas de contenido del corpus (sin palabras
  funcionales, atestiguados >= 2 veces en las lecturas) con la traducción
  española como pista. La colocación por backtracking vive en
  src/engine/crucigrama.js.

Re-ejecutar al añadir lecturas (cambian léxico y frecuencias).

Uso:  PYTHONUTF8=1 python juegos.py
"""
import json
import re

from procesar import RAIZ, RUTA_LEXICO

RUTA_FRECUENCIAS = RAIZ / "src" / "data" / "frecuencias.json"
RUTA_JUEGOS = RAIZ / "src" / "data" / "juegos.json"

RE_ASCII = re.compile(r"[a-z]+")
LONGITUDES_ESCALERA = (3, 4, 5)
LONGITUD_CRUCIGRAMA = (4, 9)  # min, max
FRECUENCIA_MINIMA = 2  # el lema debe estar atestiguado más de una vez
MAX_CRUCIGRAMA = 400

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


def construir():
    lexico = json.loads(RUTA_LEXICO.read_text(encoding="utf-8"))
    frecuencias = json.loads(RUTA_FRECUENCIAS.read_text(encoding="utf-8"))["lemas"]

    escalera = {str(n): {} for n in LONGITUDES_ESCALERA}
    glosa_lema = {}  # lema -> es (prefiere la entrada cuya forma ES el lema)

    for clave, entrada in sorted(lexico.items()):
        idioma, forma = clave.split(":", 1)
        if idioma != "de":
            continue
        forma = forma.lower()
        es = (entrada.get("es") or "").strip()
        lema = (entrada.get("lemma") or "").lower()
        if not es:
            continue
        if RE_ASCII.fullmatch(forma) and len(forma) in LONGITUDES_ESCALERA:
            escalera[str(len(forma))][forma] = es
        if lema and (forma == lema or lema not in glosa_lema):
            glosa_lema[lema] = es

    lo, hi = LONGITUD_CRUCIGRAMA
    candidatos = [
        (frecuencias.get(f"de:{lema}", 0), lema, es)
        for lema, es in glosa_lema.items()
        if RE_ASCII.fullmatch(lema)
        and lo <= len(lema) <= hi
        and lema not in FUNCIONALES
        and frecuencias.get(f"de:{lema}", 0) >= FRECUENCIA_MINIMA
    ]
    candidatos.sort(key=lambda t: (-t[0], t[1]))
    crucigrama = [
        {"palabra": lema, "pista": es}
        for _, lema, es in candidatos[:MAX_CRUCIGRAMA]
    ]

    salida = {"escalera": escalera, "crucigrama": crucigrama}
    RUTA_JUEGOS.write_text(
        json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    resumen = ", ".join(f"L={n}: {len(escalera[str(n)])}" for n in LONGITUDES_ESCALERA)
    print(f"escalera ({resumen})  crucigrama: {len(crucigrama)} entradas")
    print(f"-> {RUTA_JUEGOS.relative_to(RAIZ)}")


if __name__ == "__main__":
    construir()
