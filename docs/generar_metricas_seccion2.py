# -*- coding: utf-8 -*-
"""Genera docs/metricas-seccion2.pdf: métricas de la Sección 2 (repaso espaciado):
resultados de la simulación SM-2 vs Leitner, analítica de la cadena de Markov
y ejemplos del modelo de conocimiento sobre el corpus real.

Requiere docs/datos-simulacion.json (npm run simular) y src/data/frecuencias.json.

Uso:  PYTHONUTF8=1 python docs/generar_metricas_seccion2.py
"""
import json
import math
from pathlib import Path

from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable)

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).with_name("metricas-seccion2.pdf")

datos = json.loads(Path(__file__).with_name("datos-simulacion.json").read_text(encoding="utf-8"))
frec = json.loads((RAIZ / "src" / "data" / "frecuencias.json").read_text(encoding="utf-8"))

AZUL = colors.HexColor("#1f3a5f"); AZUL2 = colors.HexColor("#2e5e8c")
VERDE = colors.HexColor("#2e7d4f"); NARANJA = colors.HexColor("#c05f2a")
GRIS = colors.HexColor("#555555"); GRISC = colors.HexColor("#f0f0f0")
ss = getSampleStyleSheet()
St = lambda n, **k: ParagraphStyle(n, parent=ss["Normal"], **k)
STIT = ParagraphStyle("t", parent=ss["Title"], fontSize=22, textColor=AZUL, leading=26)
SSUB = St("s", fontSize=11.5, textColor=GRIS, alignment=TA_CENTER, spaceAfter=4)
SH1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=14.5, textColor=AZUL,
                     spaceBefore=13, spaceAfter=5, leading=17)
SB = St("b", fontSize=9.7, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=5)
SCELL = St("c", fontSize=8.4, leading=11)
SCELLH = St("ch", fontSize=8.4, leading=11, textColor=colors.white, fontName="Helvetica-Bold")
story = []


def h1(t):
    story.append(Paragraph(t, SH1))
    story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL, spaceAfter=4))


def p(t):
    story.append(Paragraph(t, SB))


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


def grafica(series, titulo, eje_y, y_min=None, y_max=None):
    """Dos líneas (SM-2 azul, Leitner naranja) sobre el día simulado."""
    d = Drawing(15.8 * cm, 6.4 * cm)
    lp = LinePlot()
    lp.x, lp.y, lp.width, lp.height = 1.4 * cm, 0.9 * cm, 13.6 * cm, 4.6 * cm
    lp.data = series
    lp.lines[0].strokeColor = AZUL2; lp.lines[0].strokeWidth = 1.4
    lp.lines[1].strokeColor = NARANJA; lp.lines[1].strokeWidth = 1.4
    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.labelTextFormat = "%d"
    lp.yValueAxis.labelTextFormat = eje_y
    if y_min is not None:
        lp.yValueAxis.valueMin = y_min
    if y_max is not None:
        lp.yValueAxis.valueMax = y_max
    d.add(lp)
    d.add(String(1.4 * cm, 5.9 * cm, titulo, fontName="Helvetica-Bold",
                 fontSize=9.5, fillColor=AZUL))
    leg = Legend()
    leg.x, leg.y = 12.2 * cm, 6.1 * cm
    leg.fontSize = 8; leg.alignment = "right"
    leg.colorNamePairs = [(AZUL2, "SM-2"), (NARANJA, "Leitner")]
    d.add(leg)
    story.append(d); story.append(Spacer(1, 6))


sm2, lei = datos["sm2"], datos["leitner"]
par = datos["parametros"]
N = par["palabras"]

# --- Portada ---------------------------------------------------------------
story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("Sección 2 — Repaso espaciado", St("secmarker", fontSize=13,
             textColor=AZUL2, alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=6)))
