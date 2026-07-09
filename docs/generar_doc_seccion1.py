# -*- coding: utf-8 -*-
"""Genera docs/documentacion-seccion1.pdf: documentación detallada de todo lo
construido (frontend, pipeline PLN, traducción, errores, decisiones), pensada
como base para la memoria de la tesis y para el auto-aprendizaje.

Uso:  python docs/generar_doc_seccion1.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Preformatted, HRFlowable, KeepTogether,
)

SALIDA = Path(__file__).parent / "documentacion-seccion1.pdf"

# --- Paleta ---------------------------------------------------------------
AZUL = colors.HexColor("#1f3a5f")
AZUL2 = colors.HexColor("#2e5e8c")
VERDE = colors.HexColor("#2e6b45")
ROJO = colors.HexColor("#8c2f2f")
GRIS = colors.HexColor("#555555")
GRIS_CLARO = colors.HexColor("#f0f0f0")
GRIS_CODIGO = colors.HexColor("#f5f5f2")
AMBAR = colors.HexColor("#7a5a00")

# --- Estilos --------------------------------------------------------------
ss = getSampleStyleSheet()
S = {}
S["titulo"] = ParagraphStyle("titulo", parent=ss["Title"], fontSize=24,
                             textColor=AZUL, spaceAfter=6, leading=28)
S["subtitulo"] = ParagraphStyle("subtitulo", parent=ss["Normal"], fontSize=12,
                                textColor=GRIS, alignment=TA_CENTER, spaceAfter=4)
S["h1"] = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=16, textColor=AZUL,
                         spaceBefore=16, spaceAfter=6, leading=19)
S["h2"] = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12.5, textColor=AZUL2,
                         spaceBefore=11, spaceAfter=4, leading=15)
S["h3"] = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=11, textColor=colors.black,
                         spaceBefore=8, spaceAfter=3, leading=13)
S["body"] = ParagraphStyle("body", parent=ss["Normal"], fontSize=9.7, leading=13.6,
                           alignment=TA_JUSTIFY, spaceAfter=5)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], leftIndent=12,
                             bulletIndent=2, spaceAfter=2)
S["code"] = ParagraphStyle("code", parent=ss["Code"], fontSize=8.2, leading=10.5,
                           textColor=colors.HexColor("#1a1a1a"))
S["small"] = ParagraphStyle("small", parent=S["body"], fontSize=8.3, textColor=GRIS,
                            alignment=TA_LEFT)
S["cell"] = ParagraphStyle("cell", parent=ss["Normal"], fontSize=8.3, leading=11)
S["cellh"] = ParagraphStyle("cellh", parent=S["cell"], textColor=colors.white,
                            fontName="Helvetica-Bold")
S["toc"] = ParagraphStyle("toc", parent=S["body"], spaceAfter=2, alignment=TA_LEFT)


def _san(t):
    # Evita glifos ausentes en las fuentes base (Helvetica/Courier -> WinAnsi).
    reemplazos = {"→": "-&gt;", "⇄": "&lt;-&gt;", "✓": "[OK]", "✗": "[X]",
                  "≈": "~", "×": "x", "≥": "&gt;=", "•": "-"}
    for a, b in reemplazos.items():
        t = t.replace(a, b)
    return t


story = []


def h1(t):
    story.append(Paragraph(t, S["h1"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL, spaceAfter=4))


def h2(t):
    story.append(Paragraph(t, S["h2"]))


def h3(t):
    story.append(Paragraph(t, S["h3"]))


def p(t):
    story.append(Paragraph(_san(t), S["body"]))


def li(items):
    for it in items:
        story.append(Paragraph("• " + _san(it), S["bullet"]))
    story.append(Spacer(1, 3))


def code(t):
    tbl = Table([[Preformatted(t, S["code"])]], colWidths=[16.4 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIS_CODIGO),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5))


def tabla(filas, anchos, encabezado=True):
    data = [[Paragraph(_san(c), S["cellh"] if (encabezado and i == 0) else S["cell"])
             for c in fila] for i, fila in enumerate(filas)]
    tbl = Table(data, colWidths=anchos, repeatRows=1 if encabezado else 0)
    estilo = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
    ]
    if encabezado:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), AZUL2))
    tbl.setStyle(TableStyle(estilo))
    story.append(tbl)
    story.append(Spacer(1, 7))


def callout(tipo, titulo, cuerpo):
    color = {"error": ROJO, "insight": VERDE, "nota": AMBAR}[tipo]
    etiqueta = {"error": "ERROR / SOLUCIÓN", "insight": "INSIGHT", "nota": "NOTA"}[tipo]
    contenido = [Paragraph(f'<b>{etiqueta} — {_san(titulo)}</b>',
                           ParagraphStyle("cot", parent=S["body"], textColor=color,
                                          spaceAfter=3, fontSize=9.3))]
    for par in cuerpo:
        contenido.append(Paragraph(_san(par), ParagraphStyle(
            "cob", parent=S["body"], fontSize=9, spaceAfter=3)))
    tbl = Table([[contenido]], colWidths=[16.4 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbfbf9")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, color),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e2e2")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether(tbl))
    story.append(Spacer(1, 7))


# =========================================================================
#  PORTADA
# =========================================================================
story.append(Spacer(1, 3.5 * cm))
story.append(Paragraph("Sección 1 — Lectura", ParagraphStyle(
    "secmarker", parent=S["subtitulo"], textColor=AZUL2,
    fontName="Helvetica-Bold", fontSize=13, spaceAfter=6)))
story.append(Paragraph("Plataforma web para el aprendizaje de idiomas", S["titulo"]))
story.append(Paragraph("Documentación técnica: sistema de lectura y pipeline de PLN",
                       S["subtitulo"]))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("Español · Inglés · Alemán &nbsp;|&nbsp; React + Vite · Python · spaCy (de/en/es) · FreeDict · opus-mt / Gemini · wordfreq",
                       S["subtitulo"]))
story.append(Spacer(1, 1.2 * cm))
story.append(HRFlowable(width="60%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph(
    "Documento de referencia para la memoria de tesis y el auto-aprendizaje. "
    "Recoge las librerías y modelos empleados, la arquitectura, los pipelines, "
    "los errores encontrados y su solución, y las ventajas y desventajas de cada "
    "decisión de implementación.",
    ParagraphStyle("intro", parent=S["body"], alignment=TA_CENTER, fontSize=10,
                   textColor=GRIS)))
story.append(PageBreak())

# =========================================================================
#  ÍNDICE
# =========================================================================
h1("Índice")
indice = [
    "1. Introducción y objetivos",
    "2. Arquitectura general",
    "3. Frontend (React + Vite)",
    "4. Pipeline de PLN offline (Python)",
    "5. Traducción por oración de libros (LLM vs MT)",
    "6. Errores encontrados y soluciones",
    "7. Ventajas y desventajas de cada implementación",
    "8. Librerías, modelos y recursos",
    "9. Insights y metodología",
    "10. Estado actual y trabajo futuro",
    "11. Glosario técnico",
]
for it in indice:
    story.append(Paragraph(it, S["toc"]))
story.append(PageBreak())

# =========================================================================
#  1. INTRODUCCIÓN
# =========================================================================
h1("1. Introducción y objetivos")
p("El proyecto es una plataforma web para aprender español, inglés y alemán, concebida "
  "como trabajo de tesis en <b>matemática algorítmica</b>. La aportación central de la "
  "tesis no es la herramienta en sí, sino el <b>modelado matemático y algorítmico</b> que la "
  "sustenta (procesos estocásticos, modelos de frecuencia léxica, reglas morfológicas, "
  "álgebra lineal, teoría de grafos y de números); el sitio es el medio donde esas "
  "herramientas viven y se demuestran en funcionamiento.")
p("La plataforma se organiza en cuatro vertientes: (1) <b>lectura</b>, "
  "(2) <b>repaso de vocabulario</b> con repetición espaciada (SM-2 en producción, Leitner "
  "como cadena de Markov por simulación), (3) <b>gramática</b> generada con PLN sobre los "
  "propios textos, y (4) <b>juegos</b> de palabras. Este documento cubre la <b>vertiente de "
  "lectura</b> y su <b>pipeline de PLN</b> en los tres idiomas de estudio: alemán e inglés "
  "(traducidos al español) y <b>español como lengua de estudio para nativos</b> (libros "
  "difíciles con glosado de voces raras).")
h2("Alcance de lo construido")
li([
    "Sección de <b>Lectura</b> completa: biblioteca por idioma/nivel, lector con traducción "
    "por palabra y por frase, bolsa de palabras persistente y seguimiento de progreso.",
    "<b>Tres idiomas de estudio</b>: alemán e inglés (con traducción al español) y "
    "<b>español como lengua de estudio para nativos</b>, con libros difíciles glosados "
    "(definiciones de voces raras, no traducción).",
    "<b>Pipeline de PLN offline</b> en Python que ingiere libros de dominio público, los "
    "procesa con spaCy (modelo por idioma) y genera el JSON que consume el frontend "
    "(traducción por palabra, por frase, y glosado monolingüe del español).",
    "<b>Idioma de estudio global</b> (contexto React persistido) que gobierna todas las "
    "secciones; bolsa filtrada por idioma; <b>perfil exportable/importable</b> como JSON "
    "sin servidor.",
    "<b>Motor de lógica pura</b> con pruebas unitarias (Vitest), germen del núcleo matemático.",
    "Mejoras al <b>juego Codenames</b>: extracción del generador congruencial a un módulo puro, "
    "semilla que codifica idioma y nivel, y optimización de recursos.",
])

# =========================================================================
#  2. ARQUITECTURA
# =========================================================================
h1("2. Arquitectura general")
p("El sistema se estructura en tres piezas claramente separadas, siguiendo el diseño de la "
  "tesis: un pipeline offline que hace el trabajo pesado, un motor algorítmico puro, y un "
  "frontend que solo presenta e interactúa.")
tabla([
    ["Pieza", "Tecnología", "Responsabilidad"],
    ["Pipeline offline", "Python (spaCy, FreeDict, transformers)",
     "Ingiere textos de dominio público, calcula segmentación, lematización y traducción; "
     "exporta JSON. Se ejecuta una sola vez, fuera de línea."],
    ["Motor algorítmico", "JavaScript puro (+ Vitest)",
     "Lógica sin efectos secundarios: bolsa de palabras, generación determinista del tablero, "
     "progreso. Testeable en aislamiento."],
    ["Frontend", "React 19 + Vite 8 + react-router 7",
     "Consume el JSON precalculado y gestiona presentación e interacción. No ejecuta "
     "procesamiento pesado en vivo."],
], [3.2 * cm, 4.6 * cm, 8.6 * cm])
callout("insight", "Principio de diseño: “sin APIs en vivo”",
        ["La aplicación en ejecución es <b>determinista y sin red</b>: todo el estado vive en "
         "<font face='Courier'>localStorage</font> y todos los datos (textos, traducciones, "
         "léxico) son JSON estático precalculado. El coste computacional (PLN, traducción) se "
         "paga una vez en el pipeline, no en cada visita.",
         "Matiz importante: usar un LLM (Gemini) o un modelo de MT para traducir un libro es "
         "un <b>paso offline de una sola vez</b> que produce JSON estático; no rompe ese "
         "principio, porque la app nunca llama a una API en tiempo de ejecución."])
p("<b>Flujo de datos:</b> textos de dominio público (Project Gutenberg) -> pipeline Python "
  "(spaCy + diccionarios) -> archivos JSON en <font face='Courier'>src/data/</font> -> "
  "frontend React que los carga y renderiza. El estado del usuario (bolsa, progreso) se "
  "guarda en el navegador.")

# =========================================================================
#  3. FRONTEND
# =========================================================================
h1("3. Frontend (React + Vite)")
h2("3.1 Stack y versiones")
tabla([
    ["Librería", "Versión", "Para qué"],
    ["React", "19.2", "UI declarativa por componentes."],
    ["Vite", "8.0", "Bundler y servidor de desarrollo (HMR). Rollup/Oxc por debajo."],
    ["react-router-dom", "7.18", "Enrutado por secciones y URLs profundas."],
    ["Vitest", "4.1", "Pruebas unitarias del motor puro."],
    ["ESLint", "9", "Análisis estático."],
], [4.2 * cm, 2.2 * cm, 10 * cm])

h2("3.2 Enrutado y secciones")
p("<font face='Courier'>App.jsx</font> pasó de ser el router del juego a un router de "
  "<b>plataforma</b> con <font face='Courier'>BrowserRouter</font>. Rutas: "
  "<font face='Courier'>/</font> (menú), <font face='Courier'>/juegos/*</font> (Codenames), "
  "<font face='Courier'>/lectura</font> (biblioteca), "
  "<font face='Courier'>/lectura/:idioma/:nivel/:id</font> (lector) y "
  "<font face='Courier'>/bolsa</font>. Para que las URLs profundas no den 404 en Netlify se "
  "añadió <font face='Courier'>public/_redirects</font> con "
  "<font face='Courier'>/* /index.html 200</font> (fallback SPA).")

h2("3.3 Modelo de datos")
p("Cada <b>lectura</b> es un JSON con metadatos y el cuerpo alineado por frase entre idiomas. "
  "Las lecturas ya no tienen que ser trilingües: pueden ser de+es, en+es, o <b>solo es</b> "
  "(libros de estudio para nativos). La regla de <font face='Courier'>idiomasDisponibles</font> "
  "es: de/en son idiomas de estudio si tienen cuerpo; el español lo es <b>solo cuando es el "
  "original</b> (no hay de/en) — en las demás lecturas actúa como idioma de traducción. Los "
  "libros añaden campos <font face='Courier'>libro/parte/partes</font> para agruparse.")
code('''{
  "id": "mercado-01", "nivel": "principiante", "autor": "...",
  "titulo": { "es": "El mercado", "en": "The market", "de": "Der Markt" },
  "fuente": "…procedencia y URL de dominio público…",
  "cuerpo": {
    "de": ["Sie kauft Äpfel, Brot und Käse.", …],   // frase i
    "es": ["Compra manzanas, pan y queso.",   …]    // frase i (alineada)
  }
}''')
p("El <b>léxico</b> (traducción por palabra) es un mapa "
  "<font face='Courier'>idioma:forma -&gt; { lemma, es }</font>. Se busca por la forma "
  "superficial normalizada (minúsculas, sin puntuación), conservando acentos y umlauts. "
  "En las entradas <font face='Courier'>es:</font> el campo <font face='Courier'>es</font> "
  "no es una traducción sino una <b>definición en español moderno</b> de una voz rara.")
code('''{ "de:frau":   { "lemma": "Frau",   "es": "mujer" },
  "en:mice":   { "lemma": "mouse",  "es": "ratón" },
  "es:adarga": { "lemma": "adarga", "es": "escudo de cuero, ovalado…" } }''')
p("La <b>bolsa de palabras</b> es única y persistente; cada entrada guarda "
  "<font face='Courier'>id, lang, surface, lemma, traducciones, origen, addedAt</font>. "
  "Está diseñada para que el motor de repaso (Sección 2 de la tesis) le agregue después su "
  "estado (caja de Leitner, factor SM-2).")

h2("3.4 Motor de lógica pura + persistencia")
p("Se separó el <b>núcleo puro</b> (sin DOM, React ni localStorage) de la persistencia. Esto "
  "es lo que la tesis valora como “motor testeable” y de paso elimina duplicación de código.")
li([
    "<font face='Courier'>engine/board.js</font>: generador congruencial lineal (LCG), "
    "Fisher-Yates, composición/parseo de semilla y generación determinista del tablero.",
    "<font face='Courier'>engine/bolsa.js</font>: alta/baja en la bolsa. Regla de la tesis: "
    "<b>una palabra ya presente conserva su estado</b> (no se reinicia el progreso).",
    "<font face='Courier'>engine/progreso.js</font>: lecturas completadas.",
    "<font face='Courier'>engine/almacenamiento.js</font>: adaptador delgado (impuro) sobre "
    "<font face='Courier'>localStorage</font>.",
])
p("Pruebas con <b>Vitest</b> (17 casos): determinismo del tablero (misma semilla -> mismo "
  "resultado, distribución 9/8/7/1), la regla de no-reinicio de la bolsa, normalización, etc.")
callout("insight", "El LCG como puente con la teoría de números",
        ["El juego sincroniza los tableros de ambos equipos con un <b>generador congruencial "
         "lineal</b> sembrado por un hash de la semilla. La semilla se rediseñó a formato "
         "<font face='Courier'>XX-YYYY</font>, donde <font face='Courier'>XX</font> codifica "
         "idioma y nivel del vocabulario; así el capitán solo introduce la semilla y el "
         "sistema deduce el diccionario. Esto conecta con aritmética modular y teoría de "
         "números, tal como plantea la tesis."])

h2("3.5 Experiencia de lectura")
li([
    "<b>Tokenización</b> por expresión regular Unicode (<font face='Courier'>\\p{L}…</font>) "
    "que separa palabras clicables de la puntuación, conservando el texto original.",
    "<b>Traducción por palabra:</b> al tocar una palabra se busca en el léxico y se muestra "
    "un popup con la traducción al español y un botón para añadirla a la bolsa.",
    "<b>Traducción por frase:</b> un marcador discreto en el margen de cada frase revela su "
    "traducción alineada. Se eligió un objetivo <b>táctil</b> (no hover) para que funcione en "
    "móvil; el hover es solo una mejora en escritorio.",
    "<b>Libros:</b> las partes de un libro colapsan en una sola tarjeta con progreso "
    "“N/10 partes”; el lector ofrece navegación anterior/siguiente y “finalizar y continuar”.",
    "<b>Bolsa y progreso</b> persistentes en localStorage; la biblioteca conserva idioma y "
    "nivel en la URL para no reiniciarse al volver de una lectura.",
])

h2("3.6 Carga de datos y peso del bundle")
p("El catálogo carga todas las lecturas automáticamente con "
  "<font face='Courier'>import.meta.glob</font>, de modo que añadir lecturas (a mano o desde "
  "el pipeline) no requiere tocar código. El <b>léxico</b> (465 KB, 5.779 entradas) se "
  "importaba de forma estática e inflaba el bundle inicial; se pasó a <b>carga bajo demanda</b> "
  "con <font face='Courier'>dynamic import</font>, que Vite emite como chunk aparte cacheado, "
  "descargado solo al abrir una lectura. Bundle inicial: <b>1018 KB -&gt; 694 KB</b> "
  "(gzip 328 -&gt; 253 KB).")

h2("3.7 Idioma de estudio global, bolsa por idioma y perfil")
p("Al crecer a tres idiomas de estudio hizo falta una noción transversal de <b>idioma de "
  "estudio actual</b>. Es un contexto React "
  "(<font face='Courier'>contexto/idiomaEstudio.jsx</font>) persistido en "
  "<font face='Courier'>idiomaEstudio.v1</font>, con un selector compartido presente en el "
  "hub, el Repaso y la Bolsa; las demás secciones (Juegos, Gramática) leen el mismo contexto "
  "para elegir su bloque de datos.")
li([
    "<b>La bolsa no se parte por idioma:</b> sigue siendo un único almacén "
    "<font face='Courier'>bolsa.v1</font> (cada entrada ya lleva "
    "<font face='Courier'>lang</font> y su id es <font face='Courier'>lang:forma</font>); se "
    "<b>filtra al consumir</b>. Detalle importante: el Repaso conserva la bolsa completa en "
    "memoria y solo arma la sesión con el idioma activo — si persistiera la lista filtrada, "
    "borraría el resto de idiomas.",
    "<b>Perfil exportable/importable:</b> todo el estado del usuario vive en unas pocas "
    "claves de localStorage detrás de <font face='Courier'>almacenamiento.js</font> (única "
    "frontera de I/O). <font face='Courier'>exportarPerfil()</font> las serializa a un JSON "
    "descargable y <font face='Courier'>importarPerfil()</font> las restaura validando la "
    "envoltura y cada valor; da copia de seguridad y portabilidad <b>sin servidor</b>.",
    "<b>Popup de palabra:</b> se rediseñó en columna (palabra, traducción/definición a todo "
    "el ancho, botón debajo) para que las definiciones largas del glosado español se lean "
    "bien y el botón nunca desborde.",
])

# =========================================================================
#  4. PIPELINE
# =========================================================================
h1("4. Pipeline de PLN offline (Python)")
p("El pipeline vive en <font face='Courier'>pipeline/</font> y convierte libros de texto plano "
  "en las lecturas JSON que consume el frontend. Está separado en dos pasos: "
  "<b>ingesta</b> de un libro (<font face='Courier'>procesar.py</font>) y "
  "<b>construcción del léxico</b> sobre todas las lecturas "
  "(<font face='Courier'>construir_lexico.py</font>).")

h2("4.1 spaCy: segmentación, tokenización, lematización")
p("Se usa <b>spaCy</b> con un modelo por idioma: <font face='Courier'>de_core_news_md</font> "
  "(alemán), <font face='Courier'>en_core_web_sm</font> (inglés) y "
  "<font face='Courier'>es_core_news_md</font> (español). spaCy segmenta el texto en frases, "
  "tokeniza y asigna a cada token su lema, categoría gramatical (POS), rasgos morfológicos y "
  "relaciones de dependencia. El pipeline aprovecha las <b>frases</b> (para alinear "
  "traducciones) y los <b>lemas</b> (para buscar en el diccionario). "
  "<font face='Courier'>procesar.py</font> elige el modelo según el "
  "<font face='Courier'>idioma</font> declarado por cada libro en "
  "<font face='Courier'>LIBROS</font>, admite ingerir un <b>fragmento</b> acotado "
  "(<font face='Courier'>max_chars</font>, para obras enormes como el Quijote) y un marcador "
  "<font face='Courier'>fin</font> (para recortar índices al final, como en <i>Azul…</i>).")
callout("insight", "Verbos separables del alemán vía la dependencia svp",
        ["El alemán parte muchos verbos: “…bereitet … vor” es el verbo <b>vorbereiten</b> "
         "(preparar). spaCy etiqueta el prefijo con la dependencia "
         "<font face='Courier'>svp</font> (separable verb prefix) apuntando al verbo. El "
         "pipeline lo detecta y <b>reconstruye</b> el lema real: "
         "<font face='Courier'>vor + bereiten = vorbereiten</font>, y hace que tocar "
         "cualquiera de las dos partes remita a la misma entrada. Esto resuelve "
         "automáticamente un caso que al principio hubo que corregir a mano.",
         "Es un buen ejemplo de la tesis: usar el <b>análisis de dependencias</b> para "
         "resolver una ambigüedad morfológica de forma algorítmica."])

h2("4.2 Traducción por palabra: diccionarios FreeDict por capas")
p("La traducción por palabra es <b>determinista y offline</b>. Se usan diccionarios libres de "
  "<b>FreeDict</b> (formato TEI/XML) y una estrategia por capas en "
  "<font face='Courier'>traductor.py</font> (para el alemán; el inglés va directo por "
  "eng-spa, sin capas):")
tabla([
    ["Capa", "Método", "Marca"],
    ["1. Directo", "deu-spa (36.744 entradas), por lema y por forma", "—"],
    ["2. Cadena", "deu-eng (~380 mil) -> eng-spa (~59 mil) cuando deu-spa falla",
     "(vía inglés)"],
    ["3. Compuesto", "cabeza del compuesto alemán (sufijo de &gt;= 3 letras)",
     "(en compuesto)"],
], [3.0 * cm, 10.6 * cm, 2.8 * cm])
p("El diccionario deu-spa por sí solo cubría ~70% del vocabulario de un libro; le faltan "
  "muchas palabras comunes (unruhig, hilflos, bogenförmig…). La <b>cadena por inglés</b> "
  "(FreeDict deu-eng es enorme) cierra la mayor parte del hueco, aunque a costa de dos saltos "
  "y algo de ruido; por eso se marca “(vía inglés)”. La <b>descomposición de compuestos</b> "
  "(la cabeza de un compuesto alemán es el último elemento: Holztür -&gt; Tür -&gt; puerta) "
  "recupera compuestos ausentes.")

h2("4.3 Cobertura de traducción y su evolución")
p("La <b>cobertura</b> es el porcentaje de formas de palabra distintas que reciben traducción. "
  "Se midió con un diagnóstico que clasifica los fallos por categoría gramatical "
  "(<font face='Courier'>diagnostico.py</font>). Evolución sobre <i>Die Verwandlung</i>:")
tabla([
    ["Cambio", "Cobertura"],
    ["FreeDict deu-spa + modelo pequeño (sm)", "70%"],
    ["Modelo mediano (md): mejor lematización (abhielt -> abhalten)", "81%"],
    ["Cadena deu-eng -> eng-spa", "90%"],
    ["Descomposición de compuestos con cabezas de 3 letras", "92%"],
], [12 * cm, 4.4 * cm])
p("El ~8% restante son sobre todo <b>verbos fuertes</b> que spaCy no lematiza bien (hing, "
  "dasaß) y compuestos raros. Para <b>principiante e intermedio</b> se alcanzó el <b>100%</b>: "
  "el léxico se reconstruye desde una <b>semilla curada a mano</b> "
  "(<font face='Courier'>lexico.base.json</font>) que además de las entradas del pipeline "
  "incluye 49 casos rellenados manualmente (nombres propios marcados como tal, imperativos "
  "como Komm/gib, y verbos fuertes como schlief/aß).")
callout("nota", "Fusión idempotente del léxico",
        ["<font face='Courier'>construir_lexico.py</font> reconstruye el léxico completo desde "
         "la semilla curada más el vocabulario de todas las lecturas, de modo que re-ejecutar "
         "el pipeline es <b>idempotente</b> y no arrastra entradas obsoletas. Al fusionar, "
         "<b>nunca sobrescribe</b> una entrada ya traducida con una sin traducción (una misma "
         "forma puede recibir distinto lema según el contexto)."])

h2("4.4 Ambigüedad y overrides por lectura")
p("Un léxico global (clave <font face='Courier'>idioma:forma</font>) no puede desambiguar "
  "formas que dependen del contexto: <i>nahm</i> es parte de <b>annehmen</b> (suponer) en una "
  "fábula, pero es <b>nehmen</b> (tomar) en otra novela; <i>an</i> es partícula separable o "
  "preposición según la frase. Es el <b>sub-problema de ambigüedad</b> que la tesis plantea "
  "explícitamente (una misma forma admite varios análisis).")
p("Solución adoptada: cada lectura puede llevar un pequeño mapa "
  "<font face='Courier'>lexico</font> con overrides que el frontend <b>prioriza</b> sobre el "
  "léxico global. Para los textos curados de principiante/intermedio se detectaron los verbos "
  "separables (dependencia <font face='Courier'>svp</font>) inequívocos dentro de cada texto y "
  "se fijó a mano el lema y la traducción correctos, verificados frase a frase.")
callout("insight", "Por qué un léxico global no basta",
        ["El límite es de fondo: la traducción por palabra correcta depende de la <b>posición "
         "del token</b>, no solo de su forma. Los overrides por lectura resuelven los casos "
         "curados; la solución general sería anotar el léxico <b>por token</b> en el pipeline "
         "(algo que spaCy ya permite) y renderizar con esos tokens en vez de tokenizar en el "
         "cliente. Es un refactor mayor, anotado como trabajo futuro."])

h2("4.5 Glosado monolingüe del español (lengua de estudio para nativos)")
p("El español dejó de ser solo la lengua-puente: hay libros difíciles (Quijote y Buscón en "
  "fragmento; <i>Azul…</i> de Darío y los <i>Cuentos</i> de Quiroga completos) pensados para "
  "que un <b>nativo</b> amplíe vocabulario. Aquí “traducir” no tiene sentido: se <b>glosa</b> "
  "— una definición breve en español moderno — y <b>solo las voces poco comunes</b>: "
  "arcaísmos del Siglo de Oro (adarga, rocín, fazaña), léxico modernista (ánfora, cendal) y "
  "regionalismos rioplatenses (mensú, tacuara, jangada).")
li([
    "<b>Detección de rareza:</b> offline, con la frecuencia general del español (escala "
    "Zipf de la biblioteca <font face='Courier'>wordfreq</font>): se extraen los lemas con "
    "Zipf bajo y ocurrencias suficientes, que forman la lista de trabajo a curar.",
    "<b>Definiciones curadas a mano</b> en <font face='Courier'>pipeline/glosas_es.json</font> "
    "(~190 voces). Los MT no sirven aquí (no hay lengua destino); el diccionario monolingüe "
    "curado es la única vía con calidad garantizada.",
    "<b>Casado robusto:</b> <font face='Courier'>construir_lexico.py</font> genera entradas "
    "<font face='Courier'>es:forma</font> casando por forma superficial <b>o</b> por lema, "
    "porque el lematizador español tropieza con arcaísmos y enclíticas "
    "(celada -&gt; “celado”, trujeron, preguntóle).",
    "<b>Solo libros de estudio:</b> la rama es del léxico se aplica únicamente a lecturas "
    "cuyo cuerpo es solo español (en las trilingües, es es la traducción, no texto a glosar).",
])
callout("insight", "El modelo de conocimiento hace el resto",
        ["No hace falta lógica nueva para que el sistema priorice las voces raras: el modelo "
         "de conocimiento de la Sección 2 ya estima P(conocer) con un prior logístico sobre "
         "la frecuencia Zipf del corpus. Para un nativo, las palabras corrientes salen con "
         "probabilidad altísima y las raras bajan — el repaso previo del Lector destaca "
         "exactamente las glosadas. La misma matemática sirve para los tres idiomas."])

# =========================================================================
#  5. TRADUCCIÓN POR ORACIÓN
# =========================================================================
h1("5. Traducción por oración de libros (LLM vs MT)")
p("Los libros de alemán e inglés solo traen el texto original; darles traducción <b>por "
  "frase</b> exige una versión española <b>alineada 1:1</b> con las frases originales (la "
  "frase <font face='Courier'>es[i]</font> corresponde a la <font face='Courier'>i</font>-ésima "
  "del original). Esa alineación es la restricción que manda en todas las opciones. Se "
  "implementaron dos vías. Los libros en español no llevan traducción por frase: son "
  "monolingües y el Lector oculta el marcador.")

h2("5.1 Vía LLM (Gemini) — máxima calidad, semi-manual")
p("Flujo con validación de alineación: <font face='Courier'>exportar_frases.py</font> vuelca "
  "las frases numeradas + un prompt estricto (“una línea por oración, no unir ni dividir”); "
  "se pega en Gemini; <font face='Courier'>importar_traduccion.py</font> parsea la respuesta y "
  "<b>valida 1:1</b> (si el conteo o la numeración no cuadran, no escribe nada). Así se tradujo "
  "<i>Die Verwandlung</i> de Kafka (10 partes, 864 oraciones, todas validadas).")

h2("5.2 Vía MT offline (opus-mt) — automática, sin API")
p("Alternativa totalmente automática con <b>opus-mt</b> (Helsinki-NLP, modelos Marian) vía "
  "<font face='Courier'>transformers</font>, traducción directa <b>sin pivote</b>. "
  "<font face='Courier'>mt.py</font> está parametrizado por idioma de origen "
  "(<font face='Courier'>opus-mt-de-es</font> y <font face='Courier'>opus-mt-en-es</font>) y "
  "<font face='Courier'>traducir_mt.py</font> deduce el origen del cuerpo de cada lectura. La "
  "alineación 1:1 es automática (una salida por frase). Antes se descartó <b>Argos "
  "Translate</b>, que no tiene de-&gt;es directo y <b>pivota por inglés</b>, con errores "
  "graves. Con MT se tradujeron <i>Immensee</i> (de-&gt;es) y los <b>cuatro libros "
  "ingleses</b> — <i>The Time Machine</i> (Wells), <i>A Christmas Carol</i> (Dickens), "
  "<i>The Fall of the House of Usher</i> (Poe) y <i>Death in Venice</i> (Mann, trad. Kenneth "
  "Burke 1925) — 58 partes en-&gt;es sin copia-pega. El par en-&gt;es es de los mejor "
  "entrenados de Helsinki-NLP, con calidad notablemente superior al de-&gt;es.")

h2("5.3 Comparación de calidad")
tabla([
    ["Frase alemana", "Gemini", "opus-mt (directo)", "Argos (pivote)"],
    ["…einem ungeheueren Ungeziefer verwandelt",
     "convertido en un monstruoso <b>insecto</b>",
     "convirtiéndose en una <b>bestia</b> monstruosa",
     "monstruoso <b>vértigo</b> (mal)"],
    ["bestäubt (polvoriento)", "cubiertos de polvo", "<b>polinizados</b> (mal)", "—"],
    ["wohlgekleideter Mann", "hombre bien vestido", "<b>vestido y vestido</b> (mal)", "—"],
], [4.6 * cm, 4.0 * cm, 4.0 * cm, 3.8 * cm])
p("<b>Conclusión práctica:</b> la MT offline <b>automatiza todo</b> el flujo pero comete "
  "errores semánticos que un LLM no comete. Para libros donde importe la calidad, conviene el "
  "LLM; para volumen o cuando la calidad “suficiente” basta, la MT. Ambas producen JSON "
  "estático, así que la app sigue siendo offline.")

# =========================================================================
#  6. ERRORES
# =========================================================================
h1("6. Errores encontrados y soluciones")
p("Esta sección recoge los tropiezos del proceso; es la parte más útil para aprender, porque "
  "muchos son problemas de entorno o de comprensión de las librerías, no de la lógica.")

callout("error", "Certificados SSL en git (y luego en Python)",
        ["<b>Síntoma:</b> <font face='Courier'>git push</font> y las descargas de Python "
         "fallaban con “unable to get local issuer certificate”.",
         "<b>Causa:</b> el entorno intercepta TLS y el almacén de certificados de OpenSSL/git "
         "no tenía el certificado raíz.",
         "<b>Solución:</b> en git, <font face='Courier'>http.sslBackend=schannel</font> (usa el "
         "almacén de Windows, que se mantiene actualizado solo). En Python, instalar "
         "<font face='Courier'>pip-system-certs</font>, que hace que <font face='Courier'>"
         "requests</font> use también el almacén de Windows (necesario para descargar los "
         "modelos de spaCy, los diccionarios y los modelos de traducción)."])

callout("error", "Reglas de los Hooks de React",
        ["<b>Síntoma:</b> riesgo de romper el orden de los hooks en "
         "<font face='Courier'>TableroClave</font>, que tenía un <font face='Courier'>return</font> "
         "de error antes de los <font face='Courier'>useState</font>.",
         "<b>Solución:</b> mover <b>todos</b> los hooks al principio del componente y dejar los "
         "<font face='Courier'>return</font> condicionales después. Los hooks deben ejecutarse "
         "siempre en el mismo orden en cada render."])

callout("error", "useEffect disparado por un “gatillo falso”",
        ["<b>Síntoma:</b> para re-generar el tablero al cambiar de ronda se incrementaba un "
         "estado <font face='Courier'>numeroRonda</font> solo para forzar el "
         "<font face='Courier'>useEffect</font>.",
         "<b>Solución:</b> extraer una función <font face='Courier'>iniciarPartida()</font> "
         "llamada explícitamente (en el montaje y al pasar de ronda). Intención explícita en "
         "vez de estado artificial."])

callout("error", "spaCy sobre-segmentaba las frases",
        ["<b>Síntoma:</b> <i>Die Verwandlung</i> daba 2.666 “frases” (Kafka usa frases largas; "
         "eran fragmentos).",
         "<b>Causa:</b> el texto de Gutenberg viene con <b>líneas envueltas</b> (un salto de "
         "línea cada ~70 caracteres); spaCy segmentaba por esos saltos.",
         "<b>Solución:</b> unir todas las líneas en un flujo continuo antes de segmentar "
         "(quitando además los marcadores de capítulo). Resultado: 864 frases reales."])

callout("error", "Compuestos y verbos fuertes sin traducción",
        ["<b>Síntoma:</b> ~19% de palabras sin traducción; muchos compuestos (Musterkollektion) "
         "y formas verbales (hing, dasaß).",
         "<b>Solución:</b> cadena de-&gt;en-&gt;es con el enorme diccionario deu-eng, "
         "descomposición de la cabeza del compuesto, y modelo spaCy mediano para mejores "
         "lemas. Cobertura 70% -&gt; 92%. Los verbos fuertes restantes exigirían un analizador "
         "morfológico más potente (rendimientos decrecientes)."])

callout("error", "MT por pivote confundía el sentido",
        ["<b>Síntoma:</b> Argos traducía “Ungeziefer” (insecto) como “vértigo”.",
         "<b>Causa:</b> Argos no tiene de-&gt;es directo; pivota por inglés y el doble salto "
         "acumula errores de sentido.",
         "<b>Solución:</b> usar opus-mt directo de-&gt;es (Helsinki-NLP), que no pivota y da "
         "traducciones sin ese tipo de error grave."])

callout("error", "El lematizador español tropieza con arcaísmos y enclíticas",
        ["<b>Síntoma:</b> al glosar los libros del Siglo de Oro, spaCy producía lemas "
         "inexistentes: <i>celada</i> -&gt; “celado”, <i>azotes</i> -&gt; “azot”, y formas con "
         "pronombre enclítico (<i>preguntóle</i>, <i>trujeron</i>) quedaban sin analizar.",
         "<b>Causa:</b> <font face='Courier'>es_core_news_md</font> está entrenado con español "
         "contemporáneo; el español áureo queda fuera de distribución.",
         "<b>Solución:</b> el glosario casa por <b>forma superficial además de por lema</b>: "
         "una entrada como “trujeron” se define por su forma exacta y no depende del "
         "lematizador. Las voces del glosario se detectan con la frecuencia Zipf del español "
         "general (wordfreq), no con el análisis morfológico."])

callout("error", "Codificación de consola y shell en Windows",
        ["<b>Síntoma:</b> los umlauts salían como cajas o daban "
         "<font face='Courier'>UnicodeEncodeError</font> (cp1252); y en cierto momento el shell "
         "de Bash se quedó sin PATH (ni <font face='Courier'>ls</font> funcionaba).",
         "<b>Solución:</b> ejecutar Python con <font face='Courier'>PYTHONUTF8=1</font> "
         "(fuerza UTF-8 en E/S) y escribir siempre el JSON con "
         "<font face='Courier'>ensure_ascii=False</font>; y cambiar a PowerShell cuando Bash "
         "falló. Los datos siempre estuvieron bien (UTF-8); era solo la <b>visualización</b>."])

callout("error", "Imágenes enormes (rendimiento)",
        ["<b>Síntoma:</b> la imagen del hero pesaba <b>19 MB</b> (5192x3072).",
         "<b>Solución:</b> redimensionar a 1600 px y convertir a WebP con "
         "<font face='Courier'>sharp</font>: 19 MB -&gt; 46 KB (-99,75%). También se redujo el "
         "favicon (PNG de 200 KB -&gt; 19 KB) y se corrigió su declaración "
         "<font face='Courier'>type</font>."])

# =========================================================================
#  7. VENTAJAS / DESVENTAJAS
# =========================================================================
h1("7. Ventajas y desventajas de cada implementación")
h2("7.1 Traducción por oración: LLM (Gemini) vs MT offline (opus-mt)")
tabla([
    ["Criterio", "LLM (Gemini)", "MT offline (opus-mt)"],
    ["Calidad", "Muy alta, literaria", "Buena, con errores semánticos"],
    ["Automatización", "Semi-manual (copia-pega)", "Total (script)"],
    ["Coste / dependencia", "Requiere el LLM (aunque offline: 1 vez)",
     "Modelo local ~300 MB; CPU"],
    ["Alineación 1:1", "Hay que validarla (prompt + verificador)",
     "Automática (una salida por frase)"],
    ["Escalabilidad", "Limitada por el copia-pega", "Alta (miles de frases)"],
], [3.4 * cm, 6.5 * cm, 6.5 * cm])

h2("7.2 Traducción por palabra: capas del traductor")
tabla([
    ["Capa", "Ventaja", "Desventaja"],
    ["Directo deu-spa", "Mejor calidad y precisión", "Cobertura limitada (~70%)"],
    ["Cadena de-&gt;en-&gt;es", "Gran cobertura (deu-eng es enorme)",
     "Dos saltos: ruido y pérdida de sentido; se marca"],
    ["Cabeza de compuesto", "Recupera compuestos ausentes",
     "Aproximada; puede errar (Handschuh)"],
], [3.6 * cm, 6.4 * cm, 6.4 * cm])

h2("7.3 Otras decisiones")
tabla([
    ["Decisión", "Ventaja", "Desventaja"],
    ["Texto paralelo para traducir la frase",
     "Determinista, sin API; sirve para gramática futura",
     "Sólo frase, no palabra; hay que alinear"],
    ["Léxico para traducir la palabra",
     "Traducción por palabra offline y precisa",
     "No capta contexto; requiere el pipeline"],
    ["localStorage para el estado",
     "Cero backend; privado; simple",
     "No sincroniza entre dispositivos"],
    ["Modelo spaCy md vs sm",
     "Mejor lematización (etiquetado más preciso)",
     "Más peso y algo más lento"],
    ["Léxico por dynamic import",
     "Bundle inicial mucho menor; cacheado",
     "Pequeña latencia al abrir la primera lectura"],
], [4.4 * cm, 6.0 * cm, 6.0 * cm])

# =========================================================================
#  8. LIBRERÍAS Y MODELOS
# =========================================================================
h1("8. Librerías, modelos y recursos")
h2("8.1 Frontend")
tabla([
    ["Recurso", "Licencia", "Uso"],
    ["React 19 / react-dom", "MIT", "UI por componentes"],
    ["Vite 8", "MIT", "Bundler + dev server"],
    ["react-router-dom 7", "MIT", "Enrutado y URLs"],
    ["Vitest 4", "MIT", "Pruebas del motor puro"],
    ["sharp (dev, puntual)", "Apache-2.0", "Optimización de imágenes (WebP)"],
], [5.0 * cm, 2.6 * cm, 8.8 * cm])
h2("8.2 Pipeline de PLN")
tabla([
    ["Recurso", "Licencia", "Uso"],
    ["spaCy + de_core_news_md / en_core_web_sm / es_core_news_md", "MIT",
     "Segmentación, tokenización, lematización, dependencias (un modelo por idioma)"],
    ["FreeDict deu-spa / deu-eng / eng-spa (TEI)", "Libre (GPL/CC)",
     "Traducción por palabra (directo + cadena; el inglés va directo por eng-spa)"],
    ["transformers + torch", "Apache-2.0 / BSD",
     "Ejecutar opus-mt"],
    ["Helsinki-NLP/opus-mt-de-es y opus-mt-en-es (Marian)", "CC-BY / Apache",
     "MT por frase de-&gt;es y en-&gt;es (offline)"],
    ["wordfreq", "Apache-2.0",
     "Frecuencia Zipf del español general: detecta las voces raras a glosar"],
    ["glosas_es.json (curado propio)", "—",
     "Glosario monolingüe de voces raras del español (definiciones a mano)"],
    ["Argos Translate (evaluado, descartado)", "MIT/CC",
     "MT por pivote; peor calidad para de-&gt;es"],
    ["pip-system-certs", "BSD",
     "Usar el almacén de certificados de Windows (SSL)"],
    ["Project Gutenberg (textos)", "Dominio público",
     "Corpus de lectura (Kafka, Storm, Wells, Dickens, Poe, Mann, Cervantes, Quevedo, "
     "Darío, Quiroga, Esopo, Grimm)"],
], [5.6 * cm, 3.0 * cm, 7.8 * cm])
h2("8.3 Modelos: notas de tamaño y calidad")
li([
    "<b>de_core_news_md / es_core_news_md</b>: modelos medianos; mejor etiquetado y "
    "lematización que los pequeños. Clave para reducir errores de lema.",
    "<b>opus-mt-de-es / opus-mt-en-es</b>: ~300 MB cada uno; inferencia en CPU; directos "
    "(sin pivote). El par en-&gt;es da calidad claramente superior.",
    "Las dependencias pesadas de MT (transformers/torch) y los modelos <b>no</b> se versionan "
    "en git; se documentan y se cachean fuera del repo. Solo se versiona el JSON de salida.",
])

# =========================================================================
#  9. INSIGHTS
# =========================================================================
h1("9. Insights y metodología")
li([
    "<b>Separar lo puro de lo impuro.</b> Extraer la lógica (LCG, bolsa, progreso) a módulos "
    "sin efectos secundarios permitió probarla con Vitest y reutilizarla; el patrón se repitió "
    "en el pipeline (traductor, construir_lexico).",
    "<b>Medir antes de optimizar.</b> El diagnóstico de cobertura por POS reveló que el "
    "problema no era la lematización sino el <b>tamaño del diccionario</b>; eso orientó la "
    "solución (cadena por inglés) en vez de perseguir mejoras marginales del lematizador.",
    "<b>Validar la alineación siempre.</b> El verificador 1:1 del importador de traducciones "
    "convirtió un paso frágil (pegar la salida de un LLM) en algo seguro: si algo no cuadra, "
    "no escribe nada.",
    "<b>Formatos “pipeline-ready”.</b> Diseñar el JSON desde el principio con el formato que "
    "emitiría el pipeline evitó rehacer el frontend cuando este llegó.",
    "<b>Diferenciar problema de datos y problema de visualización.</b> Muchos “errores” "
    "(umlauts como cajas) eran solo codificación de consola; los datos estaban bien.",
    "<b>Procedencia y licencias.</b> Cada lectura guarda su campo <font face='Courier'>fuente</font> "
    "con la obra, el autor y la URL de dominio público: transparencia para la tesis.",
])

# =========================================================================
#  10. ESTADO ACTUAL Y FUTURO
# =========================================================================
h1("10. Estado actual y trabajo futuro")
h2("Hecho")
li([
    "Sección de Lectura completa (biblioteca, lector, bolsa, progreso, libros por partes) "
    "en <b>tres idiomas de estudio</b>.",
    "Pipeline de PLN multilingüe: ingesta con modelo spaCy por idioma (y fragmentos con "
    "max_chars/fin), traducción por palabra (FreeDict por capas para de; eng-spa directo "
    "para en), por frase (Gemini y opus-mt de-&gt;es / en-&gt;es) y <b>glosado monolingüe "
    "del español</b> (wordfreq + glosario curado).",
    "Contenido: 9 lecturas cortas trilingües + 2 libros alemanes (Die Verwandlung, Immensee) "
    "+ 4 ingleses (Wells, Dickens, Poe, Mann) + 4 españoles (Quijote y Buscón en fragmento; "
    "Azul… y los Cuentos de Quiroga completos).",
    "Idioma de estudio global (contexto persistido), bolsa filtrada por idioma y perfil "
    "export/import sin servidor.",
    "Motor puro con pruebas (161 en toda la plataforma); Codenames refactorizado; recursos "
    "optimizados.",
])
h2("Pendiente / próximos pasos")
li([
    "<b>Ampliar el glosario español:</b> subir la densidad de glosas de Azul/Quiroga y "
    "extender el fragmento del Quijote (p. ej. hasta los molinos de viento, cap. VIII).",
    "<b>Léxico por token:</b> anotar la traducción por posición en el pipeline para resolver "
    "la ambigüedad de forma general (hoy: overrides por lectura).",
    "<b>Optimización adicional del peso:</b> separar metadatos del contenido para cargar las "
    "lecturas también bajo demanda; dividir el léxico por idioma/libro.",
    "<b>Mejorar cobertura y MT:</b> analizador morfológico para verbos fuertes alemanes; "
    "evaluar modelos de MT mayores.",
])

# =========================================================================
#  11. GLOSARIO
# =========================================================================
h1("11. Glosario técnico")
glos = [
    ("PLN / NLP", "Procesamiento de Lenguaje Natural."),
    ("spaCy", "Librería de PLN en Python (segmentación, POS, lemas, dependencias)."),
    ("Lema / lematización", "Forma de diccionario de una palabra (kauft -> kaufen)."),
    ("POS", "Part-of-speech: categoría gramatical (VERB, NOUN, ADJ…)."),
    ("Dependencia svp", "Etiqueta de spaCy para el prefijo de un verbo separable alemán."),
    ("Verbo separable", "Verbo alemán cuyo prefijo se desplaza (bereitet … vor = vorbereiten)."),
    ("FreeDict", "Colección de diccionarios bilingües libres en formato TEI (XML)."),
    ("TEI", "Text Encoding Initiative: estándar XML para textos y diccionarios."),
    ("MT", "Machine Translation (traducción automática)."),
    ("opus-mt / Marian", "Modelos de MT abiertos de Helsinki-NLP."),
    ("LLM", "Large Language Model (p. ej. Gemini)."),
    ("Alineación 1:1", "Correspondencia frase a frase entre el original y su traducción."),
    ("LCG", "Linear Congruential Generator: generador pseudoaleatorio (aritmética modular)."),
    ("Fisher-Yates", "Algoritmo para barajar un arreglo de forma uniforme."),
    ("SPA / bundle", "Single Page Application; bundle: JS empaquetado que se descarga."),
    ("dynamic import", "Carga de un módulo bajo demanda; genera un chunk aparte en Vite."),
    ("Cobertura de traducción", "% de formas de palabra distintas que reciben traducción."),
    ("Glosa / glosado", "Definición breve en la misma lengua para una voz rara (español)."),
    ("Escala Zipf", "log10 de la frecuencia por millón de palabras; mide la rareza léxica."),
    ("wordfreq", "Biblioteca Python con frecuencias léxicas multilíngües (escala Zipf)."),
    ("Leitner / SM-2 / FSRS", "Algoritmos de repetición espaciada para el repaso."),
]
tabla([["Término", "Definición"]] + [[t, d] for t, d in glos], [4.4 * cm, 12 * cm])

story.append(Spacer(1, 0.4 * cm))
story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL))
story.append(Paragraph(
    "Documento generado con ReportLab a partir del historial de desarrollo del proyecto "
    "<i>indescifrable</i>. Repositorio: github.com/Eduard-Cini/indescifrable.",
    S["small"]))


# --- Numeración de páginas ------------------------------------------------
def _pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
    canvas.drawString(2 * cm, 1.2 * cm, "Plataforma de idiomas — Documentación técnica")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(SALIDA), pagesize=A4,
    leftMargin=2.3 * cm, rightMargin=2.3 * cm, topMargin=2 * cm, bottomMargin=1.8 * cm,
    title="Documentación técnica — Plataforma de idiomas",
    author="Proyecto indescifrable",
)
doc.build(story, onFirstPage=_pie, onLaterPages=_pie)
print(f"PDF generado: {SALIDA}  ({SALIDA.stat().st_size // 1024} KB)")
