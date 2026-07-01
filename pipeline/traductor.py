"""Traductor alemán->español por capas, todo offline con diccionarios FreeDict:

  1. Directo deu-spa (mejor calidad).
  2. Cadena deu->eng->spa (cubre el hueco de deu-spa; marcado "(vía inglés)").
  3. Cabeza del compuesto alemán (marcado "(en compuesto)").

Busca primero por lema y, si falla, por la forma superficial (cubre errores
de lematización).
"""
from pathlib import Path

from leer_diccionario import cargar_diccionario

D = Path(__file__).parent / "diccionarios"


class Traductor:
    def __init__(self):
        self.de_es = cargar_diccionario(D / "deu-spa" / "deu-spa.tei")
        self.de_en = cargar_diccionario(D / "deu-eng" / "deu-eng.tei")
        self.en_es = cargar_diccionario(D / "eng-spa" / "eng-spa.tei")

    def tamanos(self):
        return len(self.de_es), len(self.de_en), len(self.en_es)

    def _cadena(self, w):
        """deu -> eng -> spa. Prefiere las acepciones inglesas más tempranas."""
        en = self.de_en.get(w)
        if not en:
            return None
        for frase in en.split(" / "):
            f = frase.strip().lower()
            candidatos = [f, f.removeprefix("to ").strip()]
            if f.split():
                candidatos.append(f.split()[-1])  # última palabra del sintagma
            for cand in candidatos:
                es = self.en_es.get(cand)
                if es:
                    return es.split(" / ")[0] + " (vía inglés)"
        return None

    def _compuesto(self, palabra):
        """Compuesto alemán: la cabeza es el último elemento. Prueba sufijos
        (mínimo 4 letras) por el diccionario directo o la cadena."""
        w = palabra.lower()
        if len(w) < 7:
            return None
        for i in range(1, len(w) - 2):
            suf = w[i:]
            if len(suf) < 3:
                continue
            base = self.de_es.get(suf)
            if not base:
                c = self._cadena(suf)
                base = c.replace(" (vía inglés)", "") if c else None
            if base:
                return base.split(" / ")[0] + " (en compuesto)"
        return None

    def traducir(self, lema, superficie):
        for cand in (lema.lower(), superficie.lower()):
            t = self.de_es.get(cand)
            if t:
                return t
        for cand in (lema.lower(), superficie.lower()):
            t = self._cadena(cand)
            if t:
                return t
        return self._compuesto(superficie)
