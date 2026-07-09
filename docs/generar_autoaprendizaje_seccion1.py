# -*- coding: utf-8 -*-
"""Genera docs/autoaprendizaje-seccion1.pdf: un plan de estudio práctico y progresivo
para dominar todo lo necesario y poder construir por cuenta propia la sección
de lectura y su pipeline de PLN. Cada fase incluye objetivo, conceptos,
mini-implementación (ejercicio), ejemplo de código, recursos y criterio de
dominio.  Uso:  python docs/generar_autoaprendizaje_seccion1.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Preformatted, HRFlowable, KeepTogether,
)

SALIDA = Path(__file__).parent / "autoaprendizaje-seccion1.pdf"

AZUL = colors.HexColor("#1f3a5f")
AZUL2 = colors.HexColor("#2e5e8c")
VERDE = colors.HexColor("#2e6b45")
MORADO = colors.HexColor("#5a3a7a")
GRIS = colors.HexColor("#555555")
GRIS_CLARO = colors.HexColor("#f0f0f0")
GRIS_CODIGO = colors.HexColor("#f5f5f2")
AMBAR = colors.HexColor("#7a5a00")

ss = getSampleStyleSheet()
S = {}
S["titulo"] = ParagraphStyle("titulo", parent=ss["Title"], fontSize=23, textColor=AZUL,
                             spaceAfter=6, leading=27)
S["subtitulo"] = ParagraphStyle("subtitulo", parent=ss["Normal"], fontSize=12, textColor=GRIS,
                                alignment=TA_CENTER, spaceAfter=4)
S["h1"] = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=15.5, textColor=AZUL,
                         spaceBefore=15, spaceAfter=5, leading=18)
S["h2"] = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, textColor=AZUL2,
                         spaceBefore=9, spaceAfter=3, leading=14)
S["body"] = ParagraphStyle("body", parent=ss["Normal"], fontSize=9.7, leading=13.6,
                           alignment=TA_JUSTIFY, spaceAfter=5)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], leftIndent=12, bulletIndent=2,
                             spaceAfter=2)
S["code"] = ParagraphStyle("code", parent=ss["Code"], fontSize=8.2, leading=10.5,
                           textColor=colors.HexColor("#1a1a1a"))
S["small"] = ParagraphStyle("small", parent=S["body"], fontSize=8.3, textColor=GRIS,
                            alignment=TA_LEFT)
S["cell"] = ParagraphStyle("cell", parent=ss["Normal"], fontSize=8.3, leading=11)
S["cellh"] = ParagraphStyle("cellh", parent=S["cell"], textColor=colors.white,
                            fontName="Helvetica-Bold")


def _san(t):
    for a, b in {"→": "-&gt;", "⇄": "&lt;-&gt;", "✓": "[OK]", "✗": "[X]", "≈": "~",
                 "×": "x", "≥": "&gt;=", "•": "-", "€": "EUR"}.items():
        t = t.replace(a, b)
    return t


story = []


def h1(t):
    story.append(Paragraph(t, S["h1"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL, spaceAfter=4))


def h2(t):
    story.append(Paragraph(t, S["h2"]))


def p(t):
    story.append(Paragraph(_san(t), S["body"]))


def li(items, style=None):
    for it in items:
        story.append(Paragraph("• " + _san(it), style or S["bullet"]))
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


def tabla(filas, anchos):
    data = [[Paragraph(_san(c), S["cellh"] if i == 0 else S["cell"]) for c in fila]
            for i, fila in enumerate(filas)]
    tbl = Table(data, colWidths=anchos, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ("BACKGROUND", (0, 0), (-1, 0), AZUL2),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 7))


def caja(tipo, titulo, cuerpo, items=None):
    color = {"mini": VERDE, "dominio": AMBAR, "concepto": MORADO}[tipo]
    etiqueta = {"mini": "MINI-IMPLEMENTACIÓN", "dominio": "SABRÁS QUE LO DOMINAS CUANDO",
                "concepto": "IDEA CLAVE"}[tipo]
    cont = [Paragraph(f'<b>{etiqueta}{" — " + _san(titulo) if titulo else ""}</b>',
                      ParagraphStyle("ct", parent=S["body"], textColor=color, spaceAfter=3,
                                     fontSize=9.3))]
    for par in cuerpo:
        cont.append(Paragraph(_san(par), ParagraphStyle("cb", parent=S["body"], fontSize=9,
                                                        spaceAfter=3)))
    for it in (items or []):
        cont.append(Paragraph("• " + _san(it), ParagraphStyle(
            "cbi", parent=S["body"], fontSize=9, leftIndent=10, spaceAfter=1)))
    tbl = Table([[cont]], colWidths=[16.4 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbfbf9")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, color),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e2e2")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether(tbl))
    story.append(Spacer(1, 7))


def recursos(items):
    h2("Recursos")
    for nombre, url, nota in items:
        story.append(Paragraph(
            f'• <b>{_san(nombre)}</b> — <font face="Courier" size="8">{url}</font><br/>'
            f'<font size="8.5" color="#555555">{_san(nota)}</font>',
            ParagraphStyle("rec", parent=S["body"], leftIndent=12, spaceAfter=4)))
    story.append(Spacer(1, 3))


# =========================================================================
#  PORTADA
# =========================================================================
story.append(Spacer(1, 3.3 * cm))
story.append(Paragraph("Sección 1 — Lectura", ParagraphStyle(
    "secmarker", parent=S["subtitulo"], textColor=AZUL2,
    fontName="Helvetica-Bold", fontSize=13, spaceAfter=6)))
story.append(Paragraph("Plan de aprendizaje práctico", S["titulo"]))
story.append(Paragraph("Cómo dominar (y saber construir tú mismo) la sección de lectura "
                       "y su pipeline de PLN", S["subtitulo"]))
story.append(Spacer(1, 0.5 * cm))
story.append(HRFlowable(width="60%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph(
    "Ruta progresiva de 8 fases, de lo básico a un proyecto final. Cada fase trae objetivo, "
    "conceptos, una <b>mini-implementación</b> para aprender haciendo, un ejemplo de código, "
    "recursos y un criterio de dominio. Al final, un <b>capstone</b> que recrea de punta a "
    "punta una versión mínima de la sección de lectura.",
    ParagraphStyle("intro", parent=S["body"], alignment=TA_CENTER, fontSize=10, textColor=GRIS)))
story.append(PageBreak())

# =========================================================================
#  CÓMO USAR + MAPA
# =========================================================================
h1("Cómo usar este plan")
li([
    "<b>Aprende haciendo.</b> No pases de fase sin completar su mini-implementación; el "
    "objetivo no es leer, es <b>saber construirlo</b>.",
    "<b>Orden sugerido:</b> las fases 1-4 (frontend) y 5-8 (Python/PLN) son bastante "
    "independientes; puedes alternarlas, pero dentro de cada bloque respeta el orden.",
    "<b>Dos velocidades:</b> ruta rápida = solo mini-implementaciones + capstone (~3-4 "
    "semanas a tiempo parcial); ruta profunda = añade los recursos largos y los retos extra.",
    "<b>Ten el repo a la vista.</b> Cada fase corresponde a archivos reales del proyecto "
    "<i>indescifrable</i>; ábrelos como “solución de referencia” tras intentar tu versión.",
])
h2("Mapa de fases")
tabla([
    ["Fase", "Tema", "Archivos de referencia en el repo"],
    ["0", "Prerrequisitos: JS moderno, Node, Git", "—"],
    ["1", "React: componentes, estado, efectos", "Landing.jsx, Tablero.jsx"],
    ["2", "Persistencia + funciones puras + pruebas", "engine/bolsa.js, *.test.js"],
    ["3", "Enrutado y estructura de la app", "App.jsx, Biblioteca.jsx"],
    ["4", "Datos y experiencia de lectura", "Lector.jsx, data/lecturas/"],
    ["5", "Python + spaCy (segmentar, lematizar)", "pipeline/procesar.py"],
    ["6", "Diccionarios, traducción por palabra y glosado", "pipeline/traductor.py, glosas_es.json"],
    ["7", "Traducción por oración: MT y LLM", "pipeline/mt.py, importar_traduccion.py"],
    ["8", "Integración del pipeline y despliegue", "construir_lexico.py, Netlify/git"],
    ["Cap.", "Capstone: mini-lector de punta a punta", "(todo junto)"],
], [1.2 * cm, 5.6 * cm, 9.6 * cm])

# =========================================================================
#  FASE 0
# =========================================================================
h1("Fase 0 — Prerrequisitos: JavaScript moderno, Node y Git")
p("<b>Objetivo:</b> manejar con soltura el JavaScript que usa React y las herramientas de "
  "base. Sin esto, todo lo demás cuesta el doble.")
h2("Conceptos clave")
li([
    "ES6+: <font face='Courier'>const/let</font>, funciones flecha, <b>destructuring</b>, "
    "spread <font face='Courier'>...</font>, template strings, módulos "
    "<font face='Courier'>import/export</font>.",
    "Métodos de arreglo: <font face='Courier'>map, filter, reduce, find, some</font> "
    "(imprescindibles para listas en React).",
    "Asincronía: <font face='Courier'>Promise</font>, <font face='Courier'>async/await</font>, "
    "<font face='Courier'>fetch</font>.",
    "Node + npm (instalar dependencias, scripts) y Git (commit, push, ramas).",
])
caja("mini", "Calentamiento sin framework",
     ["Crea un archivo <font face='Courier'>bolsa.js</font> con funciones puras que operen "
      "sobre un arreglo de palabras y pruébalas con <font face='Courier'>console.log</font>:"],
     items=[
         "<font face='Courier'>agregar(bolsa, palabra)</font> que no duplique.",
         "<font face='Courier'>quitar(bolsa, palabra)</font> y <font face='Courier'>contar(bolsa)</font>.",
         "Reto: que <font face='Courier'>agregar</font> devuelva un <b>nuevo</b> arreglo "
         "(inmutabilidad), sin mutar el original.",
     ])
code('''export const agregar = (bolsa, p) =>
  bolsa.includes(p) ? bolsa : [...bolsa, p];

console.log(agregar(["sol"], "luna")); // ["sol","luna"]
console.log(agregar(["sol"], "sol"));  // ["sol"]  (no duplica)''')
recursos([
    ("javascript.info", "https://javascript.info", "El mejor tutorial moderno de JS, gratis."),
    ("MDN JavaScript", "https://developer.mozilla.org/es/docs/Web/JavaScript",
     "Referencia. Busca map/filter/reduce, destructuring, async/await."),
    ("Node.js", "https://nodejs.org", "Instala la versión LTS; trae npm."),
    ("Git handbook", "https://docs.github.com/get-started", "commit, push, ramas."),
])
caja("dominio", "",
     ["Puedes escribir funciones que reciben datos y devuelven datos nuevos sin mutar, y "
      "explicar la diferencia entre <font face='Courier'>map</font> y "
      "<font face='Courier'>forEach</font>."])

# =========================================================================
#  FASE 1
# =========================================================================
h1("Fase 1 — React: componentes, estado y efectos")
p("<b>Objetivo:</b> construir interfaces por componentes y entender <b>cuándo</b> y "
  "<b>por qué</b> se vuelven a renderizar.")
h2("Conceptos clave")
li([
    "Componente = función que devuelve JSX. Props (datos que entran) vs estado "
    "(<font face='Courier'>useState</font>).",
    "Renderizado condicional (<font face='Courier'>{cond &amp;&amp; ...}</font>) y listas con "
    "<font face='Courier'>.map()</font> + <font face='Courier'>key</font> estable.",
    "<font face='Courier'>useEffect</font> para efectos (cargar datos, temporizadores) y su "
    "array de dependencias.",
    "Eventos: <font face='Courier'>onClick</font>, <font face='Courier'>onChange</font>; "
    "subir el estado al componente padre.",
])
caja("mini", "Bolsa de palabras en pantalla",
     ["Monta un proyecto con Vite (<font face='Courier'>npm create vite@latest -- --template "
      "react</font>) y crea una <b>Bolsa</b>: un input + botón que añade palabras a una lista "
      "en <font face='Courier'>useState</font>, con botón para quitar cada una."],
     items=[
         "Usa <font face='Courier'>.map()</font> con <font face='Courier'>key</font> para la lista.",
         "Reto: importa tu <font face='Courier'>agregar/quitar</font> de la Fase 0 y úsalos "
         "(lógica separada de la UI).",
     ])
code('''function Bolsa() {
  const [palabras, setPalabras] = useState([]);
  const [texto, setTexto] = useState("");
  return (
    <div>
      <input value={texto} onChange={e => setTexto(e.target.value)} />
      <button onClick={() => setPalabras(agregar(palabras, texto))}>Añadir</button>
      <ul>{palabras.map(p => <li key={p}>{p}</li>)}</ul>
    </div>
  );
}''')
recursos([
    ("react.dev — Learn", "https://react.dev/learn", "Tutorial oficial. Haz “Tic-Tac-Toe” y “Thinking in React”."),
    ("react.dev — useEffect", "https://react.dev/learn/synchronizing-with-effects",
     "Cuándo (y cuándo NO) usar efectos."),
    ("Vite — Guide", "https://vite.dev/guide/", "Crear el proyecto, dev server, build."),
])
caja("dominio", "",
     ["Puedes explicar por qué React necesita <font face='Courier'>key</font> en las listas y "
      "predecir cuándo se re-renderiza un componente."])

# =========================================================================
#  FASE 2
# =========================================================================
h1("Fase 2 — Persistencia, funciones puras y pruebas")
p("<b>Objetivo:</b> separar la <b>lógica pura</b> (testeable) de los <b>efectos</b> "
  "(localStorage, DOM). Es el patrón del “motor” del proyecto y el germen del núcleo "
  "matemático de la tesis.")
caja("concepto", "Puro vs impuro",
     ["Una función <b>pura</b> no toca el mundo exterior: misma entrada -&gt; misma salida, "
      "sin efectos. <font face='Courier'>agregarPalabra(bolsa, x)</font> es pura; "
      "<font face='Courier'>localStorage.setItem(...)</font> es un efecto. Separarlos permite "
      "<b>probar</b> la lógica en aislamiento y reutilizarla."])
h2("Conceptos clave")
li([
    "<font face='Courier'>localStorage</font>: guardar/leer JSON (adaptador delgado e impuro).",
    "Módulo puro: la regla del proyecto es “una palabra ya presente <b>conserva su estado</b>”.",
    "Pruebas con <b>Vitest</b>: <font face='Courier'>describe/it/expect</font>.",
])
caja("mini", "Motor de la bolsa + su prueba",
     ["Extrae <font face='Courier'>agregarPalabra/quitarPalabra</font> a "
      "<font face='Courier'>bolsa.js</font>, un <font face='Courier'>almacenamiento.js</font> "
      "que persista en localStorage, y escribe una prueba Vitest."],
     items=[
         "Test: agregar una palabra nueva la añade; agregar una existente <b>no</b> la duplica "
         "ni cambia su estado.",
         "Instala y corre: <font face='Courier'>npm i -D vitest</font> y "
         "<font face='Courier'>npx vitest</font>.",
     ])
code('''import { describe, it, expect } from "vitest";
import { agregarPalabra } from "./bolsa";

it("no duplica ni reinicia una palabra existente", () => {
  const previa = { id: "de:frau", caja: 4 };       // estado acumulado
  const bolsa = agregarPalabra([previa], { id: "de:frau", caja: 0 });
  expect(bolsa).toHaveLength(1);
  expect(bolsa[0].caja).toBe(4);                    // conserva el estado
});''')
recursos([
    ("Vitest", "https://vitest.dev/guide/", "Configuración y API de pruebas."),
    ("MDN localStorage", "https://developer.mozilla.org/es/docs/Web/API/Window/localStorage",
     "getItem/setItem + JSON.parse/stringify."),
    ("react.dev — Keeping components pure", "https://react.dev/learn/keeping-components-pure",
     "Por qué la pureza importa."),
])
caja("dominio", "",
     ["Puedes escribir una función pura, su adaptador de persistencia y una prueba que "
      "verifique una regla de negocio."])

# =========================================================================
#  FASE 3
# =========================================================================
h1("Fase 3 — Enrutado y estructura de la aplicación")
p("<b>Objetivo:</b> convertir componentes sueltos en una app con secciones y URLs.")
h2("Conceptos clave")
li([
    "<font face='Courier'>react-router-dom</font>: <font face='Courier'>BrowserRouter, Routes, "
    "Route, Link, useParams, useNavigate</font>.",
    "Parámetros de ruta (<font face='Courier'>/lectura/:id</font>) y de búsqueda "
    "(<font face='Courier'>useSearchParams</font>) para conservar filtros.",
    "Fallback SPA en el hosting (<font face='Courier'>_redirects</font> en Netlify) para que "
    "las URLs profundas no den 404.",
])
caja("mini", "Biblioteca -> Detalle",
     ["Crea 3 rutas: inicio, una lista de elementos, y un detalle "
      "<font face='Courier'>/item/:id</font>. Al hacer clic en la lista, navega al detalle y "
      "lee el <font face='Courier'>:id</font> con <font face='Courier'>useParams</font>."],
     items=[
         "Guarda un filtro (idioma/nivel) en la URL con "
         "<font face='Courier'>useSearchParams</font> y comprueba que se conserva al volver.",
     ])
code('''<Routes>
  <Route path="/" element={<Home/>} />
  <Route path="/lectura" element={<Biblioteca/>} />
  <Route path="/lectura/:idioma/:nivel/:id" element={<Lector/>} />
</Routes>
// en Lector:  const { idioma, nivel, id } = useParams();''')
recursos([
    ("React Router — Tutorial", "https://reactrouter.com/start/tutorial",
     "Rutas, params, navegación."),
    ("Netlify — Redirects", "https://docs.netlify.com/routing/redirects/",
     "El fallback /* /index.html 200 para SPA."),
])
caja("dominio", "",
     ["Puedes montar una app multi-página con URLs compartibles y leer parámetros de la ruta."])

# =========================================================================
#  FASE 4
# =========================================================================
h1("Fase 4 — Modelado de datos y la experiencia de lectura")
p("<b>Objetivo:</b> el corazón del frontend: renderizar un texto con palabras clicables, "
  "mostrar traducciones y la traducción por frase.")
h2("Conceptos clave")
li([
    "Diseñar el JSON de una lectura: <font face='Courier'>cuerpo</font> como arreglo de frases "
    "<b>alineadas</b> por índice entre idiomas.",
    "<b>Tokenización</b> con regex Unicode (<font face='Courier'>\\p{L}</font>) que separa "
    "palabras de puntuación conservando el texto.",
    "Mapear un clic de palabra a una entrada de un <b>léxico</b> "
    "(<font face='Courier'>idioma:forma -&gt; traducción</font>).",
    "Cargar datos con <font face='Courier'>import.meta.glob</font> y el léxico grande con "
    "<font face='Courier'>dynamic import</font> (peso del bundle).",
])
caja("mini", "Mini-lector",
     ["Con un objeto JS <font face='Courier'>{ de:[...], es:[...] }</font> y un mini-léxico "
      "<font face='Courier'>{ 'de:frau':'mujer', ... }</font>, renderiza el texto alemán con "
      "cada palabra clicable; al hacer clic, muestra su traducción; y un botón por frase que "
      "revela la línea española alineada."],
     items=[
         "Escribe <font face='Courier'>tokenizar(frase)</font> con "
         "<font face='Courier'>String.matchAll</font> y una regex Unicode.",
         "Reto: resalta las palabras que ya guardaste en la bolsa.",
     ])
code('''function tokenizar(frase) {
  const re = /\\p{L}[\\p{L}\\p{M}\'-]*/gu;   // 'u' = unicode
  const out = []; let last = 0, m;
  while ((m = re.exec(frase)) !== null) {
    if (m.index > last) out.push({tipo:"sep", v: frase.slice(last, m.index)});
    out.push({tipo:"palabra", v: m[0]});
    last = m.index + m[0].length;
  }
  if (last < frase.length) out.push({tipo:"sep", v: frase.slice(last)});
  return out;
}''')
recursos([
    ("MDN — Unicode property escapes", "https://developer.mozilla.org/es/docs/Web/JavaScript/Guide/Regular_expressions/Unicode_character_class_escapes",
     "La clave de \\p{L} y la bandera u."),
    ("Vite — Glob import", "https://vite.dev/guide/features.html#glob-import",
     "import.meta.glob (eager y lazy) y dynamic import."),
])
caja("dominio", "",
     ["Puedes convertir una frase en palabras clicables y conectarlas a un diccionario en "
      "memoria, con la traducción por frase alineada."])

# =========================================================================
#  FASE 5
# =========================================================================
h1("Fase 5 — Python + spaCy: segmentar, tokenizar, lematizar")
p("<b>Objetivo:</b> el primer paso del pipeline. Convertir texto crudo en frases y en tokens "
  "con su lema y categoría gramatical.")
h2("Conceptos clave")
li([
    "Entorno de Python: <font face='Courier'>venv</font> + <font face='Courier'>pip</font>; "
    "instalar spaCy y un modelo (<font face='Courier'>python -m spacy download de_core_news_md"
    "</font>).",
    "El objeto <font face='Courier'>doc = nlp(texto)</font>: iterar tokens; "
    "<font face='Courier'>token.lemma_, .pos_, .dep_</font>; frases con "
    "<font face='Courier'>doc.sents</font>.",
    "Ambigüedad morfológica y su tratamiento algorítmico (los <b>verbos separables</b> del "
    "alemán vía la dependencia <font face='Courier'>svp</font>).",
])
caja("mini", "Lemas y verbos separables",
     ["Escribe un script que imprima, para cada token de una frase alemana, su forma y su "
      "lema. Luego detecta la dependencia <font face='Courier'>svp</font> y <b>reconstruye</b> "
      "el verbo separable."],
     items=[
         "Frase de prueba: <font face='Courier'>“…bereitet sie das Frühstück … vor.”</font> "
         "-&gt; el lema real de <i>bereitet</i> es <b>vorbereiten</b>.",
         "Reto: cuenta cuántas frases produce spaCy en un párrafo largo y compara con las que "
         "esperabas (verás el problema de las líneas envueltas).",
     ])
code('''import spacy
nlp = spacy.load("de_core_news_md")
doc = nlp("Zu Hause bereitet sie das Frühstück für ihre Familie vor.")
lemas = {t.i: t.lemma_ for t in doc}
for t in doc:
    if t.dep_ == "svp":                       # prefijo separable
        lemas[t.head.i] = t.text.lower() + t.head.lemma_   # vor+bereiten
print(lemas)   # ... 'vorbereiten' ...''')
recursos([
    ("spaCy — Curso gratis", "https://course.spacy.io/es",
     "Curso interactivo oficial (¡en español!). El mejor punto de entrada."),
    ("spaCy 101", "https://spacy.io/usage/spacy-101", "Conceptos y objetos base."),
    ("spaCy — Linguistic features", "https://spacy.io/usage/linguistic-features",
     "POS, lemas, dependencias, morfología."),
])
caja("dominio", "",
     ["Puedes cargar un modelo, extraer frases y lemas, e inspeccionar dependencias para "
      "resolver un caso morfológico."])

# =========================================================================
#  FASE 6
# =========================================================================
h1("Fase 6 — Diccionarios, traducción por palabra y glosado monolingüe")
p("<b>Objetivo:</b> traducir palabra por palabra <b>sin API</b>, aprender a medir y mejorar "
  "la cobertura, y — para la lengua materna — <b>glosar</b> las voces raras en vez de "
  "traducirlas.")
h2("Conceptos clave")
li([
    "Parsear un diccionario <b>FreeDict</b> (TEI/XML) con "
    "<font face='Courier'>xml.etree.ElementTree</font>; cuidado con los "
    "<b>namespaces</b> XML.",
    "Estrategia por capas: directo -&gt; <b>cadena</b> por un idioma puente (de-&gt;en-&gt;es) "
    "-&gt; <b>descomposición de compuestos</b>.",
    "<b>Cobertura</b>: % de formas con traducción; diagnóstico por categoría gramatical para "
    "saber qué falla y por qué.",
    "<b>Glosado monolingüe</b>: cuando la lengua de estudio es la materna no hay lengua "
    "destino; se define la voz rara en la misma lengua. La <b>rareza</b> se decide con la "
    "frecuencia general (escala Zipf, biblioteca <font face='Courier'>wordfreq</font>) y las "
    "definiciones se curan a mano — los MT no sirven aquí.",
])
caja("concepto", "Medir antes de optimizar",
     ["En el proyecto, la cobertura pasó de 70% a 92%. El diagnóstico reveló que el problema "
      "no era la lematización sino el <b>tamaño del diccionario</b>: por eso la solución fue la "
      "cadena por inglés (el diccionario de-&gt;en es enorme), no perseguir mejoras marginales "
      "del lematizador."])
caja("mini", "Parser + traductor con fallback",
     ["Descarga un FreeDict pequeño (p. ej. deu-spa), parsea las entradas a un dict "
      "<font face='Courier'>lema-&gt;traducción</font>, y escribe "
      "<font face='Courier'>traducir(lema, forma)</font> que pruebe: lema, luego la forma, y "
      "sobre una lista de 50 palabras <b>mide la cobertura</b>."],
     items=[
         "Reto: añade la cabeza del compuesto (sufijo &gt;= 3 letras) como último fallback.",
         "Reto 2 (glosado): con <font face='Courier'>wordfreq</font>, extrae de un párrafo "
         "del Quijote las palabras con <font face='Courier'>zipf_frequency(p,'es') &lt; 3</font> "
         "y escribe a mano su definición — acabas de construir un mini-glosario monolingüe.",
     ])
code('''import xml.etree.ElementTree as ET
NS = "{http://www.tei-c.org/ns/1.0}"
raiz = ET.parse("deu-spa.tei").getroot()
dic = {}
for e in raiz.iter(f"{NS}entry"):
    orth = e.find(f".//{NS}form/{NS}orth")
    trads = [q.text for c in e.iter(f"{NS}cit") if c.get("type")=="trans"
             for q in c.findall(f"{NS}quote")]
    if orth is not None and trads:
        dic.setdefault(orth.text.lower(), " / ".join(trads[:3]))
print(dic.get("frau"))   # mujer / esposa / señora''')
recursos([
    ("FreeDict", "https://freedict.org", "Diccionarios libres; descarga el formato ‘src’ (TEI)."),
    ("Python — ElementTree", "https://docs.python.org/3/library/xml.etree.elementtree.html",
     "Parseo de XML; ojo con los namespaces {...}."),
    ("Wiktionary / kaikki", "https://kaikki.org", "Alternativa de mayor cobertura (más pesada)."),
    ("wordfreq", "https://pypi.org/project/wordfreq/",
     "Frecuencias léxicas multilíngües (escala Zipf); detecta las voces raras a glosar."),
])
caja("dominio", "",
     ["Puedes parsear un diccionario, construir un traductor con fallbacks y reportar su "
      "cobertura sobre un texto."])

# =========================================================================
#  FASE 7
# =========================================================================
h1("Fase 7 — Traducción por oración: MT y LLM")
p("<b>Objetivo:</b> dar traducción por frase a un libro conservando la <b>alineación 1:1</b>, "
  "por dos vías, y entender sus compromisos.")
h2("Conceptos clave")
li([
    "El requisito duro: la frase <font face='Courier'>es[i]</font> debe corresponder a "
    "<font face='Courier'>de[i]</font>.",
    "<b>MT offline</b> con <font face='Courier'>transformers</font> + opus-mt "
    "(Helsinki-NLP): automática; alineación garantizada (una salida por frase). Evita el "
    "<b>pivote</b> por inglés si hay modelo directo.",
    "<b>LLM</b> (p. ej. Gemini): mejor calidad pero semi-manual; hay que <b>validar</b> la "
    "salida (prompt numerado + verificador de conteo).",
])
caja("mini", "Traduce 5 frases y valida",
     ["Con opus-mt traduce 5 frases alemanas; imprime pares de-es. Luego escribe un "
      "<b>validador</b> que reciba una traducción numerada de un LLM y compruebe que hay "
      "exactamente una línea por frase (si no cuadra, rechaza)."],
     items=[
         "Compara la misma frase con MT y con un LLM: anota los errores de la MT.",
     ])
code('''from transformers import MarianMTModel, MarianTokenizer
name = "Helsinki-NLP/opus-mt-de-es"
tok, model = MarianTokenizer.from_pretrained(name), MarianMTModel.from_pretrained(name)
def traducir(frases):
    b = tok(frases, return_tensors="pt", padding=True, truncation=True)
    return [tok.decode(g, skip_special_tokens=True) for g in model.generate(**b)]
print(traducir(["Es war kein Traum."]))   # ['No fue un sueño.']''')
recursos([
    ("HF Transformers — Translation", "https://huggingface.co/docs/transformers/tasks/translation",
     "Uso de modelos MarianMT/opus-mt."),
    ("Helsinki-NLP opus-mt", "https://huggingface.co/Helsinki-NLP",
     "Modelos de MT por par de idiomas."),
    ("Argos Translate", "https://github.com/argosopentech/argos-translate",
     "MT offline ligera (pivota por inglés; útil conocer sus límites)."),
])
caja("dominio", "",
     ["Puedes traducir un lote de frases con un modelo local y explicar por qué preferirías un "
      "LLM o una MT según el caso."])

# =========================================================================
#  FASE 8
# =========================================================================
h1("Fase 8 — Integración del pipeline y despliegue")
p("<b>Objetivo:</b> unir todo: de un texto de Gutenberg a JSON que tu app consume, y publicarlo.")
h2("Conceptos clave")
li([
    "Ingesta: descargar de Project Gutenberg, quitar el <b>boilerplate</b> y <b>unir las "
    "líneas envueltas</b> antes de segmentar; trocear en partes legibles.",
    "Exportar JSON <b>“pipeline-ready”</b> con el mismo formato que consume el frontend "
    "(no rehacer el frontend después).",
    "Despliegue: Git + Netlify (build automático); y los baches de entorno "
    "(certificados SSL, codificación UTF-8 en consola).",
])
caja("mini", "De Gutenberg a tu app",
     ["Baja un texto corto de Gutenberg, límpialo, segméntalo con spaCy, exporta un JSON "
      "<font face='Courier'>{ id, cuerpo:{ de:[...] } }</font> y <b>conéctalo</b> a tu "
      "mini-lector de la Fase 4."],
     items=[
         "Añade la traducción por palabra (Fase 6) y por frase con MT (Fase 7).",
         "Sube a un repo y despliega en Netlify con el fallback SPA.",
     ])
code('''# limpiar líneas envueltas de Gutenberg antes de segmentar
import re, requests, spacy
txt = requests.get("https://www.gutenberg.org/cache/epub/22367/pg22367.txt").text
txt = txt.split("*** END")[0]
txt = txt[txt.find("Als Gregor Samsa"):]
flujo = re.sub(r"\\s+", " ", " ".join(txt.splitlines()))
frases = [s.text.strip() for s in spacy.load("de_core_news_md")(flujo).sents]''')
recursos([
    ("Project Gutenberg", "https://www.gutenberg.org", "Textos de dominio público (usa pgID.txt)."),
    ("Netlify — Deploy", "https://docs.netlify.com/site-deploys/create-deploys/",
     "Conecta el repo; build de Vite automático."),
    ("pip-system-certs", "https://pypi.org/project/pip-system-certs/",
     "Si tienes errores SSL en Windows al descargar modelos/diccionarios."),
])
caja("dominio", "",
     ["Puedes llevar un texto crudo a JSON consumible por tu app y publicarlo en la web."])

# =========================================================================
#  CAPSTONE
# =========================================================================
h1("Proyecto final (capstone) — Mini-lector de punta a punta")
p("Reúne todo en una versión mínima pero completa de la sección de lectura. No hace falta "
  "que sea grande; sí que atraviese <b>todas</b> las piezas.")
h2("Requisitos")
li([
    "<b>Pipeline (Python):</b> toma 1 texto corto alemán (10-20 frases), lo segmenta con "
    "spaCy, genera un léxico <font face='Courier'>de:forma-&gt;es</font> con FreeDict (+ "
    "fallback) y una traducción por frase con opus-mt. Exporta 1 JSON.",
    "<b>Frontend (React):</b> biblioteca con esa lectura; lector con palabras clicables "
    "(traducción por palabra), marcador de traducción por frase, y una <b>bolsa</b> "
    "persistente en localStorage.",
    "<b>Motor puro + prueba:</b> la lógica de la bolsa en un módulo puro con al menos un test "
    "Vitest.",
    "<b>Despliegue:</b> repo en Git + Netlify.",
    "<b>Extensión opcional (glosado):</b> añade un texto en tu lengua materna con 5-10 voces "
    "raras glosadas a mano (detectadas con wordfreq) y haz que el popup muestre la definición.",
])
h2("Criterios de éxito")
li([
    "Puedo <b>regenerar</b> el JSON ejecutando el pipeline (reproducible).",
    "Al tocar una palabra veo su traducción; al pulsar el marcador veo la frase en español.",
    "La bolsa sobrevive a recargar la página.",
    "Sé explicar cada decisión (por qué texto paralelo para la frase y léxico para la palabra, "
    "por qué separar lo puro de lo impuro, por qué MT vs LLM).",
])
caja("concepto", "El orden mental del proyecto",
     ["<b>Datos primero, presentación después.</b> Diseña el JSON (el “contrato”) antes de la "
      "UI; el pipeline llena ese contrato y el frontend solo lo pinta. Ese desacople es lo que "
      "permite cambiar el motor de traducción (FreeDict, MT, LLM) sin tocar la interfaz."])

# --- tabla final de recursos troncales ---
h2("Recursos troncales (para tener a mano)")
tabla([
    ["Tema", "Recurso principal"],
    ["JavaScript", "javascript.info"],
    ["React", "react.dev/learn"],
    ["Enrutado", "reactrouter.com"],
    ["Pruebas", "vitest.dev"],
    ["Bundler", "vite.dev/guide"],
    ["spaCy / PLN", "course.spacy.io/es (curso gratis)"],
    ["Diccionarios", "freedict.org"],
    ["MT", "huggingface.co/docs/transformers"],
    ["Textos", "gutenberg.org"],
    ["Despliegue", "docs.netlify.com"],
], [4.2 * cm, 12.2 * cm])

story.append(Spacer(1, 0.3 * cm))
story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL))
story.append(Paragraph(
    "Acompaña este plan con el documento “Documentación técnica”, que describe cómo está "
    "resuelto cada punto en el proyecto <i>indescifrable</i>.", S["small"]))


def _pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
    canvas.drawString(2 * cm, 1.2 * cm, "Plan de aprendizaje — Plataforma de idiomas")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(SALIDA), pagesize=A4,
    leftMargin=2.3 * cm, rightMargin=2.3 * cm, topMargin=2 * cm, bottomMargin=1.8 * cm,
    title="Plan de aprendizaje — Plataforma de idiomas", author="Proyecto indescifrable",
)
doc.build(story, onFirstPage=_pie, onLaterPages=_pie)
print(f"PDF generado: {SALIDA}  ({SALIDA.stat().st_size // 1024} KB)")
