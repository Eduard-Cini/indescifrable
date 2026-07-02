# -*- coding: utf-8 -*-
"""Genera docs/documentacion-seccion3.pdf: documentación técnica de la Sección 3
(gramática): pipeline de ejercicios cloze con spaCy, distractores híbridos
paradigma/coseno, filtros de unicidad de respuesta, motor JS puro y UI.

Uso:  PYTHONUTF8=1 python docs/generar_doc_seccion3.py
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
SALIDA = Path(__file__).with_name("documentacion-seccion3.pdf")

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
story.append(Paragraph("Sección 3 — Gramática", STIT))
story.append(Paragraph("Documentación técnica: ejercicios cloze con spaCy, "
                       "distractores híbridos paradigma/coseno y filtros de "
                       "unicidad de respuesta", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. Qué resuelve esta sección")
p("La Sección 3 convierte los textos en alemán de la plataforma en <b>ejercicios de "
  "gramática</b>. La organización es <b>por tema</b>: primero se presenta la regla (lección "
  "con resumen y tabla de referencia) y a partir de ella se practica con ejercicios "
  "<b>cloze</b> de opción múltiple: una frase real del corpus con un hueco y 4 opciones "
  "(la respuesta + 3 distractores). Cuatro temas iniciales: declinación del artículo, "
  "preposición y caso, conjugación del verbo y verbos separables.")
p("Todo el trabajo lingüístico (localizar el hueco, construir y ordenar los distractores) "
  "ocurre <b>offline</b> en el pipeline Python con spaCy; el frontend solo baraja y presenta. "
  "El reto central no es encontrar huecos sino garantizar que el ejercicio tenga "
  "<b>respuesta única</b>: un distractor que también produzca una frase válida no evalúa "
  "nada. Cada tema lleva su propio criterio formal de exclusión (sección 6).")

h1("2. Mapa de archivos")
tabla([
    ["Pieza", "Archivo", "Qué contiene"],
    ["Generador de ejercicios", "pipeline/gramatica.py",
     "spaCy de_core_news_md: detección de huecos por tema, distractores "
     "híbridos, filtros de unicidad, selección estratificada"],
    ["Datos", "src/data/gramatica.json",
     "temas[] (lección: resumen + tabla) y ejercicios{tema: [...]}; "
     "lo sobreescribe el pipeline"],
    ["Motor puro", "src/engine/gramatica.js (+ .test)",
     "Sesión y opciones deterministas por semilla; corrección y resumen"],
    ["UI selector de temas", "src/secciones/gramatica/Gramatica.jsx",
     "Ruta /gramatica: tarjetas de tema con lección y conteo"],
    ["UI sesión de práctica", "src/secciones/gramatica/Ejercicios.jsx",
     "Ruta /gramatica/:tema: regla desplegable, hueco, opciones, feedback"],
    ["Estilos", "src/secciones/gramatica/gramatica.css",
     "Reutiliza el layout de lectura.css y la paleta de repaso.css"],
], [3.3 * cm, 5.9 * cm, 7.2 * cm])

h1("3. Formato de datos")
p("Un ejercicio parte la frase en tres trozos alrededor del hueco, así la UI lo renderiza "
  "sin volver a tokenizar. La pista explica la regla que decide la respuesta y la fuente "
  "identifica la lectura de origen (nivel · título).")
code('{ "id": "declinacion-03",\n'
     '  "antes": "Sie fährt mit ",\n'
     '  "respuesta": "dem",\n'
     '  "despues": " Fahrrad zur Schule.",\n'
     '  "distractores": ["den", "das", "der"],\n'
     '  "pista": "Dativo · neutro · singular.",\n'
     '  "fuente": "principiante · Un día de Ana",\n'
     '  "nivel": "principiante" }')
p("Cada tema lleva además su <b>lección</b>: <font face='Courier'>{ id, titulo, nivel, resumen, "
  "tabla: { cabecera, filas } }</font>. La UI la muestra en la portada del tema y como "
  "desplegable («Ver la regla») durante la práctica. El <font face='Courier'>nivel</font> del tema "
  "clasifica su dificultad (decisión del usuario: declinación, conjugación y separables = "
  "principiante; preposición y caso = intermedio); el del ejercicio es el de su lectura de "
  "origen. La navegación es <b>por lectura</b>: el motor reagrupa el JSON con "
  "<font face='Courier'>agruparPorLectura</font> (lecturas ordenadas por nivel ascendente; dentro de "
  "cada una, los ejercicios agrupados por tema en orden de dificultad del tema).")

h1("4. Detección de huecos (spaCy)")
p("El pipeline recorre las frases en alemán de <b>todas</b> las lecturas (solo frases de "
  "hasta 18 tokens: las de los libros llegan a 40+ y no funcionan como cloze). Cada tema "
  "define qué token se convierte en hueco:")
tabla([
    ["Tema", "Criterio sobre el análisis de spaCy"],
    ["Declinación", "pos=DET con lemma «der» (artículo definido); la pista sale de la "
     "morfología Case/Gender/Number del token"],
    ["Preposición y caso", "pos=ADP presente en el inventario dativo/acusativo, y con "
     "marca de caso visible en su sintagma (ver §6)"],
    ["Conjugación", "pos=VERB/AUX con VerbForm=Fin; la pista sale de Person/Number"],
    ["Separables", "dep=svp (prefijo verbal separado); el lema del verbo se reconstruye "
     "prefijo + lema del head (vor + bereiten → vorbereiten), igual que en la Sección 1"],
], [3.6 * cm, 12.8 * cm])

h1("5. Distractores híbridos: paradigma + coseno")
p("Un método único no basta. La <b>similitud coseno</b> a secas produce distractores flojos "
  "en clases cerradas (los vecinos vectoriales de «der» no son necesariamente artículos); "
  "el <b>paradigma</b> a secas no sabe cuáles de las formas rivales son plausibles en el "
  "contexto. El híbrido asigna a cada método el papel que hace bien:")
p("1. El <b>paradigma morfológico define el conjunto</b> de candidatos: las otras 5 formas "
  "del artículo; las preposiciones del caso opuesto; las demás formas del mismo lema verbal "
  "atestiguadas en el corpus (índice lema → formas invertido del léxico de la Sección 1); "
  "los demás prefijos separables.")
p("2. La <b>similitud coseno ordena el conjunto</b>: con los vectores de spaCy "
  "(de_core_news_md, 20.000 × 300), se puntúa cos(v<sub>respuesta</sub>, v<sub>candidato</sub>) "
  "y se toman los k=3 más parecidos — los <i>hard negatives</i>, los más difíciles de "
  "descartar para el alumno.")
code("cos(u, v) = (u · v) / (||u|| · ||v||)      empate → orden alfabético (determinista)")

h1("6. Filtros de unicidad de respuesta")
p("Ordenar por coseno maximiza la dificultad, pero un distractor «demasiado bueno» puede ser "
  "directamente <b>válido</b>. Cada tema excluye sus alternativas válidas con un criterio "
  "verificable:")
tabla([
    ["Tema", "Criterio de exclusión", "Ejemplo que evita"],
    ["Declinación", "Las demás formas del paradigma violan caso/género/número por "
     "construcción (el sustantivo fija género y número; la sintaxis, el caso)",
     "—"],
    ["Preposición", "Pool = preposiciones del caso OPUESTO; además el hueco solo se genera "
     "si el sintagma lleva marca de caso visible (DET/ADJ/PRON declinado)",
     "«um sieben Uhr»: sin artículo, «nach sieben Uhr» también sería válida"],
    ["Conjugación", "Re-parseo con sustitución: el candidato solo vale si en contexto NO es "
     "forma finita o su persona/número no concuerdan con el sujeto",
     "«ging» → «geht»: otro tiempo, misma concordancia → frase válida → excluido"],
    ["Separables", "La respuesta debe formar un verbo atestiguado en el léxico del corpus "
     "(descarta svp espurios del parser) y los distractores deben NO formarlo",
     "aufmachen vs zumachen: ambos válidos → «zu» no puede ser distractor de «auf»"],
], [2.6 * cm, 7.6 * cm, 6.2 * cm])
p("El filtro de conjugación es el más caro: por cada candidato se re-parsea la frase con la "
  "sustitución hecha y se lee la morfología del token resultante. Para acotarlo, se valida "
  "en orden de coseno descendente y se corta al llegar a k distractores.")

h1("7. Selección estratificada")
p("Los candidatos se acumulan por (tema, fuente) con una cota de 12 por fuente, y la "
  "selección final hace <b>round-robin</b> entre fuentes ordenadas por nivel (principiante → "
  "intermedio → avanzado) hasta el tope de 40 por tema. Sin esto, el tope se llenaba con la "
  "primera lectura en orden alfabético (Immensee) y el resto del corpus no aportaba nada; "
  "con esto, cada tema mezcla los tres niveles y 9–12 fuentes distintas.")

h1("8. Motor puro (JS) y UI")
h2("8.1 src/engine/gramatica.js")
p("Funciones puras testeadas con Vitest: <font face='Courier'>opcionesDe(ejercicio, semilla)</font> "
  "baraja respuesta+distractores de forma determinista (mismo orden entre renders, distinto "
  "entre ejercicios); <font face='Courier'>agruparPorLectura(data)</font> reagrupa los ejercicios por "
  "lectura de origen (orden: nivel ascendente) y, dentro de cada lectura, en subgrupos por "
  "tema en orden de dificultad; <font face='Courier'>claveGrupo</font> / "
  "<font face='Courier'>temaCompletado</font> / <font face='Courier'>lecturaCompletada</font> gobiernan el "
  "progreso (clave estable lectura|tema: sobrevive a regenerar los ids); "
  "<font face='Courier'>esCorrecta</font> y <font face='Courier'>resumenSesion</font> completan la sesión. "
  "El azar entra siempre por el LCG determinista de <font face='Courier'>board.js</font>, con una "
  "corrección: ese generador puede emitir valores fuera de [0,1) (hash de semilla negativo), "
  "así que el motor toma la parte fraccionaria antes de barajar.")
h2("8.2 Flujo de la UI")
p("<b>/gramatica</b> lista las <b>lecturas</b> del corpus con ejercicios (título en alemán), "
  "ordenadas de principiante a avanzado, cada una con su etiqueta de nivel, el conteo y una "
  "palomita ✓ si ya está completada. <b>/gramatica/:lectura</b> es el <b>índice de temas</b> "
  "de esa lectura: el usuario elige qué tema practicar (tarjetas en orden de dificultad, "
  "con palomita por tema terminado). <b>/gramatica/:lectura/:tema</b> corre la tanda de ese "
  "tema: regla desplegable, frase con hueco y 4 opciones; al responder se colorea la "
  "elección y la correcta y se muestra la pista. Al TERMINAR la tanda se persiste la clave "
  "lectura|tema (<font face='Courier'>gramatica.completados.v1</font>); la lectura queda completada "
  "cuando todos sus temas están terminados. <font face='Courier'>gramatica.json</font> se carga por "
  "<b>dynamic import</b>: chunk aparte, fuera del bundle inicial, como el léxico.")

h1("9. Decisiones y trampas")
tabla([
    ["Tema", "Decisión / trampa"],
    ["Respuesta única", "Es el requisito central del diseño; cada tema tiene su filtro "
     "formal (§6). Un cloze con dos respuestas válidas no evalúa nada."],
    ["LCG de board.js", "state/(m−1) con hash negativo produce valores negativos; el motor "
     "de gramática normaliza a [0,1) sin tocar board.js (cambiaría los tableros del juego)"],
    ["svp espurios", "El parser etiqueta svp cosas que no son prefijos separables («gab die "
     "Hand darauf» → *daraufgeben); la atestiguación en el léxico los descarta"],
    ["Separables ≠ gramática pura", "Elegir el prefijo es en parte semántico (la pista da "
     "el verbo); la atestiguación garantiza que los distractores no formen verbo real"],
    ["Regeneración", "gramatica.json lo sobreescribe el pipeline; no editar a mano. El "
     "proceso es determinista: mismo corpus → mismo JSON"],
    ["Python + umlauts", "Siempre PYTHONUTF8=1 y ensure_ascii=False (regla del repo)"],
], [4.2 * cm, 12.2 * cm])

h1("10. Cómo regenerar cada artefacto")
code("python pipeline/gramatica.py            # src/data/gramatica.json (los 4 temas)\n"
     "python pipeline/gramatica.py conjugacion   # un solo tema\n"
     "npm test                                # tests del engine\n"
     "python docs/generar_doc_seccion3.py     # este PDF\n"
     "python docs/generar_metricas_seccion3.py\n"
     "python docs/generar_autoaprendizaje_seccion3.py")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Sección 3 — Gramática (documentación técnica)")
doc.build(story)
print(f"-> {SALIDA}")
