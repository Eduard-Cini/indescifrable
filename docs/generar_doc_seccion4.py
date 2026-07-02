# -*- coding: utf-8 -*-
"""Genera docs/documentacion-seccion4.pdf: documentación técnica de la Sección 4
(juegos): Codenames determinista por semilla, escalera de palabras (grafo de
Hamming 1 + BFS) y crucigrama (colocación por backtracking).

Uso:  PYTHONUTF8=1 python docs/generar_doc_seccion4.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable)

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).with_name("documentacion-seccion4.pdf")

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
story.append(Paragraph("Sección 4 — Juegos", STIT))
story.append(Paragraph("Documentación técnica: Codenames determinista por semilla, "
                       "escalera de palabras (grafo de Hamming 1 + BFS) y crucigrama "
                       "(colocación por backtracking)", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. Qué resuelve esta sección")
p("La Sección 4 convierte el vocabulario de la plataforma en <b>juegos de palabras</b>, cada "
  "uno con un algoritmo clásico como corazón: el <b>Codenames</b> (Indescifrable) reparte un "
  "tablero 5×5 con un generador congruencial lineal, de modo que una semilla de 6 caracteres "
  "reemplaza a un servidor; la <b>escalera de palabras</b> pide transformar una palabra "
  "alemana en otra cambiando una letra por paso — un camino en el grafo de Hamming 1 que se "
  "resuelve con BFS; y el <b>crucigrama</b> coloca palabras alemanas entrelazadas con "
  "<b>backtracking</b>, con las pistas en español. Los tres comparten el principio de la "
  "plataforma: <b>sin APIs en vivo</b> — todo es determinista por semilla, así que compartir "
  "una partida es compartir un string.")
p("La escalera y el crucigrama son además <b>pedagógicos</b>: sus palabras salen del corpus "
  "de lecturas (Sección 1), cada peldaño de la escalera muestra su traducción y las pistas "
  "del crucigrama son las glosas españolas del léxico. Jugar es repasar vocabulario.")

h1("2. Mapa de archivos")
tabla([
    ["Pieza", "Archivo", "Qué contiene"],
    ["Selección de palabras", "pipeline/juegos.py",
     "Extrae de lexico.json las formas ASCII (L=3–5) con glosa para la escalera "
     "y 400 lemas frecuentes no funcionales como entradas del crucigrama"],
    ["Datos", "src/data/juegos.json",
     "escalera{L: {palabra: glosa}} y crucigrama[{palabra, pista}]; lo "
     "sobreescribe el pipeline"],
    ["Motor escalera", "src/engine/escalera.js (+ .test)",
     "Grafo por cubetas comodín, BFS (camino mínimo y niveles), generación de "
     "retos por semilla, validación de pasos, estadísticas"],
    ["Motor crucigrama", "src/engine/crucigrama.js (+ .test)",
     "Reglas de colocación, búsqueda por backtracking con presupuesto, "
     "numeración clásica, cuadrícula y métricas"],
    ["Motor Codenames", "src/engine/board.js (+ .test)",
     "LCG por semilla, Fisher–Yates, composición/parseo de semilla con código "
     "de vocabulario"],
    ["UI", "src/secciones/juegos/*.jsx + juegos.css",
     "/juegos (hub), /juegos/escalera, /juegos/crucigrama; Codenames en "
     "/juegos/codenames (src/JuegoApp.jsx, previo a esta sección)"],
    ["Estadísticas", "simulacion/juegos-stats.mjs",
     "Ejecuta los motores reales → docs/datos-juegos.json (lo consume el PDF "
     "de métricas)"],
], [3.1 * cm, 5.6 * cm, 7.7 * cm])

h1("3. Datos: pipeline/juegos.py → juegos.json")
p("El pipeline no inventa vocabulario: filtra el léxico de la Sección 1. Para la "
  "<b>escalera</b> toma las formas alemanas de 3–5 letras <b>solo ASCII</b> (sin umlauts ni "
  "ß: el alumno hispanohablante debe poder teclearlas) con su traducción. Para el "
  "<b>crucigrama</b> toma <b>lemas</b> de 4–9 letras atestiguados ≥ 2 veces en las lecturas "
  "(frecuencias de la Sección 2), excluyendo una lista curada de <b>palabras funcionales</b> "
  "(artículos, preposiciones, pronombres, auxiliares): «der» es frecuentísimo pero la pista "
  "«el / la» no enseña nada. Quedan las 400 más frecuentes, ordenadas por frecuencia.")
code('{ "escalera": { "4": { "haus": "casa", "hand": "mano", ... }, ... },\n'
     '  "crucigrama": [ { "palabra": "sagen", "pista": "decir" }, ... ] }')
p("Como el resto de datos pesados, <font face='Courier'>juegos.json</font> entra al frontend "
  "por <b>dynamic import</b>: chunk aparte, fuera del bundle inicial.")

h1("4. Escalera de palabras: grafo de Hamming 1 + BFS")
h2("4.1 El modelo")
p("Nodos = palabras del diccionario de longitud L; arista entre dos palabras si difieren en "
  "<b>exactamente una letra</b> (distancia de Hamming 1). Un reto es un par (origen, destino) "
  "y jugar es recorrer un camino: cada paso debe ser una palabra del diccionario vecina de "
  "la anterior. El «par» perfecto lo certifica el <b>camino mínimo</b>, que BFS encuentra en "
  "O(V + E) por ser el grafo no ponderado.")
h2("4.2 Construcción por cubetas comodín")
p("Comparar todas las parejas es O(n²·L). En su lugar, cada palabra se mete en L cubetas, "
  "una por posición enmascarada (hand → *and, h*nd, ha*d, han*): dos palabras son vecinas "
  "<b>si y solo si</b> comparten alguna cubeta. La construcción queda en O(n·L) más el "
  "tamaño real de la salida, y palabras de longitudes distintas nunca colisionan (la máscara "
  "conserva la longitud).")
code("hand → {*and, h*nd, ha*d, han*}\n"
     "land → {*and, l*nd, la*d, lan*}   comparten *and → vecinas")
h2("4.3 Generación de retos")
p("<font face='Courier'>generarReto(palabras, {pasos, semilla})</font> baraja los orígenes "
  "posibles con el LCG (determinista) y, para cada uno, calcula los niveles BFS y busca "
  "destinos a distancia <b>exacta</b> «pasos»: el reto anuncia su dificultad y la garantiza "
  "(no existe atajo más corto, porque la distancia ES el mínimo). La UI ofrece pista "
  "(siguiente palabra de un camino mínimo desde la posición actual, recalculado por BFS), "
  "deshacer y rendirse (muestra el camino del reto). Todo peldaño pisado enseña su glosa.")

h1("5. Crucigrama: colocación por backtracking")
h2("5.1 Reglas de colocación (legalidad)")
p("El tablero es un mapa disperso celda → letra. Colocar una palabra en (fila, col, dir) es "
  "legal si: (1) la casilla anterior al inicio y la posterior al final están libres; (2) "
  "cada casilla de la palabra o está <b>vacía</b> o ya contiene <b>la misma letra</b> (eso "
  "es un cruce); y (3) toda casilla vacía que se rellena no toca lateralmente otra palabra "
  "(sin palabras paralelas pegadas). Además, salvo la primera palabra, toda colocación debe "
  "tener <b>al menos un cruce</b>: el tablero es conexo por construcción.")
h2("5.2 La búsqueda")
p("Se parte de la palabra más larga del pool en horizontal (mejor ancla) y se profundiza: "
  "para cada palabra restante se generan sus colocaciones legales <b>ancladas en un cruce</b> "
  "(solo casillas donde ya está una de sus letras: el espacio de búsqueda se reduce a los "
  "anclajes posibles), ordenadas de más a menos cruces (tableros densos primero). Si una "
  "rama no alcanza el objetivo de n palabras, se <b>deshace</b> la colocación (se borran "
  "solo las casillas que esa palabra añadió, respetando los cruces) y se prueba la "
  "siguiente. Un <b>presupuesto de nodos</b> (5.000) acota el peor caso exponencial; si se "
  "agota, se reintenta con objetivo n−1 — con una palabra nunca falla, así que siempre "
  "devuelve tablero. En la práctica el presupuesto no se toca: la tasa de éxito medida es "
  "100% (véase metricas-seccion4.pdf).")
h2("5.3 Salida")
p("El resultado se traslada a origen (0, 0), se calculan las dimensiones y se numera al "
  "estilo clásico: casillas iniciales en orden de lectura; si una horizontal y una vertical "
  "empiezan en la misma casilla, comparten número. "
  "<font face='Courier'>cuadricula()</font> lo vuelca a una matriz para la UI (null = casilla "
  "negra) y <font face='Courier'>metricas()</font> cuenta casillas, cruces y densidad.")

h1("6. Codenames (Indescifrable): la semilla como servidor")
p("El juego original necesita que dos capitanes vean la MISMA clave secreta sin "
  "comunicarse. Aquí lo resuelve la aritmética: la semilla (p. ej. "
  "<font face='Courier'>DP-K9A2</font>) codifica el vocabulario (DP = alemán principiante) y "
  "alimenta un <b>LCG</b> (a = 1103515245, c = 12345, m = 2³¹) que baraja las palabras y "
  "reparte los colores con Fisher–Yates. Mismo string → mismo tablero y misma clave en "
  "cualquier dispositivo, sin backend. El barajado del resto de juegos reutiliza este LCG "
  "con una corrección (<font face='Courier'>crearGeneradorNormalizado</font>): el generador "
  "original puede emitir valores fuera de [0, 1) con hashes negativos, y la parte "
  "fraccionaria lo normaliza sin alterar los tableros ya repartidos.")

h1("7. Motor puro (JS) y UI")
p("Los tres motores viven en <font face='Courier'>src/engine/</font> sin DOM ni localStorage, "
  "testeados con Vitest (grafo y BFS sobre diccionarios de juguete y sobre el real; "
  "legalidad, determinismo e invariantes del crucigrama: cruces ≥ palabras − 1, sin "
  "conflictos de letra, numeración en orden de lectura). La UI "
  "(<font face='Courier'>src/secciones/juegos/</font>) solo presenta: <b>/juegos</b> es el hub "
  "con los tres juegos; <b>/juegos/escalera</b> ofrece longitud (3–5) y pasos (3–6), input "
  "con validación (¿cambia una letra? ¿existe en el corpus?) y glosa por peldaño; "
  "<b>/juegos/crucigrama</b> renderiza la cuadrícula interactiva (avance de foco en la "
  "dirección activa, click repetido alterna horizontal/vertical, flechas y Backspace), "
  "comprobar y revelar. "
  "El Codenames conserva su pantalla clásica en /juegos/codenames.")

h1("8. Decisiones y trampas")
tabla([
    ["Tema", "Decisión / trampa"],
    ["Solo ASCII en escalera/crucigrama", "Umlauts y ß se excluyen: en teclado español "
     "romperían la fluidez de tecleo. El grafo pierde ~5% de nodos (medido)"],
    ["Distancia EXACTA en el reto", "Buscar destino a distancia exacta k (no ≤ k) hace que "
     "el «mínimo posible» anunciado sea verdad por construcción"],
    ["Palabras funcionales fuera", "Frecuencia alta ≠ buena entrada: «der/und/nicht» no "
     "enseñan nada como pista; lista curada en pipeline/juegos.py"],
    ["Formas vs lemas", "La escalera usa FORMAS (los peldaños solo deben existir); el "
     "crucigrama usa LEMAS (una entrada de crucigrama es una palabra de diccionario)"],
    ["Presupuesto del backtracking", "Garantiza terminación con peor caso exponencial; el "
     "reintento n−1 garantiza salida. Medido: nunca se activa con el pool real"],
    ["Imports con extensión .js", "Los motores se importan también desde node "
     "(simulacion/juegos-stats.mjs): los imports internos llevan extensión explícita"],
], [4.2 * cm, 12.2 * cm])

h1("9. Cómo regenerar cada artefacto")
code("python pipeline/juegos.py               # src/data/juegos.json (tras añadir lecturas)\n"
     "npm test                                # tests de los motores\n"
     "npm run simular-juegos                  # docs/datos-juegos.json (estadísticas reales)\n"
     "python docs/generar_doc_seccion4.py     # este PDF\n"
     "python docs/generar_metricas_seccion4.py\n"
     "python docs/generar_autoaprendizaje_seccion4.py")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Sección 4 — Juegos (documentación técnica)")
doc.build(story)
print(f"-> {SALIDA}")
