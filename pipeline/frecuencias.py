"""Emite src/data/frecuencias.json: conteo de lemas en el corpus de lecturas.

Alimenta el modelo de conocimiento del frontend (src/engine/conocimiento.js):
el prior P(conocer) de una palabra nunca vista es una logística sobre su
escala Zipf, zipf = log10(conteo/total × 10^6).

No necesita spaCy: reutiliza el mapa forma→lemma de lexico.json, que ya se
construyó con spaCy sobre este mismo corpus (construir_lexico.py). Los tokens
sin entrada en el léxico cuentan por su forma normalizada.

Uso:  PYTHONUTF8=1 python frecuencias.py
"""
import json
import re
from collections import Counter
from pathlib import Path

from procesar import normalizar, RAIZ, RUTA_LEXICO

DIR_LECTURAS = RAIZ / "src" / "data" / "lecturas"
RUTA_FRECUENCIAS = RAIZ / "src" / "data" / "frecuencias.json"

# Mismo criterio de palabra que tokenizar() en el frontend: letra inicial,
# luego letras/apóstrofos/guiones.
RE_PALABRA = re.compile(r"[^\W\d_][\w'’-]*", re.UNICODE)


def contar():
    lexico = json.loads(RUTA_LEXICO.read_text(encoding="utf-8"))
    conteos = Counter()
    totales = Counter()

    for ruta in sorted(DIR_LECTURAS.glob("*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        for idioma in ("de", "en"):
            frases = datos.get("cuerpo", {}).get(idioma)
            if not frases:
                continue
            # El override por lectura desambigua (p. ej. "nahm" → annehmen);
            # manda sobre el léxico global, igual que en el Lector.
            override = datos.get("lexico", {})
            for frase in frases:
                for m in RE_PALABRA.finditer(frase):
                    forma = normalizar(m.group())
                    if not forma:
                        continue
                    clave = f"{idioma}:{forma}"
                    entrada = override.get(clave) or lexico.get(clave)
                    lema = normalizar(entrada["lemma"]) if entrada else forma
                    conteos[f"{idioma}:{lema}"] += 1
                    totales[idioma] += 1

    salida = {
        "totales": dict(totales),
        "lemas": dict(sorted(conteos.items())),
    }
    RUTA_FRECUENCIAS.write_text(
        json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    print(f"tokens: {dict(totales)}  lemas distintos: {len(conteos)}")
    for idioma in totales:
        top = [k for k, _ in conteos.most_common(200) if k.startswith(idioma)][:8]
        resumen = ", ".join(k.split(":", 1)[1] + "=" + str(conteos[k]) for k in top)
        print(f"  top {idioma}: {resumen}")
    print(f"-> {RUTA_FRECUENCIAS.relative_to(RAIZ)}")


if __name__ == "__main__":
    contar()
