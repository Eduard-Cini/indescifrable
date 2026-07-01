"""Vuelca una traducción numerada (respuesta del LLM) en cuerpo.es de la
lectura, validando la alineación 1:1 con las oraciones originales.

Uso:  PYTHONUTF8=1 python importar_traduccion.py verwandlung-01 traducciones/verwandlung-01.es.txt

Habilita automáticamente la traducción por oración (⇄) en el frontend, que ya
la muestra cuando cuerpo.es existe y tiene el mismo número de frases.
"""
import json
import re
import sys
from pathlib import Path

DIR_LECTURAS = Path(__file__).resolve().parents[1] / "src" / "data" / "lecturas"

LINEA = re.compile(r"^\s*(\d+)[.)]\s*(.+?)\s*$")


def parsear(texto):
    """Devuelve { numero: traduccion } de las líneas 'N. texto'."""
    salida = {}
    for linea in texto.splitlines():
        m = LINEA.match(linea)
        if m:
            salida[int(m.group(1))] = m.group(2).strip()
    return salida


def importar(id_lectura, archivo, idioma_origen="de"):
    ruta = DIR_LECTURAS / f"{id_lectura}.json"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    n = len(datos["cuerpo"][idioma_origen])

    numeradas = parsear(Path(archivo).read_text(encoding="utf-8"))
    faltantes = [i for i in range(1, n + 1) if i not in numeradas]
    extra = [i for i in numeradas if i < 1 or i > n]

    if faltantes or extra:
        print(f"⚠ Alineación imperfecta: {len(numeradas)} traducciones vs {n} oraciones")
        if faltantes:
            print(f"  faltan las oraciones: {faltantes[:20]}")
        if extra:
            print(f"  números fuera de rango: {extra[:20]}")
        print("  No se escribió nada. Revisa la respuesta del LLM.")
        return

    datos["cuerpo"]["es"] = [numeradas[i] for i in range(1, n + 1)]
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ {n} traducciones alineadas escritas en {ruta.name} (cuerpo.es)")


if __name__ == "__main__":
    importar(sys.argv[1], sys.argv[2])
