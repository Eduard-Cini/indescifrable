"""Exporta las oraciones de una lectura como lista numerada, lista para pegar
en un LLM (Gemini, etc.) y obtener una traducción alineada 1:1.

Uso:  PYTHONUTF8=1 python exportar_frases.py verwandlung-01
Salida: traducciones/<id>.pendiente.txt  (prompt + oraciones numeradas)

Luego, con la respuesta del LLM pegada en traducciones/<id>.es.txt, usar
importar_traduccion.py para volcarla en el JSON (validando la alineación).
"""
import json
import sys
from pathlib import Path

DIR_LECTURAS = Path(__file__).resolve().parents[1] / "src" / "data" / "lecturas"
DIR_SALIDA = Path(__file__).parent / "traducciones"

PROMPT = """Traduce al español neutral (latinoamericano) cada oración numerada del \
alemán. Reglas estrictas:
- Devuelve EXACTAMENTE una línea por cada oración de entrada, con el mismo número.
- No unas ni dividas oraciones: conserva la correspondencia 1 a 1.
- Traducción literaria, natural y fiel; sin notas ni comentarios.
- Responde solo con las líneas numeradas.
"""


def exportar(id_lectura, idioma="de"):
    datos = json.loads((DIR_LECTURAS / f"{id_lectura}.json").read_text(encoding="utf-8"))
    frases = datos["cuerpo"][idioma]
    DIR_SALIDA.mkdir(exist_ok=True)
    destino = DIR_SALIDA / f"{id_lectura}.pendiente.txt"
    with destino.open("w", encoding="utf-8") as f:
        f.write(PROMPT + "\n")
        for i, fr in enumerate(frases, 1):
            f.write(f"{i}. {fr}\n")
    print(f"{len(frases)} oraciones -> {destino}")


if __name__ == "__main__":
    exportar(sys.argv[1] if len(sys.argv) > 1 else "verwandlung-01")
