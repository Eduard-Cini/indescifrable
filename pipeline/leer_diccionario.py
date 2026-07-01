"""Parsea el diccionario FreeDict deu-spa (TEI) a un mapa lema -> traducción.

FreeDict (https://freedict.org) publica diccionarios libres. Aquí usamos
deu-spa (alemán -> español), formato TEI. Licencia: ver diccionarios/deu-spa/COPYING.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

TEI = Path(__file__).parent / "diccionarios" / "deu-spa" / "deu-spa.tei"
NS = "{http://www.tei-c.org/ns/1.0}"


def _texto(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def cargar_diccionario(ruta=TEI, max_traducciones=3):
    """Devuelve { lema_en_minuscula: "trad1 / trad2 / ..." } desde el TEI."""
    tree = ET.parse(ruta)
    root = tree.getroot()
    dic = {}
    for entry in root.iter(f"{NS}entry"):
        orth = entry.find(f".//{NS}form/{NS}orth")
        if orth is None or not _texto(orth):
            continue
        clave = _texto(orth).lower()
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
        # conserva la primera acepción encontrada para cada lema
        if clave not in dic:
            dic[clave] = " / ".join(traducciones[:max_traducciones])
    return dic


if __name__ == "__main__":
    d = cargar_diccionario()
    print(f"entradas: {len(d)}")
    for w in ["frau", "haus", "gehen", "vorbereiten", "markt", "wolf", "wald", "mädchen"]:
        print(f"  {w:14} -> {d.get(w, '(no está)')}")
