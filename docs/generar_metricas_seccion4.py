# -*- coding: utf-8 -*-
"""Genera docs/metricas-seccion4.pdf: métricas de la Sección 4 (juegos).
Formaliza los tres algoritmos (LCG, grafo de Hamming 1 + BFS, backtracking) y
presenta las medidas REALES de docs/datos-juegos.json (ejecutar antes
`npm run simular-juegos`, que corre los motores JS de producción) y los
conteos de src/data/juegos.json, así el PDF siempre refleja el corpus vigente.

Uso:  PYTHONUTF8=1 python docs/generar_metricas_seccion4.py
"""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable)

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).with_name("metricas-seccion4.pdf")
JUEGOS = json.loads((RAIZ / "src" / "data" / "juegos.json").read_text(encoding="utf-8"))
STATS = json.loads((RAIZ / "docs" / "datos-juegos.json").read_text(encoding="utf-8"))

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


ESC = STATS["escalera"]
CRU = STATS["crucigrama"]

# --- Portada -----------------------------------------------------------------
story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("Sección 4 — Juegos", STIT))
story.append(Paragraph("Métricas: el grafo de Hamming 1 del corpus, la tasa de éxito del "
                       "backtracking y el determinismo por semilla, medidos sobre los "
                       "motores reales", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. Qué se mide y cómo")
p("Todas las cifras de este documento salen de <b>ejecutar los motores de producción</b> "
  "(src/engine/escalera.js y crucigrama.js) con <font face='Courier'>npm run simular-juegos</font> "
  "(simulacion/juegos-stats.mjs → docs/datos-juegos.json, mismo patrón que la comparación "
  "SM-2/Leitner de la Sección 2). No hay reimplementación paralela: si el motor cambia, las "
  "métricas cambian con él. Para la <b>escalera</b> se caracteriza el grafo de palabras del "
  "corpus (¿existen retos? ¿de qué dificultades?); para el <b>crucigrama</b>, un barrido de "
  f"{CRU['8']['semillas']} semillas por tamaño mide tasa de éxito, densidad y coste.")

h1("2. Escalera: el grafo de Hamming 1 del corpus")
h2("2.1 Formalización")
p("G<sub>L</sub> = (V, E) con V = palabras de longitud L del léxico (solo ASCII) y "
  "{u, v} ∈ E ⇔ d<sub>H</sub>(u, v) = 1. Un reto de k pasos es un par con "
  "dist<sub>G</sub>(origen, destino) = k; BFS certifica la distancia en O(V + E). La "
  "construcción del grafo usa cubetas comodín (L máscaras por palabra): O(n·L) contra el "
  "O(n²·L) de comparar parejas.")
h2("2.2 El grafo medido, por longitud")
filas = [["L", "Nodos", "Aristas", "Componentes", "Gigante", "Aisladas",
          "Diámetro*", "Dist. media*"]]
for L in sorted(ESC):
    e = ESC[L]
    filas.append([L, e["nodos"], e["aristas"], e["numComponentes"],
                  e["mayoresComponentes"][0], e["aisladas"], e["diametro"],
                  e["distanciaMedia"]])
tabla(filas, [1.1 * cm, 1.7 * cm, 1.8 * cm, 2.6 * cm, 1.9 * cm, 1.9 * cm, 2.1 * cm, 2.5 * cm])
p("* Diámetro y distancia media sobre pares alcanzables (dentro de cada componente). El "
  "grafo NO es conexo — el léxico de un corpus literario no es un diccionario exhaustivo — "
  "pero la <b>componente gigante</b> basta: el generador de retos solo elige pares a "
  "distancia exacta k, que por definición viven en la misma componente. Nótese la forma de "
  "campana con la longitud: con L=3 hay pocas palabras pero muy conectadas; con L=5 hay "
  "más palabras pero el espacio 26<super>5</super> está mucho más vacío y las vecinas "
  "escasean.")

h2("2.3 ¿Existen retos para cada dificultad?")
filas = [["L", "Pares alcanzables"] + [f"a distancia {k}" for k in (3, 4, 5, 6)]]
for L in sorted(ESC):
    e = ESC[L]
    filas.append([L, e["paresAlcanzables"]] +
                 [e["paresPorDistancia"].get(str(k), 0) for k in (3, 4, 5, 6)])
tabla(filas, [1.2 * cm, 3.4 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm])
p("Los cuatro niveles de dificultad que ofrece la UI (3–6 pasos) tienen cientos o miles de "
  "pares candidatos en cada longitud: el selector nunca cae en vacío. La cola de la "
  "distribución (hasta el diámetro, 12–19 según L) queda como margen para dificultades "
  "futuras.")

h1("3. Crucigrama: el backtracking medido")
h2("3.1 Formalización")
p("Colocar n palabras entrelazadas es un problema de satisfacción de restricciones "
  "(variables = palabras; dominios = colocaciones legales; restricciones = coincidencia de "
  "letra en cruces, extremos libres, sin contactos laterales, ≥ 1 cruce por palabra). La "
  "búsqueda es en profundidad con retroceso: el anclaje en cruces reduce el dominio de cada "
  "variable de O(filas·columnas·2) a las casillas que ya contienen una letra de la palabra, "
  "y el orden «más cruces primero» prioriza tableros densos. Presupuesto de 5.000 nodos y "
  "degradación n → n−1 garantizan terminación con salida.")
h2("3.2 Barrido de semillas")
filas = [["n pedido", "Semillas", "Tasa de éxito", "Palabras medias", "Cruces medios",
          "Densidad media", "ms / tablero"]]
for n in sorted(CRU, key=int):
    c = CRU[n]
    filas.append([n, c["semillas"], f"{c['tasaExito'] * 100:.1f}%", c["palabrasMedias"],
                  c["crucesMedios"], c["densidadMedia"], c["msPorTablero"]])
tabla(filas, [1.9 * cm, 1.9 * cm, 2.5 * cm, 2.9 * cm, 2.5 * cm, 2.8 * cm, 2.3 * cm])
p(f"Con el pool real ({STATS['entradasCrucigrama']} entradas, 30 candidatas barajadas por "
  "semilla) el backtracking coloca las n palabras pedidas en el <b>100% de las semillas</b> "
  "probadas y en décimas de milisegundo: el presupuesto de nodos es un seguro, no un coste. "
  "Cruces medios ≈ n − 1 con excedente pequeño: el tablero típico es un árbol de palabras "
  "con algún cruce extra — exactamente lo que las reglas permiten sin forzar rejillas "
  "imposibles. La densidad (casillas ocupadas / rectángulo envolvente) baja suavemente con "
  "n: tableros más grandes se dispersan, pero no colapsan.")

h1("4. Codenames: la semilla como canal")
p("La partida entera se codifica en 6 caracteres: 2 de vocabulario (idioma × nivel) y 4 de "
  "semilla en alfabeto de 36 símbolos → 36<super>4</super> = 1.679.616 tableros por "
  "vocabulario. El LCG "
  "(a = 1103515245, c = 12345, m = 2³¹, los parámetros de la libc clásica) genera la "
  "permutación de palabras (Fisher–Yates) y el reparto de colores 9/8/7/1. La propiedad que "
  "importa no es la calidad criptográfica (irrelevante aquí) sino el <b>determinismo "
  "multiplataforma</b>: la aritmética entera de JS reproduce el mismo tablero en cualquier "
  "dispositivo, y la semilla sustituye al servidor.")
code("x_{i+1} = (a·x_i + c) mod m      con x_0 = hash(semilla)\n"
     "36^4 = 1 679 616 tableros/vocabulario · 13 vocabularios")

h1("5. Determinismo transversal")
p("Los tres juegos comparten el mismo generador (board.js) y la misma disciplina que las "
  "Secciones 2 y 3: <b>el azar solo entra por la semilla</b>. Consecuencias medibles: los "
  "tests de los motores pueden afirmar igualdad exacta de retos y tableros "
  "(<font face='Courier'>toEqual</font> entre dos llamadas con la misma semilla); un reto de "
  "escalera o un crucigrama son compartibles por URL/string sin estado en servidor; y las "
  "estadísticas de este documento son reproducibles con "
  "<font face='Courier'>npm run simular-juegos</font>.")

h1("6. Limitaciones y trabajo futuro")
p("<b>El grafo hereda el corpus.</b> Las glosas y las palabras vienen de lecturas "
  "literarias: hay formas conjugadas raras en la escalera y alguna glosa contextual "
  "(«hoch» → «anticiclón» si en el texto era el sustantivo Hoch). El filtro es léxico, no "
  "semántico. <b>Sin umlauts.</b> Excluir ä/ö/ü/ß simplifica el tecleo pero recorta el "
  "alemán real; una alternativa futura es aceptar ae/oe/ue como equivalentes. "
  "<b>Crucigrama sin rejilla simétrica.</b> Se genera estilo «entrelazado libre», no la "
  "rejilla simétrica de periódico (eso exigiría diccionarios mucho mayores y otro "
  "algoritmo, p. ej. dancing links). <b>Futuro</b>: retos diarios (semilla = fecha), "
  "palabras de la bolsa del usuario como pool del crucigrama (conectaría con la Sección 2), "
  "y dificultad de la escalera por rareza de las palabras además de por distancia.")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Sección 4 — Juegos (métricas)")
doc.build(story)
print(f"-> {SALIDA}")
