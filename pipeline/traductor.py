"""Traductor alemán/inglés -> español por capas, todo offline con FreeDict:

  1. Directo (deu-spa / eng-spa), mejor calidad.
  2. Cadena deu->eng->spa (cubre el hueco de deu-spa; marcado "(vía inglés)").
  3. Cabeza del compuesto alemán (marcado "(en compuesto)").

En todas las capas se elige la acepción cuya CATEGORÍA GRAMATICAL concuerda con
el análisis de spaCy: FreeDict guarda una entrada por categoría y quedarse con
la primera del archivo daba errores como bone -> «osiforme» (adjetivo) en vez
de «hueso». Si no hay acepción de esa categoría se cae en la primera, así que
nunca se pierde cobertura.

Busca primero por lema y, si falla, por la forma superficial (cubre errores
de lematización).
"""
from pathlib import Path

from leer_diccionario import cargar_diccionario, elegir

D = Path(__file__).parent / "diccionarios"


class Traductor:
    def __init__(self):
        self.de_es = cargar_diccionario(D / "deu-spa" / "deu-spa.tei")
        self.de_en = cargar_diccionario(D / "deu-eng" / "deu-eng.tei")
        self.en_es = cargar_diccionario(D / "eng-spa" / "eng-spa.tei")

    def tamanos(self):
        return len(self.de_es), len(self.de_en), len(self.en_es)

    def _cadena(self, w, pos=None):
        """deu -> eng -> spa. Prefiere las acepciones inglesas más tempranas y
        mantiene la categoría gramatical en los dos saltos."""
        en = elegir(self.de_en.get(w), pos)
        if not en:
            return None
        for frase in en.split(" / "):
            f = frase.strip().lower()
            candidatos = [f, f.removeprefix("to ").strip()]
            if f.split():
                candidatos.append(f.split()[-1])  # última palabra del sintagma
            for cand in candidatos:
                es = elegir(self.en_es.get(cand), pos)
                if es:
                    return es.split(" / ")[0] + " (vía inglés)"
        return None

    def _compuesto(self, palabra):
        """Compuesto alemán: la cabeza es el último elemento y es un SUSTANTIVO
        (Holztür -> Tür). Prueba sufijos por el diccionario directo o la cadena."""
        w = palabra.lower()
        if len(w) < 7:
            return None
        for i in range(1, len(w) - 2):
            suf = w[i:]
            if len(suf) < 3:
                continue
            base = elegir(self.de_es.get(suf), "NOUN")
            if not base:
                c = self._cadena(suf, "NOUN")
                base = c.replace(" (vía inglés)", "") if c else None
            if base:
                return base.split(" / ")[0] + " (en compuesto)"
        return None

    def traducir(self, lema, superficie, pos=None):
        for cand in (lema.lower(), superficie.lower()):
            t = elegir(self.de_es.get(cand), pos)
            if t:
                return t
        for cand in (lema.lower(), superficie.lower()):
            t = self._cadena(cand, pos)
            if t:
                return t
        return self._compuesto(superficie)

    def traducir_en(self, lema, superficie, pos=None):
        """Inglés -> español, directo por eng-spa (por lema y forma)."""
        for cand in (lema.lower(), superficie.lower()):
            t = elegir(self.en_es.get(cand), pos)
            if t:
                return t
        return None
