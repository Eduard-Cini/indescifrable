# -*- coding: utf-8 -*-
"""Genera docs/metricas-seccion3.pdf: métricas de la Sección 3 (gramática).
Formaliza el generador de cloze (distractores híbridos paradigma/coseno y
filtros de unicidad) y calcula los conteos REALES leyendo src/data/gramatica.json,
así el PDF siempre refleja el corpus vigente.

Uso:  PYTHONUTF8=1 python docs/generar_metricas_seccion3.py
"""
import json
from collections import Counter
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable)

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).with_name("metricas-seccion3.pdf")
DATOS = json.loads((RAIZ / "src" / "data" / "gramatica.json").read_text(encoding="utf-8"))

TITULO_TEMA = {t["id"]: t["titulo"] for t in DATOS["temas"]}
EJS = DATOS["ejercicios"]

AZUL = colors.HexColor("#1f3a5f"); AZUL2 = colors.HexColor("#2e5e8c")
GRIS = colors.HexColor("#555555"); GRISC = colors.HexColor("#f0f0f0")
ss = getSampleStyleSheet()
St = lambda n, **k: ParagraphStyle(n, parent=ss["Normal"], **k)
STIT = ParagraphStyle("t", parent=ss["Title"], fontSize=22, textColor=AZUL, leading=26)
SSUB = St("s", fontSize=11.5, textColor=GRIS, alignment=TA_CENTER, spaceAfter=4)
SH1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=14.5, textColor=AZUL,
                     spaceBefore=13, spaceAfter=5, leading=17)
SH2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, textColor=AZUL2,
                     spaceBefore=9, spaceAfter=3, leading=14)
SB = St("b", fontSize=9.7, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=5)
SCODE = St("code", fontSize=8.6, leading=12, fontName="Courier",
           backColor=GRISC, borderPadding=5, spaceAfter=6, spaceBefore=2)
SCELL = St("c", fontSize=8.4, leading=11)
SCELLH = St("ch", fontSize=8.4, leading=11, textColor=colors.white, fontName="Helvetica-Bold")
story = []


def h1(t):
    story.append(Paragraph(t, SH1))
    story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL, spaceAfter=4))


def h2(t):
    story.append(Paragraph(t, SH2))


def p(t):
    story.append(Paragraph(t, SB))


def code(t):
    story.append(Paragraph(t.replace("\n", "<br/>").replace(" ", "&nbsp;"), SCODE))


def tabla(filas, anchos):
    data = [[Paragraph(str(c), SCELLH if i == 0 else SCELL) for c in fila]
            for i, fila in enumerate(filas)]
    t = Table(data, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRISC]),
        ("BACKGROUND", (0, 0), (-1, 0), AZUL2)]))
    story.append(t); story.append(Spacer(1, 7))


def nivel_de(fuente):
    return fuente.split("·", 1)[0].strip()


# --- Conteos calculados del JSON --------------------------------------------
total = sum(len(v) for v in EJS.values())
niveles = ["principiante", "intermedio", "avanzado"]

