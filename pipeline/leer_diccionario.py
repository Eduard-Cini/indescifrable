"""Parsea un diccionario FreeDict (TEI) a un mapa lema -> acepciones POR CATEGORÍA.

FreeDict (https://freedict.org) publica un `<entry>` distinto para cada
categoría gramatical de una misma palabra: «bone» aparece como adj (osiforme),
n (hueso) y v (deshuesar). Guardar solo la primera entrada del archivo elegía
la categoría por azar del orden — de ahí traducciones como bone -> «osiforme»
o crystal -> «cristalino».

Por eso aquí se conservan TODAS las acepciones con su categoría, y quien
traduce elige la que concuerda con el análisis morfológico de spaCy
(ver traductor.py). Licencia de cada diccionario: ver su COPYING.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

TEI = Path(__file__).parent / "diccionarios" / "deu-spa" / "deu-spa.tei"
NS = "{http://www.tei-c.org/ns/1.0}"

# Categoría de spaCy -> categoría del TEI (FreeDict usa n/v/adj/adv).
POS_SPACY_A_TEI = {
    "NOUN": "n", "PROPN": "n",
    "VERB": "v", "AUX": "v",
    "ADJ": "adj",
    "ADV": "adv",
}


def _texto(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def cargar_diccionario(ruta=TEI, max_traducciones=3):
    """Devuelve { lema_minúscula: [(pos, "trad1 / trad2 / ..."), ...] }.

    La lista conserva el orden de aparición en el archivo, así que `[0]` es el
    comportamiento anterior (primera acepción) cuando no se conoce la categoría.
    """
    root = ET.parse(ruta).getroot()
    dic = {}
    for entry in root.iter(f"{NS}entry"):
        orth = entry.find(f".//{NS}form/{NS}orth")
        if orth is None or not _texto(orth):
            continue
        clave = _texto(orth).lower()
        pos = _texto(entry.find(f".//{NS}gramGrp/{NS}pos")).lower()
        traducciones = []
        for cit in entry.iter(f"{NS}cit"):
            if cit.get("type") != "trans":
                continue
            for quote in cit.findall(f"{NS}quote"):
                t = _texto(quote)
                if t and t not in traducciones:
                    traducciones.append(t)
        if not traducciones:
            continue
        acepciones = dic.setdefault(clave, [])
        # Una sola entrada por categoría (la primera, que es la principal).
        if not any(p == pos for p, _ in acepciones):
            acepciones.append((pos, " / ".join(traducciones[:max_traducciones])))
    return dic


def elegir(acepciones, pos_spacy=None):
    """Traducción que concuerda con la categoría gramatical del token.

    Si no hay acepción de esa categoría (o no se conoce), cae en la primera
    del archivo: nunca devuelve menos que el comportamiento anterior.
    """
    if not acepciones:
        return None
    objetivo = POS_SPACY_A_TEI.get(pos_spacy or "")
    if objetivo:
        for pos, trad in acepciones:
            if pos == objetivo:
                return trad
    return acepciones[0][1]


if __name__ == "__main__":
    d = cargar_diccionario()
    print(f"entradas: {len(d)}")
    for w in ["frau", "haus", "gehen", "vorbereiten", "markt", "wolf", "wald", "mädchen"]:
        print(f"  {w:14} -> {d.get(w, '(no está)')}")
