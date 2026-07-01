"""Diagnóstico de cobertura: clasifica las formas sin traducción por categoría
gramatical (POS) para saber qué atacar. Uso: PYTHONUTF8=1 python diagnostico.py"""
from collections import Counter

import spacy

from traductor import Traductor
from procesar import (
    CONFIG, MODELO, extraer_contenido, limpiar_texto,
    normalizar, lemas_con_separables,
)

nlp = spacy.load(MODELO)
tr = Traductor()
contenido = limpiar_texto(extraer_contenido(CONFIG["archivo"], CONFIG["inicio"]))
nlp.max_length = max(nlp.max_length, len(contenido) + 100)
doc = nlp(contenido)
lemas = lemas_con_separables(doc)

vistas = set()
total = con = 0
fallos_pos = Counter()
ejemplos = {}
for t in doc:
    if not t.is_alpha:
        continue
    clave = normalizar(t.text)
    if not clave or clave in vistas:
        continue
    vistas.add(clave)
    total += 1
    if tr.traducir(lemas[t.i], t.text):
        con += 1
    else:
        fallos_pos[t.pos_] += 1
        ejemplos.setdefault(t.pos_, []).append(f"{t.text}({lemas[t.i]})")

print(f"total formas: {total}   con traducción: {con} ({100*con//total}%)   fallan: {total-con}")
print("fallos por POS:")
for pos, c in fallos_pos.most_common():
    print(f"  {pos:6} {c:5}   ej: {', '.join(ejemplos[pos][:8])}")
