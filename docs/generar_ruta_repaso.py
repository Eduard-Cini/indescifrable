# -*- coding: utf-8 -*-
"""Genera docs/ruta-aprendizaje-repaso.pdf: ruta de auto-aprendizaje de la
Sección 2 (repaso espaciado): herramientas matemáticas, algoritmos paso a paso
con ejemplos numéricos, insights de la implementación, paquetería, ejercicios
y recursos externos.

Uso:  PYTHONUTF8=1 python docs/generar_ruta_repaso.py
"""
import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, PageBreak)

SALIDA = Path(__file__).with_name("ruta-aprendizaje-repaso.pdf")

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


# --- Portada ---------------------------------------------------------------
story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("Ruta de auto-aprendizaje", STIT))
story.append(Paragraph("Sección 2 — Repaso espaciado: matemáticas, algoritmos, "
                       "implementación y recursos", SSUB))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("Para dominar por cuenta propia todo lo que usa esta sección: "
                       "de la curva de olvido a la cadena de Markov, con los ejemplos "
                       "corriendo en el propio repo.", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("0. Mapa de la ruta")
tabla([
    ["Fase", "Tema", "Tiempo orientativo", "Resultado"],
    ["1", "Curva de olvido, Zipf y logística", "1 semana",
     "Entender cada fórmula de engine/conocimiento.js"],
    ["2", "Cadenas de Markov", "1-2 semanas",
     "Derivar a mano π, E[repasos] y la tasa de engine/leitner.js"],
    ["3", "Algoritmos SRS: Leitner, SM-2, FSRS", "1 semana",
     "Recalcular la tabla de ejemplo de SM-2 sin mirar el código"],
    ["4", "Implementación y experimentos en el repo", "1-2 semanas",
     "Modificar la simulación y defender los resultados"],
], [1.2 * cm, 6.2 * cm, 3.4 * cm, 5.6 * cm])
p("Regla de oro: cada concepto se aprende <b>tres veces</b> — en papel (la fórmula), en la "
  "consola (el número) y en el repo (el código que lo usa). Las tres vistas están indicadas "
  "en cada fase.")

# ---------------------------------------------------------------------------
h1("Fase 1 — Herramientas matemáticas básicas")
h2("1.1 La curva de olvido (Ebbinghaus)")
p("Modelo: la probabilidad de recordar algo Δ días después del último repaso es "
  "<b>R = e^(−Δ/S)</b>, donde S es la <b>estabilidad</b> (en días) de esa memoria. "
  "Propiedades que hay que interiorizar: R(0) = 1; R(S) = e<super>−1</super> ≈ 0.37 (S es «la vida media "
  "natural» del recuerdo, salvo constante); y para recordar al 90% hay que preguntar en "
  "Δ ≈ 0.105·S — de ahí que un SRS con retención objetivo del 90% programe intervalos de "
  "una décima de la estabilidad.")
code("# En consola de Python:\n"
     "import math\n"
     "S = 6            # estabilidad de 6 días\n"
     "for d in (0, 1, 3, 6, 12): print(d, round(math.exp(-d/S), 3))\n"
     "# 0 1.0 | 1 0.846 | 3 0.607 | 6 0.368 | 12 0.135")
p("Dónde vive en el repo: <font face='Courier'>retrievability()</font> en engine/conocimiento.js (con "
  "S = max(intervalo, 0.5) y t recuperado del estado SM-2) y el alumno sintético de "
  "simulacion/comparar.mjs (con S que crece al acertar y se contrae al fallar).")
h2("1.2 La ley de Zipf y la escala zipf")
p("En un corpus, la frecuencia de la palabra de rango r cae como ~1/r: pocas palabras "
  "acaparan casi todas las apariciones. La <b>escala zipf</b> normaliza el conteo para poder "
  "comparar entre corpus: <b>zipf = log10(conteo/total · 10<super>6</super>)</b> (apariciones por millón, en "
  "logaritmo). Referencias mentales: zipf ≥ 5 son palabras funcionales (und, der); zipf ≈ 3 "
  "es vocabulario medio; zipf &lt; 2, palabras raras.")
h2("1.3 La función logística")
p("σ(x) = 1/(1+e^(−x)) convierte una puntuación en probabilidad. El prior del modelo es "
  "<b>P(conocer) = σ((zipf − z<sub>0</sub>)/τ)</b> con z<sub>0</sub> = 3.0 (el punto del 50%) y τ = 0.7 (cuán "
  "brusca es la transición). Ejercicio de 5 minutos: calcula P para «und» (zipf ≈ 4.5) y "
  "para un hapax (zipf ≈ 1.5) y comprueba contra la tabla de metricas-repaso.pdf.")

# ---------------------------------------------------------------------------
h1("Fase 2 — Cadenas de Markov (el corazón matemático)")
p("Una cadena de Markov es un proceso que salta entre estados donde el futuro solo depende "
  "del estado actual. Todo lo que usa esta sección cabe en cuatro ideas:")
tabla([
    ["Idea", "Definición operativa", "En Leitner"],
    ["Matriz de transición P", "P[i][j] = prob. de pasar de i a j; filas suman 1",
     "P[i][i+1] = p (acierto), P[i][1] = 1−p (fallo)"],
    ["Distribución estacionaria π", "π = πP; a la larga, fracción de visitas a cada estado",
     "En qué caja «vive» una palabra a largo plazo"],
    ["Tiempos de llegada", "h_i = E[pasos desde i hasta un objetivo]; sistema lineal",
     "Repasos/días esperados para llegar a la caja 5"],
    ["Recompensas por estado", "Cada visita a i «cuesta» c_i; coste medio = Σ π_i·c_i",
     "Cada caja espera I_i días → tasa = 1/Σ π_i·I_i"],
], [3.4 * cm, 6.8 * cm, 6.2 * cm])
h2("2.1 Ejemplo resuelto: Leitner con p = 0.9")
p("E[repasos hasta la caja 5] es la esperanza de la primera racha de 4 aciertos seguidos: "
  "<b>E = 1/p + 1/p<super>2</super> + 1/p<super>3</super> + 1/p<super>4</super></b>. "
  "Con p = 0.9: 1.111 + 1.235 + 1.372 + 1.524 ≈ "
  "<b>5.24 repasos</b>. Derivación (hazla en papel): h_i = 1 + p·h_{i+1} + (1−p)·h_1 con "
  "h_5 = 0; sustituye hacia atrás y despeja h_1. Los días esperados usan la misma "
  "recurrencia cambiando el «1» por el intervalo I_i de cada caja (≈ 18.1 días con p = 0.9).")
code("# Compruébalo contra el motor real (consola de Node en la raíz del repo):\n"
     "node -e \"import('./src/engine/leitner.js').then(L => {\n"
     "  console.log(L.repasosHastaUltimaCaja(0.9));   // 5.2415…\n"
     "  console.log(L.diasHastaUltimaCaja(0.9));      // 18.09…\n"
     "  console.log(L.distribucionEstacionaria(L.matrizTransicion(0.9)));\n"
     "})\"")
h2("2.2 Qué estudiar y dónde")
tabla([
    ["Recurso", "Qué aporta"],
    ["Grinstead &amp; Snell, «Introduction to Probability», cap. 11 (PDF libre en la web "
     "de Dartmouth)", "El capítulo canónico de cadenas de Markov: regulares, absorbentes, "
     "tiempos de absorción — exactamente la matemática de leitner.js"],
    ["Kemeny &amp; Snell, «Finite Markov Chains»", "Referencia clásica si quieres más "
     "profundidad (matriz fundamental N = (I−Q)<super>−1</super>)"],
    ["Vídeos: 3Blue1Brown (probabilidad) y cualquier serie de «Markov chains» "
     "(p. ej. Normalized Nerd en YouTube)", "Intuición visual de estados y estacionarias"],
    ["setosa.io/ev/markov-chains", "Visualización interactiva para jugar con matrices"],
], [8.2 * cm, 8.2 * cm])

# ---------------------------------------------------------------------------
story.append(PageBreak())
h1("Fase 3 — Los algoritmos SRS")
h2("3.1 Leitner (1972): el algoritmo de las cajas")
p("5 cajas con cadencias [1, 2, 4, 8, 16] días; acierto sube, fallo devuelve a la caja 1. "
  "Virtud: trivial de explicar y de implementar con fichas físicas. Defecto estructural "
  "(cuantificado en metricas-repaso.pdf): el intervalo tiene <b>techo</b>, así que un mazo "
  "maduro cuesta N/16 repasos diarios para siempre.")
h2("3.2 SM-2 (Wozniak, 1987): intervalos que crecen con el historial")
p("Cada ítem lleva (n, EF, I). Tras una respuesta de calidad q ∈ 0..5: si q &lt; 3, n = 0 e "
  "I = 0 (reaprender); si q ≥ 3, n aumenta e I(1) = 1, I(2) = 6, I(n) = round(I(n−1)·EF). "
  "El factor EF' = max(1.3, EF + 0.1 − (5−q)·(0.08 + (5−q)·0.02)) baja con «Difícil» (q=3, "
  "−0.14), no cambia con «Bien» (q=4) y sube con «Fácil» (q=5, +0.10). Ejemplo trabajado "
  "con EF constante 2.5 (todo «Bien»):")
n_, ef_, i_ = 0, 2.5, 0
filas = [["Repaso", "q", "n tras", "EF tras", "Intervalo (días)", "Vence (día acumulado)"]]
acum = 0
for rep in range(1, 7):
    n_ += 1
    i_ = 1 if n_ == 1 else 6 if n_ == 2 else round(i_ * ef_)
    acum += i_
    filas.append([str(rep), "4 (Bien)", str(n_), f"{ef_:.2f}", str(i_), str(acum)])
tabla(filas, [2.2 * cm, 2.6 * cm, 2.2 * cm, 2.4 * cm, 3.4 * cm, 3.6 * cm])
p("Seis aciertos llevan la palabra a un intervalo de ~94 días: el crecimiento geométrico es "
  "lo que abarata SM-2 frente a Leitner. Reproduce esta tabla a mano y luego con el motor:")
code("node -e \"import('./src/engine/srs.js').then(S => {\n"
     "  let e; const T = '2026-01-01T00:00:00.000Z';\n"
     "  for (let i = 0; i &lt; 6; i++) { e = S.calificar(e, 4, T); "
     "console.log(e.reps, e.ef, e.intervalo); }\n"
     "})\"")
h2("3.3 Más allá: half-life regression y FSRS")
p("La frontera actual ajusta la estabilidad por regresión sobre datos reales: "
  "<b>Half-Life Regression</b> (Settles &amp; Meeder, ACL 2016 — el paper de Duolingo, "
  "muy legible) y <b>FSRS</b> (Free Spaced Repetition Scheduler, el algoritmo moderno de "
  "Anki: estado (Dificultad, Estabilidad, Retrievability) con actualizaciones aprendidas de "
  "millones de repasos; su wiki en GitHub, open-spaced-repetition/fsrs4anki, trae toda la "
  "matemática). Son la extensión natural de esta sección si se quiere ir más lejos.")

# ---------------------------------------------------------------------------
h1("Fase 4 — La implementación de este repo, por dentro")
h2("4.1 Insights de diseño que conviene entender")
tabla([
    ["Insight", "Por qué importa"],
    ["Motores puros con tiempo inyectado (ahora como parámetro ISO)",
     "El mismo código corre en la UI, en los tests y en la simulación; sin mocks de reloj"],
    ["El estado SRS vive dentro de la entrada de la bolsa",
     "Una sola fuente de verdad en localStorage; agregar una palabra existente no lo pisa"],
    ["El último repaso no se guarda: se deriva (vencimiento − intervalo)",
     "El estado mínimo suficiente; menos campos que puedan desincronizarse"],
    ["Separar planificador (cuándo preguntar) de memoria (qué se recuerda)",
     "Es la estructura de la simulación y de toda la literatura SRS"],
    ["Contabilidad fiel a cada método al comparar",
     "Un fallo SM-2 cuesta 2 presentaciones (recicla en sesión); en Leitner 1 — compararlos "
     "con la misma contabilidad falsearía el coste"],
    ["Calibrar el alumno sintético antes de leer resultados",
     "Con S0 de horas la precisión cae al 25% y la comparación no informa; con precisión "
     "80-90% (como los SRS reales) los resultados son transferibles"],
], [7.2 * cm, 9.2 * cm])
h2("4.2 Paquetería y herramientas")
tabla([
    ["Herramienta", "Rol en la sección"],
    ["Vitest 4", "49 tests del engine (npm test); la especificación ejecutable de cada fórmula"],
    ["Node ≥ 20 (ESM)", "Corre la simulación directamente sobre src/engine/ (npm run simular)"],
    ["mulberry32", "RNG determinista de 32 bits: misma semilla → misma simulación"],
    ["ReportLab", "Genera estos PDF (docs/generar_*.py), tablas y gráficas nativas"],
    ["Python 3 + PYTHONUTF8=1", "pipeline/frecuencias.py y los generadores (regla: "
     "ensure_ascii=False para los umlauts)"],
    ["localStorage", "Persistencia sin backend: bolsa.v1, conocidas.v1, repasoPrevio.v1"],
], [4.4 * cm, 12 * cm])
h2("4.3 Experimentos propuestos (en orden de dificultad)")
p("1) Cambia la semilla y el horizonte de simulacion/comparar.mjs y verifica que las "
  "conclusiones no dependen del azar. "
  "2) Añade una caja 6 (intervalo 32) a INTERVALOS_CAJA y mide cuánto trabajo ahorra: ¿se "
  "acerca a SM-2? Predícelo antes con la fórmula de la tasa (1/Σ π·I). "
  "3) Haz que el alumno responda «Fácil» cuando R &gt; 0.95 y «Difícil» cuando R &lt; 0.6, y "
  "observa cómo EF separa palabras fáciles de difíciles. "
  "4) Implementa la retención objetivo: programa el siguiente repaso en Δ = −S·ln(0.9) en "
  "lugar de usar SM-2, y compárala con ambos (es la idea central de FSRS). "
  "5) Deriva la matriz fundamental N = (I−Q)<super>−1</super> de la cadena absorbente (caja 5 absorbente) "
  "y comprueba que N·1 reproduce repasosHastaUltimaCaja(p).")

h1("5. Recursos externos (lista corta y buena)")
tabla([
    ["Recurso", "Tipo", "Para qué"],
    ["Wozniak — descripción original de SM-2 (supermemo.guru / super-memory.com, "
     "«Application of a computer to improve the results…»)", "Fuente primaria",
     "El algoritmo tal como se publicó"],
    ["Manual de Anki (docs.ankiweb.net), sección «What algorithm»", "Documentación",
     "Cómo un producto real adapta SM-2/FSRS"],
    ["Settles &amp; Meeder (2016), «A Trainable Spaced Repetition Model for Language "
     "Learning» (ACL)", "Paper", "Half-life regression con datos de Duolingo"],
    ["open-spaced-repetition/fsrs4anki (GitHub, wiki «The Algorithm»)", "Código + docs",
     "FSRS: el estado del arte, con fórmulas"],
    ["Murre &amp; Dros (2015), «Replication and Analysis of Ebbinghaus' Forgetting "
     "Curve» (PLOS ONE)", "Paper", "La curva de olvido con datos modernos"],
    ["Grinstead &amp; Snell, cap. 11 (Dartmouth, PDF libre)", "Libro",
     "Cadenas de Markov completas con ejercicios"],
    ["gwern.net/spaced-repetition", "Ensayo/recopilación",
     "Panorama y bibliografía comentada de todo el campo"],
], [8.6 * cm, 3 * cm, 4.8 * cm])

h1("6. Lista de verificación de dominio")
p("Puedes dar la sección por dominada cuando, sin mirar el código: "
  "(a) escribes la recurrencia de SM-2 y explicas por qué «Bien» no mueve EF; "
  "(b) derivas E = Σ p^(−j) para la racha de aciertos de Leitner; "
  "(c) explicas por qué la tasa estacionaria es 1/Σ π·I y la calculas para p = 0.9; "
  "(d) justificas los cuatro casos de P(conocer) del modelo de conocimiento; "
  "(e) predices el efecto de añadir una caja a Leitner antes de simularlo — y luego lo "
  "confirmas con npm run simular.")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Ruta de auto-aprendizaje — Repaso espaciado")
doc.build(story)
print(f"-> {SALIDA}")
