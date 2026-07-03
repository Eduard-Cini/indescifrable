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
WOR = STATS["wordle"]
SOP = STATS["sopa"]

# --- Portada -----------------------------------------------------------------
story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("Sección 4 — Juegos", STIT))
story.append(Paragraph("Métricas: el grafo de Hamming 1 del corpus, la tasa de éxito del "
                       "backtracking, la entropía del Wordle y el determinismo por "
                       "semilla, medidos sobre los motores reales", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. Qué se mide y cómo")
p("Todas las cifras de este documento salen de <b>ejecutar los motores de producción</b> "
  "(src/engine/escalera.js y crucigrama.js) con <font face='Courier'>npm run simular-juegos</font> "
  "(simulacion/juegos-stats.mjs → docs/datos-juegos.json, mismo patrón que la comparación "
  "SM-2/Leitner de la Sección 2). No hay reimplementación paralela: si el motor cambia, las "
  "métricas cambian con él. Para la <b>escalera</b> se caracteriza el grafo de palabras del "
  "corpus (¿existen retos? ¿de qué dificultades?); para el <b>crucigrama</b> y la <b>sopa</b>, "
  f"un barrido de {CRU['8']['semillas']} semillas por tamaño mide tasa de éxito, densidad y "
  "coste; para el <b>Wordle</b>, un solver voraz por entropía juega contra TODOS los "
  "secretos posibles de cada longitud.")

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

h1("4. Adivina la palabra: la entropía medida")
h2("4.1 Formalización")
p("Sea S el conjunto de candidatas. Un intento g induce la partición de S por patrones de "
  "feedback (unión disjunta de clases S<sub>p</sub> = {s : feedback(s, g) = p}). La "
  "información esperada de g es la entropía de Shannon H(g) = −Σ (|S<sub>π</sub>|/|S|) · "
  "log2(|S<sub>π</sub>|/|S|); el máximo teórico con |S| candidatas es log2|S| (partición en "
  "clases unitarias: el intento identificaría el secreto de golpe). El solver voraz juega "
  "el argmax de H sobre las candidatas consistentes en cada turno — voraz, no óptimo: el "
  "árbol de decisión óptimo exige minimizar la profundidad esperada, no la ganancia del "
  "turno (véase §9).")
h2("4.2 Resultados por longitud")
filas = [["L", "Palabras", "Mejor 1er intento", "H (bits)", "máx. log2|S|",
          "Intentos medios", "Resuelto en ≤ 6"]]
for L in sorted(WOR):
    w = WOR[L]
    filas.append([L, w["palabras"], f"«{w['mejorPrimerIntento']}»",
                  w["entropiaPrimerIntento"], w["entropiaMaxima"],
                  w["intentosMedios"], f"{w['resueltosEnSeis'] * 100:.1f}%"])
tabla(filas, [0.9 * cm, 1.9 * cm, 3.3 * cm, 1.9 * cm, 2.4 * cm, 2.9 * cm, 2.7 * cm])
dist4 = WOR["4"]["distribucion"]; dist5 = WOR["5"]["distribucion"]
p("Distribución de intentos del solver (L=4): "
  + ", ".join(f"{t}: {n}" for t, n in sorted(dist4.items(), key=lambda x: int(x[0])))
  + ". (L=5): "
  + ", ".join(f"{t}: {n}" for t, n in sorted(dist5.items(), key=lambda x: int(x[0])))
  + ".")
p("Dos lecturas: (1) el mejor primer intento aporta ~4.2/5.6 bits de los ~8.1/8.8 posibles "
  "— un solo feedback no identifica el secreto, pero recorta el espacio en un factor "
  "2<super>H</super> ≈ 18–49; (2) el solver voraz resuelve casi todo el diccionario dentro "
  "de los 6 intentos del juego (99.3–99.8%) con ~3 de media: la cota de 6 intentos de la UI "
  "es holgada pero no trivial, señal de dificultad bien calibrada. El contador «quedan N "
  "posibles» de la UI muestra al alumno exactamente |S| tras cada intento.")

h1("5. Sopa de letras: colocación aleatorizada medida")
filas = [["n pedido", "Semillas", "Sopas completas", "Palabras medias"]]
for n in sorted(SOP, key=int):
    s = SOP[n]
    filas.append([n, s["semillas"], f"{s['tasaCompleta'] * 100:.1f}%", s["palabrasMedias"]])
tabla(filas, [2.2 * cm, 2.2 * cm, 3.2 * cm, 3.2 * cm])
p("La colocación aleatorizada (sin backtracking: sortear y reintentar) coloca las n "
  "palabras pedidas en el 100% de las semillas para n = 6–10 en la cuadrícula 12×12: con "
  "esa holgura de espacio, el retroceso sería maquinaria de más. El contraste con el "
  "crucigrama es el punto pedagógico: misma familia de problema, pero la restricción de "
  "conectividad (cada palabra debe cruzar otra) es la que obliga a retroceder.")

h1("6. Codenames: la semilla como canal")
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

h1("7. Los juegos por lectura: disponibilidad medida")
p("Los cuatro juegos de palabras se pueden jugar con el vocabulario de UNA lectura: la "
  "navegación va por juego y, dentro de cada juego, se elige el vocabulario (el corpus "
  "entero o una lectura). La disponibilidad no es una lista curada: cada juego "
  "tiene un criterio formal en src/engine/juegos.js — escalera: existe un par a distancia "
  "≥ 3 en el grafo de Hamming de la lectura; Wordle: alguna longitud con ≥ 12 palabras; "
  "crucigrama/sopa: ≥ 6 entradas con pista. El índice de cada juego lista solo las "
  "lecturas que lo aguantan. La tabla sale de ejecutar esos criterios sobre los pools "
  "reales (pipeline/juegos.py agrupa las partes de un libro por título):")
filas = [["Lectura", "Nivel", "L=3/4/5", "Entradas", "Juegos disponibles"]]
for lec in STATS["lecturas"]:
    p_ = lec["palabrasPorLongitud"]
    filas.append([
        lec["titulo"], lec["nivel"],
        f"{p_.get('3', 0)}/{p_.get('4', 0)}/{p_.get('5', 0)}",
        lec["entradasCrucigrama"],
        ", ".join(lec["disponibles"]),
    ])
tabla(filas, [4.6 * cm, 2.3 * cm, 2.2 * cm, 1.9 * cm, 5.4 * cm])
p("El patrón confirma la intuición pedagógica que motivó el diseño: las lecturas de "
  "principiante (30-40 palabras útiles) no sostienen ni el grafo de la escalera (sin pares "
  "a distancia 3) ni un diccionario de Wordle, pero sí crucigrama y sopa; las intermedias "
  "ganan el Wordle y, las más ricas, la escalera; los libros lo ofrecen todo. El criterio "
  "es una función del vocabulario, así que al añadir lecturas la tabla se actualiza sola.")

h1("8. Determinismo transversal")
p("Los cinco juegos comparten el mismo generador (board.js) y la misma disciplina que las "
  "Secciones 2 y 3: <b>el azar solo entra por la semilla</b>. Consecuencias medibles: los "
  "tests de los motores pueden afirmar igualdad exacta de retos y tableros "
  "(<font face='Courier'>toEqual</font> entre dos llamadas con la misma semilla); un reto de "
  "escalera o un crucigrama son compartibles por URL/string sin estado en servidor; y las "
  "estadísticas de este documento son reproducibles con "
  "<font face='Courier'>npm run simular-juegos</font>.")

h1("9. Limitaciones y trabajo futuro")
p("<b>El grafo hereda el corpus.</b> Las glosas y las palabras vienen de lecturas "
  "literarias: hay formas conjugadas raras en la escalera y alguna glosa contextual "
  "(«hoch» → «anticiclón» si en el texto era el sustantivo Hoch). El filtro es léxico, no "
  "semántico. <b>Sin umlauts.</b> Excluir ä/ö/ü/ß simplifica el tecleo pero recorta el "
  "alemán real; una alternativa futura es aceptar ae/oe/ue como equivalentes. "
  "<b>Crucigrama sin rejilla simétrica.</b> Se genera estilo «entrelazado libre», no la "
  "rejilla simétrica de periódico (eso exigiría diccionarios mucho mayores y otro "
  "algoritmo, p. ej. dancing links). <b>Solver voraz, no óptimo.</b> Maximizar la entropía "
  "del turno no minimiza la profundidad esperada del árbol de decisión (el óptimo exacto es "
  "un problema de búsqueda en árboles con poda, resuelto por fuerza bruta en el Wordle "
  "inglés); para caracterizar la dificultad del diccionario, el voraz basta y es el "
  "estándar de referencia. <b>Futuro</b>: retos diarios (semilla = fecha), palabras de la "
  "bolsa del usuario como pool del crucigrama y de la sopa (el Codenames ya la acepta como "
  "vocabulario del tablero), y dificultad de la escalera por rareza de las palabras además "
  "de por distancia.")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Sección 4 — Juegos (métricas)")
doc.build(story)
print(f"-> {SALIDA}")
