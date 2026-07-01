"""Construye src/data/lexico.json a partir de TODAS las lecturas.

Recorre cada lectura de src/data/lecturas y, para su texto en alemán y/o
inglés, genera entradas `idioma:forma -> { lemma, es }`:
  - alemán: spaCy de + Traductor (deu-spa / cadena en inglés / compuesto);
  - inglés: spaCy en + FreeDict eng-spa.
Reconstruye desde lexico.base.json (entradas curadas, con prioridad), así el
resultado es idempotente. Informa la cobertura por lectura y marca los huecos.

Uso:  PYTHONUTF8=1 python construir_lexico.py
"""
import json
from pathlib import Path

import spacy

from procesar import normalizar, lemas_con_separables, RUTA_BASE, RUTA_LEXICO
from traductor import Traductor

DIR_LECTURAS = Path(__file__).resolve().parents[1] / "src" / "data" / "lecturas"


def entradas_de_texto(frases, idioma, nlp, tr):
    """Genera { idioma:forma -> {lemma, es?} } para una lista de frases."""
    lexico = {}
    faltan = []
    for frase in frases:
        doc = nlp(frase)
        lemas = lemas_con_separables(doc) if idioma == "de" else {t.i: t.lemma_ for t in doc}
        for t in doc:
            if not t.is_alpha:
                continue
            clave = f"{idioma}:{normalizar(t.text)}"
            if clave == f"{idioma}:" or clave in lexico:
                continue
            lema = lemas[t.i]
            entrada = {"lemma": lema}
            trad = tr.traducir(lema, t.text) if idioma == "de" else tr.traducir_en(lema, t.text)
            if trad:
                entrada["es"] = trad
            else:
                faltan.append(t.text)
            lexico[clave] = entrada
    return lexico, faltan


def construir():
    print("Cargando spaCy (de, en) y diccionarios FreeDict...")
    nlp_de = spacy.load("de_core_news_md")
    nlp_en = spacy.load("en_core_web_sm")
    tr = Traductor()

    base = json.loads(RUTA_BASE.read_text(encoding="utf-8")) if RUTA_BASE.exists() else {}
    lexico = {}
    print("\nlectura                         idioma  formas  con_trad")
    for ruta in sorted(DIR_LECTURAS.glob("*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        for idioma in ("de", "en"):
            frases = datos.get("cuerpo", {}).get(idioma)
            if not frases:
                continue
            nlp = nlp_de if idioma == "de" else nlp_en
            entradas, faltan = entradas_de_texto(frases, idioma, nlp, tr)
            # No sobrescribir una entrada ya traducida con una sin traducción
            # (una misma forma puede recibir distinto lema según el contexto).
            for k, v in entradas.items():
                if k not in lexico or ("es" not in lexico[k] and "es" in v):
                    lexico[k] = v
            con = sum(1 for v in entradas.values() if "es" in v)
            marca = "" if con == len(entradas) else f"  faltan: {sorted(set(faltan))[:8]}"
            print(f"  {ruta.stem:28} {idioma:4}  {len(entradas):5}   {con:5}{marca}")

    fusion = dict(lexico)
    fusion.update(base)  # las entradas curadas a mano tienen prioridad
    fusion = dict(sorted(fusion.items()))
    RUTA_LEXICO.write_text(
        json.dumps(fusion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    con = sum(1 for v in fusion.values() if "es" in v)
    print(f"\nléxico total: {len(fusion)} entradas, {con} con traducción "
          f"({100*con//len(fusion)}%) -> {RUTA_LEXICO.name}")


if __name__ == "__main__":
    construir()
