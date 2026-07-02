# -*- coding: utf-8 -*-
"""Genera docs/documentacion-repaso.pdf: documentación técnica de la Sección 2
(repaso espaciado): motor SM-2, modelo de conocimiento, repaso previo,
Leitner como cadena de Markov y la simulación comparativa.

Uso:  PYTHONUTF8=1 python docs/generar_doc_repaso.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, PageBreak)

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).with_name("documentacion-repaso.pdf")

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
story.append(Paragraph("Sección 2 — Repaso espaciado", STIT))
story.append(Paragraph("Documentación técnica: motor SM-2, modelo de conocimiento, "
                       "repaso previo y comparación con Leitner", SSUB))
story.append(Spacer(1, 0.7 * cm))
story.append(HRFlowable(width="55%", thickness=1, color=AZUL))
story.append(Spacer(1, 0.5 * cm))

h1("1. Qué resuelve esta sección")
p("La Sección 2 convierte la <b>bolsa de palabras</b> (lo que el usuario guarda mientras lee) "
  "en un sistema de estudio: cada palabra lleva un estado de <b>repetición espaciada</b> que "
  "decide cuándo volver a preguntarla. En producción la programación la gobierna <b>SM-2</b> "
  "(SuperMemo-2); <b>Leitner</b> se modela como cadena de Markov y se compara con SM-2 por "
  "simulación, fuera de producción. Además, un <b>modelo de conocimiento</b> estima qué "
  "palabras de una lectura el usuario probablemente no conoce y se las presenta como "
  "<b>repaso previo</b> antes del texto.")
p("Decisiones de producto (fijadas con el usuario): SM-2 único en la UI para estandarizar la "
  "experiencia; calificación en 4 niveles estilo Anki; tarjeta palabra → traducción "
  "(reconocimiento); repaso previo saltable con tope por nivel (5 / 12 / 20 por capítulo).")

h1("2. Mapa de archivos")
tabla([
    ["Pieza", "Archivo", "Qué contiene"],
    ["Motor SM-2", "src/engine/srs.js (+ .test)",
     "Recurrencia SM-2, sesión de repaso, resumen; puro, tiempo inyectado"],
    ["Modelo de conocimiento", "src/engine/conocimiento.js (+ .test)",
     "P(conocer) por palabra y selección de candidatas al repaso previo"],
    ["Motor Leitner + Markov", "src/engine/leitner.js (+ .test)",
     "5 cajas, matriz de transición, estacionaria, tiempos de llegada, tasa"],
    ["Tokenizador", "src/engine/tokenizar.js",
     "Regex Unicode compartido por Lector y modelo (mismas palabras)"],
    ["Persistencia", "src/engine/almacenamiento.js",
     "localStorage: bolsa.v1, conocidas.v1, repasoPrevio.v1"],
    ["UI sesión de repaso", "src/secciones/repaso/Repaso.jsx",
     "Ruta /repaso: cola vencidas+nuevas, tarjeta, 4 niveles"],
    ["UI repaso previo", "src/secciones/lectura/RepasoPrevio.jsx",
     "Fichas antes del texto; SM-2 real para bolsa, estudio para nuevas"],
    ["Botones compartidos", "src/secciones/repaso/BotonesCalificacion.jsx",
     "4 niveles con vista previa del intervalo resultante"],
    ["Frecuencias del corpus", "pipeline/frecuencias.py",
     "Emite src/data/frecuencias.json (conteo por lema, vía léxico)"],
    ["Simulación", "simulacion/comparar.mjs",
     "Alumno sintético; compara SM-2 vs Leitner sobre los motores reales"],
], [3.3 * cm, 5.9 * cm, 7.2 * cm])

h1("3. El motor SM-2")
p("El estado SRS vive <b>dentro de cada entrada de la bolsa</b> bajo la clave <font face='Courier'>srs</font>; "
  "una entrada sin <font face='Courier'>srs</font> es una palabra nueva. El módulo es puro: el instante "
  "<font face='Courier'>ahora</font> se inyecta siempre como ISO string, así los tests y la simulación son "
  "deterministas y el mismo código corre en producción y en la simulación.")
code("srs = { reps,        // aciertos consecutivos (n de SM-2)\n"
     "        ef,          // factor de facilidad (suelo 1.3)\n"
     "        intervalo,   // días hasta el próximo repaso\n"
     "        vencimiento, // ISO: cuándo vuelve a estar pendiente\n"
     "        repasos, fallos }   // estadística acumulada")
h2("3.1 Recurrencia")
code("EF' = max(1.3, EF + 0.1 − (5−q)·(0.08 + (5−q)·0.02))\n"
     "I(1) = 1,  I(2) = 6,  I(n) = round(I(n−1)·EF)     si q ≥ 3\n"
     "I = 0 (repetir hoy), n = 0                        si q &lt; 3")
p("Los 4 botones de la UI mapean a la calidad q: <b>Otra vez</b>=2, <b>Difícil</b>=3, "
  "<b>Bien</b>=4, <b>Fácil</b>=5. Con q&lt;3 la palabra vuelve al principio y se recicla al "
  "final de <i>la misma sesión</i> (vencimiento = ahora). EF se actualiza en toda respuesta, "
  "también en fallos, con suelo 1.3; nótese que q=4 deja EF exactamente igual "
  "(+0.1 − 1·0.10 = 0), por eso una palabra siempre calificada «Bien» mantiene EF 2.5.")
h2("3.2 Sesión")
p("<font face='Courier'>seleccionarSesion</font> construye la cola: primero las vencidas (la más atrasada "
  "primero), después las nuevas por orden de incorporación con tope (10 por defecto). Una "
  "palabra sin traducción al español no es repasable (no hay reverso). El vencimiento es "
  "<b>24 horas rodantes</b> desde la calificación, no medianoche como Anki: si repasas a las "
  "23:00 con intervalo 1, vence mañana a las 23:00; no hay reloj ni notificación, se compara "
  "el timestamp al abrir /repaso o la Bolsa.")

h1("4. El modelo de conocimiento")
p("Estima P(conocer) por palabra (id = <font face='Courier'>idioma:lemma</font>), por casos:")
tabla([
    ["Caso", "P(conocer)", "Racional"],
    ["Marcada «ya la conocía»", "0.95", "El usuario lo afirmó (persistido en conocidas.v1)"],
    ["En bolsa con estado SRS", "R = e^(−t/S)",
     "Retrievability: t = días desde el último repaso (= vencimiento − intervalo, "
     "recuperable del estado sin campos extra); S = max(intervalo, 0.5)"],
    ["En bolsa sin repasar", "0.2", "La guardó precisamente porque no la conocía"],
    ["Nunca vista", "σ((zipf − 3.0)/0.7)",
     "Prior logístico sobre la escala Zipf del corpus propio; "
     "zipf = log10(conteo/total·10<super>6</super>). Sin conteo: 0.1"],
], [4.2 * cm, 3.6 * cm, 8.6 * cm])
p("Con el corpus actual (~30.300 tokens en alemán): «und» (993 apariciones) → zipf ≈ 4.5 → "
  "P ≈ 0.9; un hapax → zipf ≈ 1.5 → P ≈ 0.1. Las frecuencias las emite "
  "<font face='Courier'>pipeline/frecuencias.py</font> reutilizando el mapa forma→lemma del léxico (no "
  "necesita spaCy) y respetando los overrides por lectura (p. ej. «nahm» → annehmen).")
h2("4.1 Candidatas al repaso previo")
p("Tokens únicos del cuerpo de la lectura, resueltos a lema (override de la lectura > léxico "
  "global), deduplicados por id, <b>solo con traducción al español</b> (excluye de paso los "
  "nombres propios), con P &lt; 0.7, ordenados por P ascendente y recortados al tope del "
  "nivel: principiante 5, intermedio 12, avanzado 20 por parte. En <i>Die Verwandlung</i> la "
  "primera candidata que produce el modelo es «Ungeziefer» — exactamente el hapax que debe "
  "proponer.")

h1("5. El repaso previo (flujo de UI)")
p("Al abrir una lectura en idioma extranjero, el Lector carga léxico y frecuencias (chunks "
  "dinámicos, fuera del bundle inicial), calcula las candidatas y, si hay alguna y no se "
  "mostró hoy para esa lectura, interpone <font face='Courier'>RepasoPrevio</font>. Dos tipos de ficha: si la "
  "palabra ya está en la bolsa, tarjeta SM-2 <i>real</i> (voltear + 4 niveles, califica el "
  "estado de verdad); si es nueva, ficha de estudio con ambas caras y dos salidas: "
  "«Ya la conocía» (a conocidas.v1, no vuelve) o «A la bolsa» (entra con origen "
  "<font face='Courier'>'previo'</font> y el SM-2 la programa). Siempre saltable («Ir al texto →»); al "
  "terminar o saltar se registra la fecha en repasoPrevio.v1 (máx. 1 vez/día/lectura).")
tabla([
    ["Clave localStorage", "Contenido"],
    ["bolsa.v1", "Array de entradas; el estado srs vive dentro de cada entrada"],
    ["conocidas.v1", "Array de ids marcados «ya la conocía»"],
    ["repasoPrevio.v1", "Mapa lecturaId → fecha ISO del último previo mostrado"],
    ["lecturas.completadas.v1", "Progreso de lectura (Sección 1)"],
], [5.5 * cm, 10.9 * cm])

h1("6. Leitner como cadena de Markov")
p("Leitner (5 cajas, intervalos I = [1, 2, 4, 8, 16] días): al acertar se sube de caja, al "
  "fallar se vuelve a la 1. Si la probabilidad de acierto p es constante, la sucesión de "
  "cajas es una cadena de Markov con matriz P[i][i+1] = p y P[i][1] = 1−p (techo en la 5). "
  "De ahí salen los resultados analíticos (implementados y testeados en "
  "<font face='Courier'>engine/leitner.js</font>):")
code("π = πP                    distribución estacionaria (iteración de potencias)\n"
     "E[repasos hasta caja 5] = Σ_{j=1..4} p^(−j)      (racha de 4 aciertos)\n"
     "E[días hasta caja 5]:  d_i = I_i + p·d_{i+1} + (1−p)·d_1,  d_5 = 0\n"
     "tasa en régimen = 1 / Σ_i π_i·I_i   repasos/día/palabra")
p("Con p = 0.9: ≈ 5.24 repasos y ≈ 18.1 días para llegar a la caja 5, y en régimen una "
  "palabra consume ≈ 0.08 repasos/día. El detalle numérico y su contraste con la simulación "
  "están en <b>metricas-repaso.pdf</b>.")

h1("7. La simulación comparativa")
p("<font face='Courier'>simulacion/comparar.mjs</font> (Node, <font face='Courier'>npm run simular</font>) enfrenta los dos "
  "planificadores <b>sobre los motores reales del repo</b> con un alumno sintético de curva "
  "de olvido exponencial P(recordar tras Δ) = e^(−Δ/S): al acertar S crece (S·g), al fallar "
  "se contrae (max(S0, 0.5·S)). Mismo alumno (misma dificultad, S0 y g por palabra) bajo "
  "cada planificador; 480 palabras (8/día durante 60 días), 150 días de horizonte, RNG "
  "determinista (mulberry32, semilla 42). Contabilidad fiel a cada método: un fallo en SM-2 "
  "cuesta 2 presentaciones (falla + reciclada en sesión, como la UI); en Leitner, 1 (baja de "
  "caja y espera). Salida: <font face='Courier'>docs/datos-simulacion.json</font>, que consume el generador de "
  "métricas.")

h1("8. Decisiones y trampas")
tabla([
    ["Tema", "Decisión / trampa"],
    ["Identidad de palabra", "id = idioma:lemma (normalizado); los verbos separables se "
     "identifican por su lema reconstruido (annehmen), no por la forma (nahm)"],
    ["EF con «Bien»", "q=4 deja EF sin cambio por diseño de SM-2; no es un bug"],
    ["Vencimiento", "24 h rodantes desde la calificación; no hay corte a medianoche"],
    ["Navegación entre lecturas", "El previo guarda paraId (a qué lectura pertenece): un "
     "render intermedio al navegar mostraba fichas de la lectura anterior y rompía la cola"],
    ["Peso del bundle", "lexico.json (~324 KB) y frecuencias.json (~72 KB) son chunks de "
     "import dinámico; no entran en el bundle inicial"],
    ["Calibración del alumno", "Con e^(−t/S), recordar al 90% exige S ≈ 9.5·Δ; S0 ~ U(6,16) "
     "días y g ≈ 2.2–3.6 dan precisión de repaso ~80-90%, como los SRS reales"],
    ["Python + umlauts", "Siempre PYTHONUTF8=1 y ensure_ascii=False (regla del repo)"],
], [4.2 * cm, 12.2 * cm])

h1("9. Cómo regenerar cada artefacto")
code("python pipeline/frecuencias.py        # src/data/frecuencias.json\n"
     "npm test                              # 49 tests del engine\n"
     "npm run simular                       # docs/datos-simulacion.json\n"
     "python docs/generar_doc_repaso.py     # este PDF\n"
     "python docs/generar_metricas_repaso.py\n"
     "python docs/generar_ruta_repaso.py")

doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, topMargin=1.6 * cm,
                        bottomMargin=1.6 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
                        title="Sección 2 — Repaso espaciado (documentación técnica)")
doc.build(story)
print(f"-> {SALIDA}")
