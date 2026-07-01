# -*- coding: utf-8 -*-
"""Overrides de léxico POR LECTURA para desambiguar verbos separables.

Un léxico global (clave idioma:forma) no puede distinguir "nahm" como parte de
"annehmen" (suponer) frente a "nahm" = "nehmen" (tomar): depende del contexto.
Cada lectura puede llevar un pequeño mapa `lexico` que el frontend prioriza
sobre el léxico global.

Para los textos curados (principiante/intermedio) estos overrides se revisaron
A MANO: el generador automático localiza bien los separables (dependencia `svp`
de spaCy) pero su traducción falla cuando FreeDict no tiene el lema reconstruido
o spaCy no lo lematiza (p. ej. losschoss, anfing), así que aquí se fija el lema
y la traducción correctos, verificados contra cada frase alemana.

Uso:  PYTHONUTF8=1 python overrides_lecturas.py
"""
import json
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / "src" / "data" / "lecturas"

# id de lectura -> { "de:forma": { lemma, es } }.  Verbo separable = una palabra.
CURADOS = {
    "dia-de-ana": {
        "de:steht": {"lemma": "aufstehen", "es": "se levanta (aufstehen)"},
        "de:auf": {"lemma": "aufstehen", "es": "se levanta (aufstehen)"},
    },
    "leon-y-raton": {
        "de:auf": {"lemma": "aufwecken", "es": "despertar (aufwecken)"},
        "de:durch": {"lemma": "durchnagen", "es": "roer / carcomer (durchnagen)"},
        "de:frei": {"lemma": "freilassen", "es": "liberar / soltar (freilassen)"},
    },
    "liebre-y-tortuga": {
        "de:nahm": {"lemma": "annehmen", "es": "suponer / dar por hecho (annehmen)"},
        "de:heraus": {"lemma": "herausfordern", "es": "desafiar / retar (herausfordern)"},
        "de:los": {"lemma": "losschießen", "es": "salir disparado (losschießen)"},
        "de:hielt": {"lemma": "anhalten", "es": "detenerse / pararse (anhalten)"},
        "de:weiter": {"lemma": "weitergehen", "es": "seguir / continuar (weitergehen)"},
    },
    "hormiga-y-cigarra": {
        "de:an": {"lemma": "anlegen", "es": "acumular / hacer acopio (anlegen)"},
    },
    "sterntaler": {
        "de:hinaus": {"lemma": "hinausgehen", "es": "salir (hinausgehen)"},
        "de:weiter": {"lemma": "weitergehen", "es": "seguir / continuar (weitergehen)"},
    },
    "viento-y-sol": {
        "de:zog": {"lemma": "ausziehen", "es": "quitarse (la ropa) (ausziehen)"},
    },
    "rotkaeppchen": {
        "de:zog": {"lemma": "anziehen", "es": "ponerse (la ropa) (anziehen)"},
        "de:setzte": {"lemma": "aufsetzen", "es": "ponerse (en la cabeza) (aufsetzen)"},
        "de:hin": {"lemma": "hinlegen", "es": "acostarse / tumbarse (hinlegen)"},
        "de:fing": {"lemma": "anfangen", "es": "empezar / comenzar (anfangen)"},
        "de:vorbei": {"lemma": "vorbeigehen", "es": "pasar de largo (vorbeigehen)"},
    },
}


def main():
    porid = {}
    for ruta in DIR.glob("*.json"):
        try:
            porid[json.loads(ruta.read_text(encoding="utf-8"))["id"]] = ruta
        except Exception:
            pass

    for ruta in DIR.glob("*.json"):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        overrides = CURADOS.get(datos.get("id"))
        cambio = False
        if overrides:
            nuevo = dict(sorted(overrides.items()))
            if datos.get("lexico") != nuevo:
                datos["lexico"] = nuevo
                cambio = True
        elif "lexico" in datos:  # limpia overrides automáticos previos
            datos.pop("lexico")
            cambio = True
        if cambio:
            ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
            print(f"  {ruta.stem}: {datos.get('lexico', '—')}")
    print("Listo.")


if __name__ == "__main__":
    main()
