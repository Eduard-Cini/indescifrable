# -*- coding: utf-8 -*-
"""Genera docs/autoaprendizaje-seccion4.pdf: ruta de estudio autodidacta de la
Sección 4 (juegos): grafos y BFS, backtracking/CSP y aleatoriedad determinista
(LCG, Fisher–Yates), siempre anclada al código del repo.

Uso:  PYTHONUTF8=1 python docs/generar_autoaprendizaje_seccion4.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, PageBreak)

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).with_name("autoaprendizaje-seccion4.pdf")

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


# --- Portada -----------------------------------------------------------------
story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("Sección 4 — Juegos", STIT))
story.append(Paragraph("Ruta de autoaprendizaje: grafos y BFS, backtracking y "
                       "aleatoriedad determinista, desde cero hasta defender el código "
                       "de esta sección", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("0. Mapa de la ruta")
tabla([
    ["Fase", "Tema", "Tiempo orientativo", "Resultado"],
    ["1", "Grafos y búsqueda en anchura (BFS)", "1-2 semanas",
     "Construir el grafo de Hamming del corpus y explicar por qué BFS da el mínimo"],
    ["2", "Backtracking y problemas de satisfacción de restricciones", "1-2 semanas",
     "Trazar a mano la colocación de un crucigrama de 4 palabras, con retroceso"],
    ["3", "Aleatoriedad determinista: LCG, semillas y Fisher–Yates", "1 semana",
     "Predecir un tablero de Codenames a partir de su semilla, a mano"],
    ["4", "Implementación y experimentos en el repo", "1-2 semanas",
     "Añadir una variante de juego y medirla con simular-juegos"],
], [1.2 * cm, 6.6 * cm, 3.2 * cm, 5.4 * cm])
p("Regla de oro (la misma de las Secciones 2 y 3): cada concepto se aprende <b>tres "
  "veces</b> — en papel (la definición y la prueba), en la consola (el número) y en el repo "
  "(el código que lo usa).")

# ---------------------------------------------------------------------------
h1("Fase 1 — Grafos y búsqueda en anchura")
h2("1.1 El juego más viejo de la teoría de grafos aplicada")
p("La escalera de palabras (<i>word ladder / doublets</i>) la inventó Lewis Carroll en 1877; "
  "Donald Knuth la convirtió en el ejemplo canónico de grafo real en los años 90 con las "
  "5.757 palabras inglesas de 5 letras (el grafo de <i>words</i> del Stanford GraphBase). "
  "La versión de este repo es la misma idea sobre el corpus alemán de la plataforma: "
  "vértices = palabras, aristas = distancia de Hamming 1. Todo lo interesante del juego es "
  "una propiedad del grafo: si hay solución (conectividad), cuál es la solución perfecta "
  "(distancia) y qué retos existen (distribución de distancias).")
h2("1.2 BFS y por qué da el camino mínimo")
p("BFS explora por <b>niveles</b>: primero los vecinos a distancia 1, luego los de 2… La "
  "invariante — cuando BFS alcanza un nodo, lo hace por un camino de longitud mínima — se "
  "demuestra por inducción sobre el nivel, y solo vale en grafos <b>no ponderados</b> (con "
  "pesos hace falta Dijkstra). Coste O(V + E) con cola; en "
  "<font face='Courier'>src/engine/escalera.js</font> la cola es la lista «frontera» de cada "
  "nivel (<font face='Courier'>distanciasDesde</font>) y la reconstrucción del camino guarda el "
  "predecesor de cada nodo (<font face='Courier'>caminoMinimo</font>).")
h2("1.3 La construcción por cubetas comodín")
p("El truco no-obvio del motor: en vez de comparar todas las parejas (O(n²·L)), cada "
  "palabra entra en L cubetas con una posición enmascarada (hand → *and, h*nd, ha*d, han*) "
  "y dos palabras son vecinas ⇔ comparten cubeta. Piénsalo como un hash por «patrón con "
  "comodín». Ejercicio de 15 minutos: demuestra las dos direcciones del ⇔ y encuentra qué "
  "pasaría si dos longitudes distintas compartieran cubeta (no pueden: la máscara conserva "
  "la longitud).")
code("node -e \"const {construirGrafo, estadisticas} = await import('./src/engine/escalera.js');\n"
     "const j = JSON.parse(require('fs').readFileSync('src/data/juegos.json','utf8'));\n"
     "console.log(estadisticas(construirGrafo(Object.keys(j.escalera['4']))))\"")
h2("1.4 Qué estudiar y dónde")
tabla([
    ["Recurso", "Qué aporta"],
    ["CLRS «Introduction to Algorithms», cap. de grafos elementales (BFS/DFS)",
     "La prueba formal de que BFS calcula distancias; representaciones de grafos"],
    ["Knuth, «The Stanford GraphBase» (el grafo de <i>words</i>)",
     "La escalera de palabras como objeto de estudio serio; estadísticas del grafo inglés"],
    ["Skiena, «The Algorithm Design Manual», cap. de grafos",
     "Criterio práctico: qué representación y qué recorrido usar según el problema"],
], [8.6 * cm, 7.8 * cm])

# ---------------------------------------------------------------------------
h1("Fase 2 — Backtracking y satisfacción de restricciones")
h2("2.1 El patrón general")
p("Backtracking = búsqueda en profundidad sobre soluciones parciales: extender (elegir "
  "variable y valor legal), recursar, y si la rama muere, <b>deshacer</b> y probar el "
  "siguiente valor. Las tres decisiones de diseño que separan un backtracking de juguete de "
  "uno útil: (1) <b>qué poda</b> hace ilegales las extensiones pronto; (2) <b>en qué "
  "orden</b> se prueban variables y valores; (3) <b>cuándo parar</b> si el peor caso "
  "exponencial asoma. En <font face='Courier'>src/engine/crucigrama.js</font>: la poda es el "
  "anclaje en cruces + reglas de legalidad; el orden es «más cruces primero»; el paro es el "
  "presupuesto de 5.000 nodos con degradación n → n−1.")
h2("2.2 El crucigrama como CSP")
p("Variables = palabras a colocar; dominio de cada una = sus colocaciones legales (que "
  "cambian con el tablero: por eso el dominio se recalcula al entrar en cada nodo); "
  "restricciones = letra igual en el cruce, extremos libres, sin contactos laterales. "
  "Ejercicio de 30 minutos: coloca a mano «anna, nein, insel, esel» con las reglas de "
  "<font face='Courier'>puedeColocar</font> dibujando el tablero en papel cuadriculado, y "
  "provoca un retroceso real eligiendo mal la segunda palabra. Después compara con "
  "<font face='Courier'>src/engine/crucigrama.test.js</font>, que usa exactamente ese pool.")
h2("2.3 Presupuestos y anytime")
p("El peor caso del backtracking es exponencial y no se puede eliminar, solo domesticar: "
  "un <b>presupuesto de nodos</b> convierte el algoritmo en <i>anytime</i> (siempre hay "
  "respuesta, quizá con n−1 palabras). La medición del repo "
  "(<font face='Courier'>npm run simular-juegos</font>) muestra que con el pool real el "
  "presupuesto nunca se activa (100% de éxito en &lt; 0,5 ms) — pero el seguro debe existir "
  "ANTES de saberlo. Discute: ¿por qué se degrada n en vez de aumentar el presupuesto?")
h2("2.4 Qué estudiar y dónde")
tabla([
    ["Recurso", "Qué aporta"],
    ["Russell &amp; Norvig, «Artificial Intelligence: A Modern Approach», cap. de CSP",
     "Formalización de variables/dominios/restricciones, heurísticas de orden (MRV, LCV)"],
    ["CLRS / Skiena, secciones de backtracking",
     "El patrón extender-recursar-deshacer y sus podas"],
    ["Knuth, «The Art of Computer Programming» vol. 4B, «Dancing Links»",
     "El siguiente nivel: cobertura exacta para rejillas de crucigrama de periódico"],
], [8.6 * cm, 7.8 * cm])

# ---------------------------------------------------------------------------
story.append(PageBreak())
h1("Fase 3 — Aleatoriedad determinista")
h2("3.1 El LCG y la semilla como protocolo")
p("Un generador congruencial lineal (x<sub>i+1</sub> = (a·x<sub>i</sub> + c) mod m) es el "
  "PRNG más simple que existe; sus debilidades estadísticas (planos de Marsaglia, período "
  "corto en los bits bajos) lo descartan para criptografía o simulación seria, pero aquí la "
  "propiedad que importa es otra: <b>reproducibilidad exacta multiplataforma</b>. La semilla "
  "de Codenames (<font face='Courier'>DP-K9A2</font>) es un protocolo de comunicación de 6 "
  "caracteres: dos capitanes en dispositivos distintos derivan el mismo tablero sin "
  "servidor. La misma disciplina gobierna las Secciones 2–4: el azar solo entra por la "
  "semilla (tests con <font face='Courier'>toEqual</font>, retos compartibles, métricas "
  "reproducibles).")
h2("3.2 Fisher–Yates y el sesgo del barajado ingenuo")
p("Barajar bien es elegir una permutación uniforme: Fisher–Yates lo hace en O(n) "
  "intercambiando cada posición con una aleatoria de las restantes "
  "(<font face='Courier'>barajar</font> en board.js). El clásico error — "
  "<font face='Courier'>sort(() =&gt; Math.random() − 0.5)</font> — produce permutaciones "
  "sesgadas. Ejercicio de 15 minutos: enumera las 27 trayectorias del barajado ingenuo de "
  "[a, b, c] y comprueba que las 6 permutaciones no salen equiprobables.")
h2("3.3 Una trampa real de este repo")
p("El LCG de board.js devuelve <font face='Courier'>state / (m − 1)</font> con "
  "<font face='Courier'>state = hash(semilla)</font>… y el hash de JS puede ser <b>negativo</b>: "
  "el «uniforme en [0,1)» puede salir negativo o exactamente 1, y Fisher–Yates indexaría "
  "fuera del array. La corrección (<font face='Courier'>crearGeneradorNormalizado</font>: tomar "
  "la parte fraccionaria) vive en board.js y la usan gramática, escalera y crucigrama — "
  "pero NO se cambió el generador original, porque habría cambiado todos los tableros de "
  "Codenames ya compartidos. Moraleja doble: valida el rango de tu PRNG, y trata la función "
  "semilla → salida como API pública congelada.")
h2("3.4 Qué estudiar y dónde")
tabla([
    ["Recurso", "Qué aporta"],
    ["Knuth, TAOCP vol. 2, «Seminumerical Algorithms», cap. 3",
     "La teoría del LCG: elección de a, c, m; tests espectrales; por qué los bits bajos "
     "son débiles"],
    ["Fisher–Yates / algoritmo de Durstenfeld (el artículo de Wikipedia es correcto y "
     "cita las fuentes)", "El barajado uniforme en O(n) y el catálogo de errores clásicos"],
    ["PCG (pcg-random.org), «PCG: A Family of Simple Fast Space-Efficient...»",
     "Qué usa un PRNG moderno y por qué; contraste instructivo con el LCG"],
], [8.6 * cm, 7.8 * cm])

# ---------------------------------------------------------------------------
h1("Fase 4 — Implementación y experimentos en el repo")
h2("4.1 Recorrido guiado del código")
tabla([
    ["Orden", "Archivo", "Qué mirar"],
    ["1", "src/engine/board.js", "LCG, hash de semilla, Fisher–Yates, composición "
     "vocabulario+semilla; el generador normalizado y su porqué"],
    ["2", "src/engine/escalera.js + escalera.test.js", "Cubetas comodín, BFS de niveles y "
     "de camino, generación de retos a distancia exacta"],
    ["3", "src/engine/crucigrama.js + crucigrama.test.js", "Reglas de legalidad, anclaje "
     "en cruces, retroceso con deshacer selectivo, numeración"],
    ["4", "pipeline/juegos.py", "Qué palabras entran a cada juego y por qué (ASCII, "
     "funcionales, frecuencia mínima)"],
    ["5", "simulacion/juegos-stats.mjs", "Cómo se mide un motor: mismos módulos que "
     "producción, barrido de semillas, salida versionada en docs/"],
], [1.3 * cm, 6.3 * cm, 8.8 * cm])
h2("4.2 Experimentos propuestos (de menor a mayor)")
p("<b>(a) Reto diario.</b> Semilla = fecha ISO → todos los usuarios del día juegan la misma "
  "escalera. Son ~5 líneas en la UI; discute por qué NO hay que tocar el motor. "
  "<b>(b) Distancia media por longitud.</b> Amplía juegos-stats.mjs para emitir el "
  "histograma completo de distancias y grafica la campana (¿por qué L=4 tiene la distancia "
  "media mayor que L=5 en este corpus?). "
  "<b>(c) Heurística MRV.</b> Cambia el orden de palabras del crucigrama a «menos "
  "colocaciones legales primero» y mide con el barrido de semillas si la densidad o el "
  "tiempo mejoran. "
  "<b>(d) Umlauts.</b> Acepta ae/oe/ue como ä/ö/ü en la escalera (normalización en ambos "
  "lados) y mide cuánto crece la componente gigante. "
  "<b>(e) Crucigrama personal.</b> Usa la bolsa de palabras del usuario (Sección 2) como "
  "pool — el puente natural entre juegos y repaso espaciado.")
h2("4.3 Criterio de «sección defendida»")
p("Sabes defender esta sección cuando puedes: (1) probar la invariante de BFS y explicar "
  "las cubetas comodín sin mirar el código; (2) trazar un retroceso real del crucigrama y "
  "justificar cada una de las tres reglas de legalidad con un contraejemplo; (3) explicar "
  "qué garantiza (y qué NO garantiza) un LCG y por qué aquí basta; y (4) reproducir "
  "cualquier cifra de metricas-seccion4.pdf con un comando.")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Sección 4 — Juegos (autoaprendizaje)")
doc.build(story)
print(f"-> {SALIDA}")