story.append(Paragraph("Métricas — Repaso espaciado", STIT))
story.append(Paragraph("Comparación SM-2 vs Leitner por simulación, analítica de la "
                       "cadena de Markov y modelo de conocimiento", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. Diseño del experimento")
p("Alumno sintético con curva de olvido exponencial, simulado bajo los dos planificadores "
  "<b>con los motores reales del repo</b> (engine/srs.js y engine/leitner.js). El mismo "
  "alumno — misma dificultad, estabilidad inicial y crecimiento por palabra — se somete a "
  "cada planificador; solo cambia <i>cuándo</i> le preguntan.")
tabla([
    ["Parámetro", "Valor"],
    ["Palabras", f"{N} ({par['nuevasPorDia']}/día durante {par['diasDeAlta']} días)"],
    ["Horizonte", f"{par['horizonteDias']} días"],
    ["Modelo de olvido", par["modeloOlvido"]],
    ["Parámetros del alumno", par["dificultad"]],
    ["RNG", f"mulberry32, semilla {par['seed']} (reproducible)"],
    ["Contabilidad de fallos", "SM-2: 2 presentaciones (falla + reciclada en sesión, fiel a "
     "la UI); Leitner: 1 (baja a caja 1 y espera)"],
], [4.6 * cm, 11.8 * cm])
p("<i>Métrica de retención (probe): media diaria de e^(−(hoy − último repaso)/S) sobre las "
  "palabras introducidas — la probabilidad de recordarlas si se preguntaran hoy; no gasta "
  "repasos ni interfiere con la simulación.</i>")

h1("2. Resultados globales")
pres_sm2, pres_lei = sm2["totalPresentaciones"], lei["totalPresentaciones"]
tabla([
    ["Métrica", "SM-2", "Leitner", "Diferencia"],
    ["Retención final (probe)", f"{100*sm2['retencionFinal']:.1f}%",
     f"{100*lei['retencionFinal']:.1f}%",
     f"+{100*(lei['retencionFinal']-sm2['retencionFinal']):.1f} pp Leitner"],
    ["Presentaciones totales", f"{pres_sm2:,}", f"{pres_lei:,}",
     f"+{100*(pres_lei-pres_sm2)/pres_sm2:.0f}% Leitner"],
    ["Presentaciones por palabra", f"{pres_sm2/N:.1f}", f"{pres_lei/N:.1f}", "—"],
    ["Precisión en los repasos", f"{100*sm2['precisión']:.1f}%", f"{100*lei['precisión']:.1f}%", "—"],
    ["Palabras maduras al final*", f"{sm2['madurasFinal']}", f"{lei['madurasFinal']}", "—"],
], [5.4 * cm, 3.2 * cm, 3.2 * cm, 4.6 * cm])
p("<i>*Madura: intervalo ≥ 16 días en SM-2; caja 5 en Leitner (misma cadencia máxima).</i>")
p(f"La lectura central: Leitner retiene {100*(lei['retencionFinal']-sm2['retencionFinal']):.1f} "
  f"puntos más, pero cuesta un {100*(pres_lei-pres_sm2)/pres_sm2:.0f}% más de trabajo "
  f"({pres_lei/N:.1f} frente a {pres_sm2/N:.1f} presentaciones por palabra). El techo de la "
  "caja 5 (repasar cada 16 días como máximo) produce <b>sobre-repaso</b>: sigue preguntando "
  "palabras cuya estabilidad ya supera con creces los 16 días. SM-2 no tiene techo — el "
  "intervalo crece con EF — y por eso convierte los mismos aciertos en menos trabajo futuro.")

h1("3. Series diarias")
serie_ret = [
    [(x["dia"], 100 * x["retencion"]) for x in sm2["serie"]],
    [(x["dia"], 100 * x["retencion"]) for x in lei["serie"]],
]
grafica(serie_ret, "Retención media diaria (probe, %)", "%d%%", y_min=60, y_max=101)
p("La retención de ambos sistemas se estabiliza alta; la de Leitner satura cerca del 100% "
  "porque el techo de 16 días mantiene Δ/S diminuto. La de SM-2 se asienta en torno a su "
  "punto de equilibrio: el intervalo crece hasta que el olvido lo frena.")
serie_rep = [
    [(x["dia"], x["repasos"]) for x in sm2["serie"]],
    [(x["dia"], x["repasos"]) for x in lei["serie"]],
]
grafica(serie_rep, "Presentaciones por día", "%d")
p(f"Durante el alta (días 0–{par['diasDeAlta']}) domina el goteo de nuevas; después la carga "
  "de SM-2 cae de forma sostenida (los intervalos se estiran sin límite) mientras que la de "
  f"Leitner queda anclada por el suelo estructural de la caja 5: {N} palabras / 16 días ≈ "
  f"{N//16} repasos diarios que no desaparecen nunca.")

h1("4. Distribuciones finales")
hc = datos["histCajasLeitner"]
hi = datos["histIntervalosSm2"]
tabla([["Caja Leitner", "1", "2", "3", "4", "5"],
       ["Palabras", *[str(x) for x in hc]]],
      [4 * cm] + [2.4 * cm] * 5)
cortes = hi["cortes"]
etiquetas = [f"≤{c} d" if c != "más" else ">60 d" for c in cortes]
tabla([["Intervalo SM-2", *etiquetas],
       ["Palabras", *[str(x) for x in hi["conteos"]]]],
      [3.4 * cm] + [1.9 * cm] * len(cortes))
p("Al final del horizonte casi todo el mazo de Leitner vive en la caja 5 (cadencia fija de "
  "16 días), mientras que SM-2 ha empujado la mayoría de las palabras a intervalos de más de "
  "un mes: ahí está el ahorro de trabajo.")

h1("5. Leitner como cadena de Markov (analítica)")
p("Con probabilidad de acierto p constante, la caja de una palabra es una cadena de Markov "
  "(subir con p, caer a la caja 1 con 1−p). Resultados exactos de engine/leitner.js — "
  "distribución estacionaria π, esperanza de repasos y días hasta la caja 5 "
  "(E[repasos] = Σ p^(−j), primera racha de 4 aciertos) y tasa de repasos en régimen "
  "(1/Σ π·I):")
filas = [["p", "π (cajas 1..5)", "Repasos hasta caja 5", "Días hasta caja 5",
          "Repasos/día/palabra"]]
for m in datos["markov"]:
    filas.append([f"{m['p']:.2f}",
                  "  ".join(f"{x:.3f}" for x in m["estacionaria"]),
                  f"{m['repasosHastaCaja5']}", f"{m['diasHastaCaja5']}",
                  f"{m['repasosPorDiaPalabra']}"])
tabla(filas, [1.5 * cm, 6 * cm, 3.4 * cm, 2.8 * cm, 2.7 * cm])
p(f"El contraste con la simulación cierra el círculo: la precisión empírica de Leitner fue "
  f"{100*lei['precisión']:.0f}%, y la fila p = 0.95 predice ≈ "
  f"{datos['markov'][-1]['repasosPorDiaPalabra']} repasos/día/palabra en régimen — "
  f"aplicado a {N} palabras da ≈ {datos['markov'][-1]['repasosPorDiaPalabra']*N:.0f} "
  "repasos/día, el mismo orden que muestra la cola de la serie diaria. El modelo analítico "
  "y la simulación se validan mutuamente.")

h1("6. Modelo de conocimiento sobre el corpus real")
tot = frec["totales"]["de"]
lemas = frec["lemas"]
p(f"Frecuencias del corpus (pipeline/frecuencias.py): <b>{tot:,} tokens</b> en alemán, "
  f"<b>{sum(1 for k in lemas if k.startswith('de:')):,} lemas distintos</b>. Prior "
  "P(conocer) = σ((zipf − 3.0)/0.7) con zipf = log10(conteo/total·10<super>6</super>). "
  "Ejemplos reales:")
ejemplos = ["de:und", "de:gehen", "de:fenster", "de:zimmer", "de:pfote", "de:ungeziefer"]
filas = [["Lema", "Conteo", "zipf", "P(conocer) a priori"]]
for k in ejemplos:
    c = lemas.get(k, 0)
    if not c:
        continue
    z = math.log10(c / tot * 1e6)
    prob = 1 / (1 + math.exp(-(z - 3.0) / 0.7))
    filas.append([k.split(":")[1], str(c), f"{z:.2f}", f"{prob:.2f}"])
tabla(filas, [4 * cm, 3 * cm, 3 * cm, 6.4 * cm])
p("El prior ordena como se espera: palabras funcionales frecuentes salen «probablemente "
  "conocidas» y no estorban; las raras del texto son las que llegan al repaso previo, con "
  "el tope por nivel (5/12/20).")

h1("7. Conclusiones")
p("1) <b>Leitner</b> es simple y muy retentivo, pero su intervalo máximo lo condena a un "
  "coste lineal permanente (≈ N/16 repasos diarios con el mazo maduro). "
  "2) <b>SM-2</b> compra casi la misma retención con mucho menos trabajo porque el intervalo "
  "crece geométricamente con el historial. "
  "3) La cadena de Markov de Leitner da fórmulas cerradas (repasos esperados, tasa en "
  "régimen) que la simulación reproduce — el modelo matemático no es decorativo, predice. "
  "4) La elección de producto (SM-2 en la UI, Leitner como espejo analítico) queda "
  "cuantitativamente justificada.")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Métricas — Repaso espaciado (SM-2 vs Leitner)")
doc.build(story)
print(f"-> {SALIDA}")