# --- Portada -----------------------------------------------------------------
story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("Sección 3 — Gramática", STIT))
story.append(Paragraph("Métricas: formalización del generador de cloze, distractores "
                       "híbridos paradigma/coseno y conteos del corpus", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. El problema formal")
p("Un ejercicio cloze es una tupla (c, r, D): un contexto c con un hueco, la respuesta r y "
  "un conjunto D de k distractores. Para que el ejercicio <b>mida</b> la regla gramatical "
  "que se enseña, hacen falta dos propiedades en tensión:")
p("<b>(P1) Unicidad</b>: sustituir el hueco por cualquier d ∈ D debe producir una frase "
  "agramatical (o, en separables, un verbo inexistente). Si algún d produce una frase "
  "válida, el ejercicio no tiene respuesta y penaliza al alumno que sí sabe la regla.")
p("<b>(P2) Dificultad</b>: los distractores deben ser <i>plausibles</i>. Un distractor "
  "absurdo se descarta sin saber gramática, y el ejercicio no discrimina.")
p("El generador maximiza P2 <b>sujeto a</b> P1: la similitud coseno ordena por plausibilidad "
  "(P2) y los filtros por tema garantizan la agramaticalidad (P1).")

h1("2. El método híbrido")
h2("2.1 El paradigma define el conjunto")
p("Para cada tema, el conjunto de candidatos C(r) sale del paradigma morfológico, no del "
  "espacio vectorial completo: las otras 5 formas del artículo definido; las preposiciones "
  "del caso opuesto; las formas del mismo lema verbal atestiguadas en el corpus (índice "
  "invertido lema → formas del léxico de la Sección 1); los prefijos separables del "
  "inventario. Esto garantiza que todo candidato sea <i>categorialmente</i> comparable con "
  "la respuesta — cosa que el coseno por sí solo no da: los vecinos vectoriales de «der» "
  "incluyen sustantivos y adverbios, no solo artículos.")
h2("2.2 El coseno ordena el conjunto")
p("Con los vectores de spaCy de_core_news_md (20.000 palabras × 300 dimensiones), cada "
  "candidato se puntúa contra la respuesta y se eligen los k = 3 de mayor similitud "
  "(<i>hard negatives</i>). Empates → orden alfabético, así el generador es determinista.")
code("cos(u, v) = (u · v) / (||u|| · ||v||) ∈ [−1, 1]\n"
     "D = top-k según cos(v_r, v_d),  d ∈ C(r),  filtrado por P1")
p("Intuición geométrica: dos formas del mismo paradigma que aparecen en contextos parecidos "
  "(«dem»/«den», «mit»/«bei») tienen vectores cercanos; el alumno solo puede separarlas "
  "aplicando la regla, no por rareza distribucional. Eso es exactamente lo que quiere P2.")

h1("3. Los filtros de unicidad (P1), como predicados")
p("Cada tema instancia P1 con un predicado verificable mecánicamente:")
tabla([
    ["Tema", "Predicado sobre el candidato d"],
    ["Declinación", "d difiere de r en caso/género/número por construcción del paradigma; "
     "el contexto (sustantivo + sintaxis) fija esos rasgos → d agramatical"],
    ["Preposición", "rige(d) ≠ rige(r) (caso opuesto) ∧ el sintagma tiene marca de caso "
     "visible (∃ DET/ADJ/PRON declinado en el subárbol) → d incompatible con la marca"],
    ["Conjugación", "re-parseada la frase con d en el hueco: ¬finito(d) ∨ "
     "persona(d) ≠ persona(sujeto) ∨ número(d) ≠ número(sujeto). Un d que concuerda "
     "(mismo verbo en otro tiempo: ging → geht) daría frase válida y se excluye"],
    ["Separables", "atestiguado(r + lema) en el léxico ∧ ¬atestiguado(d + lema): la "
     "respuesta forma un verbo real del corpus y ningún distractor forma otro"],
], [3.2 * cm, 13.2 * cm])
p("El filtro de conjugación usa el propio parser como oráculo de gramaticalidad: es la "
  "misma herramienta que localizó el hueco, aplicada a la frase sustituida. El de "
  "separables usa la atestiguación en el corpus como proxy de existencia del verbo — "
  "conservador pero verificable (véase §6, limitaciones).")

h1("4. Conteos del corpus (calculados de gramatica.json)")
p(f"El generador emite <b>{total} ejercicios</b> repartidos en {len(EJS)} temas, con tope "
  "de 40 por tema y selección estratificada round-robin entre fuentes (cota de 12 "
  "candidatos por fuente antes de estratificar).")

h2("4.1 Ejercicios por tema y nivel")
filas = [["Tema", "Total", "Principiante", "Intermedio", "Avanzado", "Fuentes"]]
for tema, ejercicios in EJS.items():
    por_nivel = Counter(nivel_de(e["fuente"]) for e in ejercicios)
    filas.append([
        TITULO_TEMA.get(tema, tema), len(ejercicios),
        por_nivel.get("principiante", 0), por_nivel.get("intermedio", 0),
        por_nivel.get("avanzado", 0), len({e["fuente"] for e in ejercicios}),
    ])
tabla(filas, [4.6 * cm, 1.7 * cm, 2.6 * cm, 2.4 * cm, 2.3 * cm, 1.9 * cm])
p("Sin la estratificación, el tope de 40 se llenaba íntegramente con la primera fuente en "
  "orden alfabético (Immensee) y ni una frase de principiante/intermedio aportaba "
  "ejercicios; el round-robin reparte entre 9–12 fuentes por tema.")

h2("4.2 Distribución de respuestas (declinación)")
casos = Counter(e["pista"].split("·")[0].strip().lower() for e in EJS.get("declinacion", []))
formas = Counter(e["respuesta"].lower() for e in EJS.get("declinacion", []))
filas = [["Caso (según spaCy)", "Ejercicios"]]
for caso, n in casos.most_common():
    filas.append([caso.capitalize(), n])
tabla(filas, [5.5 * cm, 3.0 * cm])
p("Formas: " + ", ".join(f"«{f}» ×{n}" for f, n in formas.most_common()) + ". "
  "La distribución refleja el corpus (narrativa en pasado, mucho nominativo/acusativo); "
  "no se fuerza el balance para no fabricar frases artificiales.")

h2("4.3 Preposiciones y separables")
prep = Counter(e["respuesta"].lower() for e in EJS.get("preposicion_caso", []))
seps = Counter(e["respuesta"].lower() for e in EJS.get("separables", []))
p("Preposiciones más preguntadas: "
  + ", ".join(f"«{f}» ×{n}" for f, n in prep.most_common(8)) + ".")
p("Prefijos separables más preguntados: "
  + ", ".join(f"«{f}» ×{n}" for f, n in seps.most_common(8)) + ".")
verbos = Counter()
for e in EJS.get("conjugacion", []):
    marca = "«"
    if "verbo «" in e["pista"]:
        verbos[e["pista"].split("verbo «", 1)[1].rstrip("».")] += 1
p("Verbos más preguntados en conjugación: "
  + ", ".join(f"«{v}» ×{n}" for v, n in verbos.most_common(8)) + ".")

h1("5. Coste computacional")
tabla([
    ["Fase", "Coste"],
    ["Parseo del corpus", "Una pasada de spaCy por frase corta (≤ 18 tokens); las largas "
     "se descartan con un prefiltro por espacios antes de parsear"],
    ["Coseno", "O(|C(r)|) productos escalares de dimensión 300 por hueco; |C| ≤ 28"],
    ["Filtro de conjugación", "El más caro: un re-parseo por candidato validado. Se valida "
     "en orden de coseno descendente y se corta al llegar a k=3 → ~3–6 re-parseos por hueco"],
    ["Total", "~1 minuto en CPU para todo el corpus; el frontend no paga nada de esto "
     "(consume JSON estático por dynamic import)"],
], [3.8 * cm, 12.6 * cm])

h1("6. Limitaciones y trabajo futuro")
p("<b>Semántica no modelada.</b> En separables la elección del prefijo es en parte "
  "semántica (aufmachen/zumachen son ambos reales); el filtro de atestiguación garantiza "
  "que los distractores no formen verbo real, pero el ejercicio sigue apoyándose en la "
  "pista (que da el verbo completo). <b>Atestiguación como proxy.</b> Que un verbo no esté "
  "en el léxico del corpus no implica que no exista en alemán; el criterio es conservador "
  "por el lado correcto (nunca valida un distractor real atestiguado), pero podría "
  "descartar distractores legítimos. <b>Parser como oráculo.</b> El filtro de concordancia "
  "hereda los errores de spaCy; en frases cortas y simples (las que se seleccionan) su "
  "precisión morfológica es alta. <b>Futuro</b>: más temas (verbo en 2ª posición, "
  "Konjunktiv), balance de casos por muestreo dirigido, ejercicios en inglés, y progreso "
  "persistente por tema (localStorage) para conectar con el repaso espaciado.")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Sección 3 — Gramática (métricas)")
doc.build(story)
print(f"-> {SALIDA} ({total} ejercicios)")
