"""Traduce por frase (de->es) todas las partes de un libro con MT offline
(opus-mt), escribiendo cuerpo.es. Alineación 1:1 garantizada (una traducción
por frase). Análogo automatizado de importar_traduccion.py (que usa un LLM).

Uso:  PYTHONUTF8=1 python traducir_mt.py <prefijo>   (p. ej. immensee)
"""
import json
import sys
from pathlib import Path

from mt import traducir_mt

DIR_LECTURAS = Path(__file__).resolve().parents[1] / "src" / "data" / "lecturas"


def traducir_libro(prefijo):
    archivos = sorted(DIR_LECTURAS.glob(f"{prefijo}-*.json"))
    if not archivos:
        raise SystemExit(f"No hay lecturas con prefijo '{prefijo}'.")
    for f in archivos:
        datos = json.loads(f.read_text(encoding="utf-8"))
        frases = datos["cuerpo"].get("de")
        if not frases:
            continue
        print(f"{f.name}: traduciendo {len(frases)} frases...", flush=True)
        datos["cuerpo"]["es"] = traducir_mt(frases)
        f.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print("Listo. El frontend activa el ⇄ por frase automáticamente.")


if __name__ == "__main__":
    traducir_libro(sys.argv[1] if len(sys.argv) > 1 else "immensee")
