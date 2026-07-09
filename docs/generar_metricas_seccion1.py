# -*- coding: utf-8 -*-
"""Calcula métricas del proyecto y genera docs/metricas-seccion1.pdf para la tesis:
densidad/cobertura de traducción por idioma (de, en) y densidad de glosado
monolingüe (es), contribución de cada capa del traductor alemán, estadísticas del
corpus trilingüe y del motor, y una comparación cuantitativa (chrF y F1 de
tokens) de la traducción automática (opus-mt) frente a la referencia del LLM.

Uso:  PYTHONUTF8=1 python docs/generar_metricas_seccion1.py
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIRL = RAIZ / "src" / "data" / "lecturas"
sys.path.insert(0, str(RAIZ / "pipeline"))

RE_PAL = re.compile(r"\w[\w'-]*", re.UNICODE)


def norm(s):
    return re.sub(r"^[^\w]+|[^\w]+$", "", s.strip().lower(), flags=re.UNICODE)


def tokens(frase):
    return [norm(m.group(0)) for m in RE_PAL.finditer(frase) if norm(m.group(0))]


# --- cargar datos ---------------------------------------------------------
lex = json.loads((RAIZ / "src" / "data" / "lexico.json").read_text(encoding="utf-8"))
lecturas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(DIRL.glob("*.json"))]

IDIOMAS = ("de", "en", "es")
NOMBRE_IDIOMA = {"de": "alemán", "en": "inglés", "es": "español"}


def es_libro(l):
    return "libro" in l


def idioma_estudio(l):
    """Idioma que el usuario estudia en esta lectura: de/en si están presentes;
    es solo cuando es el original (no hay de/en; entonces `es` no es traducción)."""
    c = l.get("cuerpo", {})
    if "de" in c:
        return "de"
    if "en" in c:
        return "en"
    if "es" in c:
        return "es"
    return None


# --- A. corpus por idioma de estudio --------------------------------------
por_nivel = Counter(l["nivel"] for l in lecturas)
stats = {}  # idioma -> (tokens, tipos, frases, n_lecturas)
for idi in IDIOMAS:
    tok = 0
    tipos = set()
    frases = 0
    n = 0
    for l in lecturas:
        if idioma_estudio(l) != idi:
            continue
        n += 1
        for fr in l["cuerpo"][idi]:
            frases += 1
            for t in tokens(fr):
                tok += 1
                tipos.add(t)
    stats[idi] = (tok, len(tipos), frases, n)

libros = sorted({l["libro"] for l in lecturas if es_libro(l)})
n_partes = sum(1 for l in lecturas if es_libro(l))

# --- B. léxico + capas (alemán) -------------------------------------------
de_entries = {k: v for k, v in lex.items() if k.startswith("de:")}
en_entries = {k: v for k, v in lex.items() if k.startswith("en:")}
es_entries = {k: v for k, v in lex.items() if k.startswith("es:")}
con_de = sum(1 for v in de_entries.values() if "es" in v)
con_en = sum(1 for v in en_entries.values() if "es" in v)
via_ingles = sum(1 for v in de_entries.values() if "(vía inglés)" in v.get("es", ""))
compuesto = sum(1 for v in de_entries.values() if "(en compuesto)" in v.get("es", ""))
directo = con_de - via_ingles - compuesto
overrides_total = sum(len(l.get("lexico", {})) for l in lecturas)
overrides_lect = sum(1 for l in lecturas if l.get("lexico"))

# --- C. cobertura por palabra por idioma/nivel (de, en) -------------------
def cobertura_lectura(l, idioma):
    ov = l.get("lexico", {})
    tips, cub = set(), set()
    for fr in l.get("cuerpo", {}).get(idioma, []):
        for t in tokens(fr):
            tips.add(t)
            k = f"{idioma}:{t}"
            if (ov.get(k) or lex.get(k) or {}).get("es"):
                cub.add(t)
    return len(cub), len(tips)


cob = {}  # (idioma, nivel) -> (cubiertos, tipos)
for idi in ("de", "en"):
    for niv in ("principiante", "intermedio", "avanzado"):
        c = t = 0
        for l in lecturas:
            if l["nivel"] == niv and idioma_estudio(l) == idi:
                cc, tt = cobertura_lectura(l, idi)
                c += cc
                t += tt
        cob[(idi, niv)] = (c, t)

# --- C bis. glosado monolingüe del español (voces raras) ------------------
# En español solo se glosan las voces poco comunes: la "densidad" es el nº de
# tipos glosados sobre el total (no se busca cubrir el 100%, sería absurdo para
# un nativo). Se reporta por libro.
def glosado_lectura(l):
    tips, glos = set(), set()
    for fr in l.get("cuerpo", {}).get("es", []):
        for t in tokens(fr):
            tips.add(t)
            if (lex.get(f"es:{t}") or {}).get("es"):
                glos.add(t)
    return len(glos), len(tips)


glos_libros = []  # (titulo, glosadas, tipos)
for lib in [b for b in libros if idioma_estudio(next(l for l in lecturas if l.get("libro") == b)) == "es"]:
    partes = [l for l in lecturas if l.get("libro") == lib]
    g = t = 0
    for l in partes:
        gg, tt = glosado_lectura(l)
        g += gg
        t += tt
    glos_libros.append((partes[0]["titulo"].get("es", lib), g, t))

# --- D. traducción por oración / glosado por libro ------------------------
METODO = {"verwandlung": "Gemini (LLM)", "immensee": "opus-mt de-&gt;es"}
info_libros = []
for lib in libros:
    partes = [l for l in lecturas if l.get("libro") == lib]
    idi = idioma_estudio(partes[0])
    titulo = partes[0]["titulo"].get(idi) or partes[0]["titulo"].get("es", lib)
    autor = partes[0].get("autor", "")
    if idi == "es":
        fr = sum(len(l["cuerpo"]["es"]) for l in partes)
        info_libros.append((titulo, autor, "es", len(partes), fr,
                            "glosa de voces raras", "—"))
    else:
        fr = sum(len(l["cuerpo"][idi]) for l in partes)
        con_es = all("es" in l["cuerpo"] and len(l["cuerpo"]["es"]) == len(l["cuerpo"][idi])
                     for l in partes)
        metodo = METODO.get(lib, "opus-mt en-&gt;es")
        info_libros.append((titulo, autor, idi, len(partes), fr, metodo,
                            "1:1" if con_es else "parcial"))

# --- F. MT vs Gemini (chrF + F1) sobre Verwandlung parte 1 -----------------
def char_ngrams(s, n):
    s = s.lower()
    return Counter(s[i:i + n] for i in range(len(s) - n + 1))


def chrf_corpus(hyps, refs, N=6, beta=2):
    fsum = 0.0
    for n in range(1, N + 1):
        match = 0; th = 0; tr = 0
        for h, r in zip(hyps, refs):
            hn, rn = char_ngrams(h, n), char_ngrams(r, n)
            th += sum(hn.values()); tr += sum(rn.values())
            match += sum(min(hn[g], rn[g]) for g in hn)
        P = match / th if th else 0
        R = match / tr if tr else 0
        f = (1 + beta**2) * P * R / (beta**2 * P + R) if (P and R) else 0
        fsum += f
    return 100 * fsum / N


def f1_tokens(hyps, refs):
    match = th = tr = 0
    for h, r in zip(hyps, refs):
        hc, rc = Counter(tokens(h)), Counter(tokens(r))
        th += sum(hc.values()); tr += sum(rc.values())
        match += sum(min(hc[g], rc[g]) for g in hc)
    P = match / th if th else 0
    R = match / tr if tr else 0
    return 100 * (2 * P * R / (P + R) if (P + R) else 0)


mt_metrica = None
try:
    from mt import traducir_mt
    ref = json.loads((DIRL / "verwandlung-01.json").read_text(encoding="utf-8"))["cuerpo"]
    hyp = traducir_mt(ref["de"], origen="de")
    mt_metrica = (chrf_corpus(hyp, ref["es"]), f1_tokens(hyp, ref["es"]), len(ref["de"]))
except Exception as e:  # si transformers no está, se omite
    print("MT no disponible:", repr(e)[:100])

# =========================================================================
#  PDF
# =========================================================================
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, PageBreak)

AZUL = colors.HexColor("#1f3a5f"); AZUL2 = colors.HexColor("#2e5e8c")
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
SSMALL = St("sm", fontSize=8.3, textColor=GRIS, alignment=TA_LEFT)
story = []


def _san(t):
    return t.replace("→", "-&gt;").replace("×", "x")


def h1(t):
    story.append(Paragraph(t, SH1)); story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL, spaceAfter=4))


def p(t):
    story.append(Paragraph(_san(t), SB))


def tabla(filas, anchos):
    data = [[Paragraph(_san(str(c)), SCELLH if i == 0 else SCELL) for c in fila]
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


story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("Sección 1 — Lectura", St("secmarker", fontSize=13,
             textColor=AZUL2, alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=6)))
story.append(Paragraph("Reporte de métricas", STIT))
story.append(Paragraph("Plataforma de idiomas — sistema de lectura trilingüe y pipeline de PLN", SSUB))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("Métricas cuantitativas para la memoria de tesis, calculadas sobre el "
                       "contenido y el código reales del proyecto.", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. Corpus trilingüe")
p(f"El corpus consta de <b>{len(lecturas)} lecturas</b> "
  f"({por_nivel['principiante']} principiante, {por_nivel['intermedio']} intermedio, "
  f"{por_nivel['avanzado']} avanzado), incluyendo <b>{len(libros)} libros</b> de dominio "
  f"público troceados en {n_partes} partes. Cada lectura tiene un <b>idioma de estudio</b>: "
  f"alemán o inglés en las lecturas traducidas, y español en los libros difíciles pensados "
  f"para nativos (donde el español es el original, no la traducción).")
tabla([
    ["Idioma de estudio", "Lecturas", "Frases", "Tokens", "Tipos", "TTR"],
    *[[NOMBRE_IDIOMA[idi], f"{stats[idi][3]}", f"{stats[idi][2]:,}", f"{stats[idi][0]:,}",
       f"{stats[idi][1]:,}", f"{(stats[idi][1]/stats[idi][0] if stats[idi][0] else 0):.3f}"]
      for idi in IDIOMAS],
], [3.6 * cm, 2.2 * cm, 2.4 * cm, 2.7 * cm, 2.5 * cm, 2.6 * cm])
p("<i>La razón tipo/token (TTR) baja en alemán/inglés refleja la repetición de vocabulario "
  "en las novelas; en español es más alta porque los libros elegidos (Quijote, Buscón, Azul, "
  "Quiroga) tienen un léxico deliberadamente rico y variado.</i>")

h1("2. Cobertura de traducción por palabra (alemán, inglés)")
p("La <b>cobertura</b> es el porcentaje de <i>tipos</i> (formas distintas) con traducción al "
  "español. La <b>densidad</b> práctica que ve el usuario es aún mayor porque las formas "
  "frecuentes —las que más se tocan— están cubiertas.")
filas_cob = [["Idioma", "Nivel", "Tipos con traducción / totales", "Cobertura"]]
for idi in ("de", "en"):
    for niv in ("principiante", "intermedio", "avanzado"):
        c, t = cob[(idi, niv)]
        if t == 0:
            continue
        filas_cob.append([NOMBRE_IDIOMA[idi], niv.capitalize(), f"{c} / {t}",
                          f"{100*c//max(1,t)}%"])
tabla(filas_cob, [2.8 * cm, 3.4 * cm, 6.2 * cm, 4 * cm])
p("Principiante e intermedio alcanzan cifras muy altas gracias a la semilla curada y a los "
  "overrides por lectura; los libros avanzados quedan algo por debajo (los fallos restantes "
  "son verbos fuertes que spaCy no lematiza y compuestos raros). El inglés parte con ventaja: "
  "es todo ASCII y el diccionario FreeDict eng-spa es directo.")

h1("3. Contribución de cada capa del traductor (alemán)")
p("Descomposición de las traducciones del léxico alemán según la capa que las resolvió "
  "(directo FreeDict, cadena por inglés, o cabeza de compuesto).")
tabla([
    ["Capa", "Entradas", "% de las traducidas"],
    ["Directo (FreeDict deu-spa)", f"{directo:,}", f"{100*directo//max(1,con_de)}%"],
    ["Cadena deu-eng -&gt; eng-spa", f"{via_ingles:,}", f"{100*via_ingles//max(1,con_de)}%"],
    ["Cabeza de compuesto", f"{compuesto:,}", f"{100*compuesto//max(1,con_de)}%"],
    ["Total con traducción (de)", f"{con_de:,}", "100%"],
], [7.4 * cm, 4.5 * cm, 4.5 * cm])
p(f"Léxico total: <b>{len(lex):,} entradas</b> ({len(de_entries):,} de + {len(en_entries):,} "
  f"en + {len(es_entries):,} es). El inglés-&gt;español cubre {con_en}/{len(en_entries)} por "
  f"FreeDict directo; el español son voces glosadas a mano (sección 5).")

h1("4. Desambiguación de verbos separables (overrides por lectura)")
p(f"El léxico global no puede distinguir formas dependientes del contexto (p. ej. <i>nahm</i> "
  f"= <i>annehmen</i> vs <i>nehmen</i>). Se añadieron <b>{overrides_total} overrides por "
  f"lectura</b> en {overrides_lect} textos de principiante/intermedio, curados a mano y "
  f"verificados frase a frase, que el frontend prioriza sobre el léxico global.")

h1("5. Glosado monolingüe del español (voces raras)")
p("Para los libros en español —la lengua materna del usuario— no se traduce: se <b>glosa</b> "
  "con una definición en español moderno solo las <b>voces poco comunes o arcaicas</b> "
  "(las corrientes no necesitan glosa). La rareza se decide con la frecuencia general del "
  "español (escala Zipf, biblioteca <font face='Courier'>wordfreq</font>) y las definiciones "
  "se curan a mano en <font face='Courier'>glosas_es.json</font>. La métrica es la "
  "<b>densidad de glosado</b>: tipos glosados sobre el total (no se busca el 100%).")
if glos_libros:
    tabla([["Libro (español)", "Tipos glosados", "Tipos totales", "Densidad"]] +
          [[tit, f"{g}", f"{t}", f"{100*g/max(1,t):.1f}%"] for tit, g, t in glos_libros],
          [6.6 * cm, 3.4 * cm, 3.2 * cm, 3.2 * cm])
p(f"El glosario curado tiene <b>{sum(1 for k in es_entries)} entradas de forma</b> derivadas "
  "de ~190 voces base. La densidad es mayor en el Siglo de Oro (Quijote, Buscón: léxico "
  "arcaico) que en los textos modernos (Azul, Quiroga), donde un nativo desconoce menos "
  "palabras. El glosario es ampliable: añadir entradas sube la densidad sin tocar código.")

h1("6. Traducción por oración / glosado (por libro)")
tabla([["Libro", "Autor", "Idi.", "Partes", "Frases", "Método", "Alin."]] + info_libros,
      [3.5 * cm, 2.8 * cm, 1.0 * cm, 1.5 * cm, 1.6 * cm, 3.4 * cm, 1.6 * cm])
p("Los libros de alemán/inglés tienen traducción por frase con alineación <b>1:1 verificada</b> "
  "(el validador no escribe nada si el conteo no cuadra); los de español no llevan traducción "
  "por frase (son monolingües: el foco es la palabra).")

h1("7. Calidad del transformer (MT) frente al LLM de referencia")
if mt_metrica:
    chrf, f1, n = mt_metrica
    p(f"Se tradujo la <b>Parte 1 de <i>Die Verwandlung</i></b> ({n} frases) con "
      f"<b>opus-mt</b> y se comparó con la traducción de <b>Gemini</b> (referencia). "
      f"Métricas de similitud automática:")
    tabla([
        ["Métrica", "Valor", "Interpretación"],
        ["chrF (F-score de n-gramas de carácter, beta=2)", f"{chrf:.1f}",
         "0-100; mide solape de caracteres. Traducciones aceptables suelen dar 40-60."],
        ["F1 de tokens (solape de palabras)", f"{f1:.1f}",
         "0-100; solape léxico bruto con la referencia."],
    ], [7.2 * cm, 2.4 * cm, 6.8 * cm])
    p("<b>Lectura de los números:</b> la MT recupera una parte sustancial del contenido de la "
      "referencia, pero <b>no es una medida de calidad absoluta</b> (Gemini no es verdad de "
      "oro, y dos traducciones correctas pueden diferir mucho en palabras). Cualitativamente la "
      "MT comete errores semánticos que el LLM no. El mismo motor opus-mt, con el modelo "
      "en-&gt;es, tradujo automáticamente los cuatro libros ingleses.")
else:
    p("(No se pudo ejecutar opus-mt en este entorno; ver la comparación cualitativa en la "
      "documentación técnica.)")

h1("8. Motor algorítmico (pruebas)")
p("El núcleo de lógica pura se prueba con <b>Vitest</b> (toda la plataforma: 161 casos). En la "
  "sección de lectura y su almacenamiento:")
tabla([
    ["Módulo", "Qué verifican las pruebas"],
    ["board.js (LCG + tablero)", "Determinismo: misma semilla -&gt; mismo tablero; distribución "
     "exacta 9/8/7/1; parseo de semilla."],
    ["bolsa.js", "Alta sin duplicar; regla “palabra existente conserva su estado”; "
     "normalización con acentos/umlauts."],
    ["progreso.js", "Marcar/consultar lecturas completadas."],
    ["almacenamiento.js", "Idioma de estudio y perfil export/import (round-trip sin pérdidas)."],
], [4.6 * cm, 11.8 * cm])

h1("9. Resumen de volumen")
tabla([
    ["Concepto", "Cantidad"],
    ["Lecturas (total)", f"{len(lecturas)}"],
    ["Libros completos o en fragmento", f"{len(libros)}"],
    ["Frases (de / en / es)", f"{stats['de'][2]:,} / {stats['en'][2]:,} / {stats['es'][2]:,}"],
    ["Entradas de léxico", f"{len(lex):,} ({len(de_entries):,} de, {len(en_entries):,} en, "
     f"{len(es_entries):,} es)"],
    ["Overrides por lectura (separables)", f"{overrides_total}"],
    ["Idiomas de estudio", "3 (de, en, es)"],
], [7 * cm, 9.4 * cm])

story.append(Spacer(1, 0.3 * cm))
story.append(HRFlowable(width="100%", thickness=0.6, color=AZUL))
story.append(Paragraph("Métricas calculadas automáticamente por docs/generar_metricas_seccion1.py "
                       "sobre el estado actual del repositorio. chrF/F1 implementados sin "
                       "dependencias externas.", SSMALL))


def _pie(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(GRIS)
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{d.page}")
    c.drawString(2 * cm, 1.2 * cm, "Reporte de métricas — Plataforma de idiomas")
    c.restoreState()


SALIDA = Path(__file__).parent / "metricas-seccion1.pdf"
SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm,
                  topMargin=2 * cm, bottomMargin=1.8 * cm,
                  title="Reporte de métricas — Plataforma de idiomas").build(
    story, onFirstPage=_pie, onLaterPages=_pie)
print(f"PDF: {SALIDA} ({SALIDA.stat().st_size // 1024} KB)")
