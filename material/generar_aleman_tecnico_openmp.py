# -*- coding: utf-8 -*-
"""Genera material/aleman-tecnico-openmp-cap1.pdf: cuaderno bilingüe (alemán | español)
para aprender alemán técnico con los temas del capítulo 1 («Einführung», pp. 1-21) de
S. Hoffmann y R. Lienhart, «OpenMP. Eine Einführung in die parallele Programmierung
mit C/C++», Springer 2008.

El texto es PROPIO (redactado para el estudio, con ejemplos propios): no traduce ni
reproduce el libro, que tiene derechos de autor. Cada apartado remite a las páginas del
original, y el glosario indica en qué página aparece cada término.

Partes: 1) texto bilingüe fila a fila, 2) glosario (sustantivos con género y plural;
verbos con presente, Präteritum, Partizip II y preposición), 3) estructuras típicas del
alemán técnico y trampas frecuentes.

Uso:  PYTHONUTF8=1 python material/generar_aleman_tecnico_openmp.py
"""
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Preformatted, KeepTogether,
                                CondPageBreak)

SALIDA = Path(__file__).with_name("aleman-tecnico-openmp-cap1.pdf")

# ---------------------------------------------------------------- fuentes (σ, →, ≤, «»)
# Las fuentes base de PDF no traen griego ni flechas: se busca una TTF con esos glifos
# (Liberation en Linux, Times/Arial/Courier New en Windows o macOS).
L = "/usr/share/fonts/truetype/liberation/"
W = "C:/Windows/Fonts/"
M = "/System/Library/Fonts/Supplemental/"
CANDIDATAS = {
    "Serif": [[L + "LiberationSerif-Regular.ttf", L + "LiberationSerif-Bold.ttf",
               L + "LiberationSerif-Italic.ttf", L + "LiberationSerif-BoldItalic.ttf"],
              [W + "times.ttf", W + "timesbd.ttf", W + "timesi.ttf", W + "timesbi.ttf"],
              [M + "Times New Roman.ttf", M + "Times New Roman Bold.ttf",
               M + "Times New Roman Italic.ttf", M + "Times New Roman Bold Italic.ttf"]],
    "Sans": [[L + "LiberationSans-Regular.ttf", L + "LiberationSans-Bold.ttf",
              L + "LiberationSans-Italic.ttf", L + "LiberationSans-BoldItalic.ttf"],
             [W + "arial.ttf", W + "arialbd.ttf", W + "ariali.ttf", W + "arialbi.ttf"],
             [M + "Arial.ttf", M + "Arial Bold.ttf", M + "Arial Italic.ttf",
              M + "Arial Bold Italic.ttf"]],
    "Mono": [[L + "LiberationMono-Regular.ttf", L + "LiberationMono-Bold.ttf",
              L + "LiberationMono-Italic.ttf", L + "LiberationMono-BoldItalic.ttf"],
             [W + "cour.ttf", W + "courbd.ttf", W + "couri.ttf", W + "courbi.ttf"],
             [M + "Courier New.ttf", M + "Courier New Bold.ttf", M + "Courier New Italic.ttf",
              M + "Courier New Bold Italic.ttf"]],
}
BASE14 = {"Serif": ("Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic"),
          "Sans": ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique"),
          "Mono": ("Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique")}
CMAP = None  # glifos de la Serif registrada (para verificar el texto)


def registrar_fuentes():
    global CMAP
    nombres = {}
    for fam, opciones in CANDIDATAS.items():
        rutas = next((r for r in opciones if all(Path(p).exists() for p in r)), None)
        if rutas is None:
            print(f"AVISO: sin TTF para {fam}; se usa la fuente base (sin σ ni flechas).")
            nombres[fam] = BASE14[fam]
            continue
        n = [fam, fam + "-B", fam + "-I", fam + "-BI"]
        for nombre, ruta in zip(n, rutas):
            pdfmetrics.registerFont(TTFont(nombre, ruta))
        pdfmetrics.registerFontFamily(fam, normal=n[0], bold=n[1], italic=n[2], boldItalic=n[3])
        nombres[fam] = tuple(n)
        if fam == "Serif":
            CMAP = pdfmetrics.getFont(n[0]).face.charToGlyph
    return nombres


F = registrar_fuentes()
SERIF, SERIF_B = F["Serif"][0], F["Serif"][1]
SANS, SANS_B = F["Sans"][0], F["Sans"][1]
MONO = F["Mono"][0]

# ---------------------------------------------------------------- estilos
AZUL = colors.HexColor("#1f3a5f"); AZUL2 = colors.HexColor("#2e5e8c")
GRIS = colors.HexColor("#555555"); GRISC = colors.HexColor("#f0f0f0")
LINEA = colors.HexColor("#d5dbe3"); FONDO_DE = colors.HexColor("#f4f7fb")
DER = colors.HexColor("#1f5fa8"); DIE = colors.HexColor("#b03030"); DAS = colors.HexColor("#2e7d32")
COLOR_ARTICULO = {"der": DER, "die": DIE, "das": DAS}

MARGEN = 1.8 * cm
ANCHO = A4[0] - 2 * MARGEN
St = ParagraphStyle
STIT = St("tit", fontName=SANS_B, fontSize=25, leading=30, textColor=AZUL, alignment=TA_CENTER)
SSUB = St("sub", fontName=SANS, fontSize=12.5, leading=17, textColor=GRIS, alignment=TA_CENTER)
SH1 = St("h1", fontName=SANS_B, fontSize=15, leading=19, textColor=AZUL, spaceBefore=4,
         spaceAfter=6)
SH2 = St("h2", fontName=SANS_B, fontSize=11.5, leading=14.5, textColor=AZUL2, spaceBefore=10,
         spaceAfter=1)
SREF = St("ref", fontName=SANS, fontSize=8.2, leading=10.5, textColor=GRIS, spaceAfter=4)
SB = St("b", fontName=SERIF, fontSize=10.3, leading=14, spaceAfter=5)
SDE = St("de", fontName=SERIF, fontSize=10, leading=13.4, textColor=colors.HexColor("#141414"))
SES = St("es", fontName=SERIF, fontSize=10, leading=13.4, textColor=colors.HexColor("#3b3b3b"))
SCAB = St("cab", fontName=SANS_B, fontSize=8.4, leading=10, textColor=colors.white)
SFORM = St("f", fontName=SERIF, fontSize=11.5, leading=15, alignment=TA_CENTER)
SCODE = St("code", fontName=MONO, fontSize=8.4, leading=10.8)
SCELL = St("c", fontName=SERIF, fontSize=9, leading=11.6)
SCELLS = St("cs", fontName=SANS, fontSize=8.3, leading=10.6, textColor=GRIS)
SCAP = St("cap", fontName=SANS, fontSize=8.3, leading=10.5, textColor=GRIS, alignment=TA_CENTER,
          spaceAfter=3)
SNUM = St("num", fontName=SERIF, fontSize=9, leading=11.6, alignment=TA_CENTER)
SCAJA = St("caja", fontName=SERIF, fontSize=10, leading=13.8, spaceAfter=4)


def md(t):
    """Marcado mínimo → XML de reportlab: `código`, **negrita**, *cursiva*, _{subíndice}."""
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"`([^`]+)`", lambda m: f'<font name="{MONO}" size="9">{m.group(1)}</font>', t)
    t = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    return t


TEXTOS = []  # todo lo que se escribe, para verificar glifos al final


def P(t, estilo):
    TEXTOS.append(t)
    return Paragraph(md(t), estilo)


# ================================================================ PARTE 1: texto bilingüe
# Tipos de fila: ("t", alemán, español) · ("code", código) · ("f", fórmula) · ("tabla",)
SECCIONES = [
    ("Was ist OpenMP?", "¿Qué es OpenMP?", "Kap. 1, S. 1–2", "cap. 1, pp. 1–2", [
        ("t", "**OpenMP** (*Open Multi-Processing*) ist ein Standard für die **parallele "
              "Programmierung** von Rechnern mit **gemeinsamem Speicher**. Er ist für die "
              "Programmiersprachen C, C++ und Fortran definiert.",
              "**OpenMP** (*Open Multi-Processing*) es un estándar para la **programación "
              "paralela** de ordenadores con **memoria compartida**. Está definido para los "
              "lenguajes de programación C, C++ y Fortran."),
        ("t", "Die Grundidee: Statt ein vorhandenes **sequenzielles** Programm neu zu "
              "schreiben, ergänzt man es an geeigneten Stellen um **Compilerdirektiven**. Diese "
              "teilen dem Compiler mit, welche Programmteile von mehreren **Threads** "
              "gleichzeitig bearbeitet werden dürfen.",
              "La idea básica: en lugar de reescribir un programa **secuencial** ya existente, "
              "se le añaden **directivas de compilador** en los lugares adecuados. Estas le "
              "indican al compilador qué partes del programa pueden ser procesadas "
              "simultáneamente por varios **hilos** (threads)."),
        ("t", "OpenMP besteht aus drei Bausteinen: den **Direktiven**, einer "
              "**Laufzeitbibliothek** mit Hilfsfunktionen und einigen **Umgebungsvariablen**, "
              "mit denen sich das Verhalten eines Programms beim Start einstellen lässt.",
              "OpenMP consta de tres componentes: las **directivas**, una **biblioteca de "
              "tiempo de ejecución** con funciones auxiliares y algunas **variables de "
              "entorno**, con las que se puede ajustar el comportamiento de un programa al "
              "arrancarlo."),
        ("t", "OpenMP ist ein **offener Standard**. Die **Spezifikation** wird vom *OpenMP "
              "Architecture Review Board* gepflegt, einem Zusammenschluss von Hardware- und "
              "Softwareherstellern sowie Forschungseinrichtungen, und steht unter "
              "www.openmp.org frei zur Verfügung.",
              "OpenMP es un **estándar abierto**. La **especificación** la mantiene el *OpenMP "
              "Architecture Review Board*, una asociación de fabricantes de hardware y software "
              "e instituciones de investigación, y está disponible libremente en "
              "www.openmp.org."),
        ("t", "*Hinweis:* Das Buch gibt den Stand von 2008 wieder (Version 2.5; Version 3.0 "
              "stand kurz bevor). Seitdem ist die Spezifikation stark gewachsen – Version 6.0 "
              "erschien 2024 –, an den Grundbegriffen dieses Kapitels hat sich aber nichts "
              "geändert.",
              "*Nota:* el libro refleja el estado de 2008 (versión 2.5; la 3.0 estaba a punto "
              "de salir). Desde entonces la especificación ha crecido mucho —la versión 6.0 "
              "apareció en 2024—, pero los conceptos básicos de este capítulo no han cambiado."),
    ]),
    ("Ein erstes Beispiel", "Un primer ejemplo", "Abschnitt 1.1, S. 2–4", "apartado 1.1, pp. 2–4", [
        ("t", "Die folgende Funktion berechnet für zwei Vektoren *x* und *y* der Länge *n* die "
              "Operation *y* ← *a*·*x* + *y* (in der Numerik unter dem Namen SAXPY bekannt):",
              "La siguiente función calcula, para dos vectores *x* e *y* de longitud *n*, la "
              "operación *y* ← *a*·*x* + *y* (conocida en cálculo numérico con el nombre de "
              "SAXPY):"),
        ("code", "void saxpy(int n, float a, const float *x, float *y)\n"
                 "{\n"
                 "    #pragma omp parallel for\n"
                 "    for (int i = 0; i < n; ++i)\n"
                 "        y[i] = a * x[i] + y[i];\n"
                 "}"),
        ("t", "Die einzelnen **Schleifendurchläufe** sind voneinander **unabhängig**: Jeder "
              "Durchlauf liest und schreibt nur die Elemente mit seinem eigenen Index *i*. "
              "Deshalb darf die **Schleife** gefahrlos **parallelisiert** werden.",
              "Las distintas **iteraciones del bucle** son **independientes** entre sí: cada "
              "iteración solo lee y escribe los elementos con su propio índice *i*. Por eso el "
              "**bucle** puede **paralelizarse** sin riesgo."),
        ("t", "Die Zeile `#pragma omp parallel for` ist eine **Direktive**. Sie weist den "
              "Compiler an, die unmittelbar folgende for-Schleife auf ein **Team** von Threads "
              "zu **verteilen**. Wie viele Threads beteiligt sind und welcher Thread welche "
              "Indizes übernimmt, regelt die **Laufzeitumgebung**; über **Klauseln** wie "
              "`num_threads` oder `schedule` lässt sich das aber auch gezielt steuern.",
              "La línea `#pragma omp parallel for` es una **directiva**. Indica al compilador "
              "que **reparta** el bucle for que la sigue inmediatamente entre un **equipo** de "
              "hilos. Cuántos hilos participan y qué hilo se encarga de qué índices lo regula el "
              "**entorno de ejecución**; pero mediante **cláusulas** como `num_threads` o "
              "`schedule` también se puede controlar de forma específica."),
        ("t", "Schon an diesem kurzen Beispiel lassen sich die wichtigsten **Eigenschaften** "
              "von OpenMP ablesen:",
              "Ya en este breve ejemplo se pueden apreciar las **características** más "
              "importantes de OpenMP:"),
        ("t", "• Hoher **Abstraktionsgrad**: Threads müssen weder erzeugt noch beendet werden – "
              "das erledigt die Laufzeitumgebung.",
              "• Alto **nivel de abstracción**: no hay que crear ni terminar los hilos; de eso "
              "se encarga el entorno de ejecución."),
        ("t", "• **Lesbarkeit**: Der parallele Code bleibt an seiner ursprünglichen Stelle "
              "stehen und muss nicht in eine eigene Thread-Funktion ausgelagert werden.",
              "• **Legibilidad**: el código paralelo se queda en su lugar original y no hay que "
              "trasladarlo a una función de hilo aparte."),
        ("t", "• **Schrittweises Vorgehen**: Man parallelisiert Schleife für Schleife und prüft "
              "nach jedem Schritt, ob die Ergebnisse noch stimmen.",
              "• **Avance gradual**: se paraleliza bucle a bucle y tras cada paso se comprueba "
              "si los resultados siguen siendo correctos."),
        ("t", "• **Rückfallebene**: Ein Compiler ohne OpenMP-Unterstützung **ignoriert** die "
              "Pragmas (allenfalls mit einer Warnung) und erzeugt ein korrektes **serielles** "
              "Programm.",
              "• **Plan de respaldo**: un compilador sin soporte de OpenMP **ignora** los "
              "pragmas (como mucho, con una advertencia) y genera un programa **serial** "
              "correcto."),
        ("t", "• **Portabilität**: Derselbe Quelltext lässt sich mit den Compilern verschiedener "
              "Hersteller und auf unterschiedlichen Plattformen übersetzen.",
              "• **Portabilidad**: el mismo código fuente se puede compilar con los "
              "compiladores de distintos fabricantes y en diferentes plataformas."),
    ]),
    ("Direktiven, Klauseln und Laufzeitbibliothek", "Directivas, cláusulas y biblioteca",
     "Abschnitt 1.1, S. 4–6", "apartado 1.1, pp. 4–6", [
        ("t", "Jede OpenMP-Direktive beginnt mit `#pragma omp`. Danach folgen der Name der "
              "Direktive und – optional – eine oder mehrere Klauseln, die ihr Verhalten genauer "
              "festlegen. Welche Klauseln zulässig sind, hängt von der jeweiligen Direktive ab.",
              "Toda directiva de OpenMP empieza por `#pragma omp`. A continuación vienen el "
              "nombre de la directiva y, opcionalmente, una o varias cláusulas que precisan su "
              "comportamiento. Qué cláusulas se admiten depende de cada directiva."),
        ("code", "#pragma omp parallel for num_threads(4)   // Direktive + Klausel · directiva + cláusula"),
        ("t", "Eine Direktive gilt für die unmittelbar folgende Anweisung bzw. den unmittelbar "
              "folgenden **strukturierten Block**. Da die Pragma-Zeile mit einem "
              "**Zeilenumbruch** enden muss, steht die öffnende geschweifte Klammer eines "
              "Blocks immer in der nächsten Zeile.",
              "Una directiva se aplica a la instrucción o al **bloque estructurado** que la "
              "sigue inmediatamente. Como la línea del pragma debe terminar con un **salto de "
              "línea**, la llave de apertura de un bloque va siempre en la línea siguiente."),
        ("t", "Um die Funktionen der **Laufzeitbibliothek** zu nutzen, bindet man die "
              "**Headerdatei** `omp.h` ein. Mit ihnen fragt man Informationen ab oder nimmt "
              "Einstellungen vor: `omp_get_thread_num()` liefert zum Beispiel die Nummer des "
              "aufrufenden Threads, `omp_get_num_threads()` die Größe des aktuellen Teams.",
              "Para usar las funciones de la **biblioteca de tiempo de ejecución** se incluye "
              "el **archivo de cabecera** `omp.h`. Con ellas se consulta información o se "
              "ajustan parámetros: `omp_get_thread_num()`, por ejemplo, devuelve el número del "
              "hilo que la llama, y `omp_get_num_threads()`, el tamaño del equipo actual."),
        ("t", "**Umgebungsvariablen** wirken, ohne dass das Programm neu übersetzt werden muss. "
              "Die bekannteste ist `OMP_NUM_THREADS`: Der Aufruf `OMP_NUM_THREADS=8 ./saxpy` "
              "startet das Programm mit acht Threads pro Team.",
              "Las **variables de entorno** surten efecto sin necesidad de volver a compilar el "
              "programa. La más conocida es `OMP_NUM_THREADS`: la orden "
              "`OMP_NUM_THREADS=8 ./saxpy` ejecuta el programa con ocho hilos por equipo."),
        ("t", "Ist die OpenMP-Unterstützung eingeschaltet, definiert der Compiler das **Makro** "
              "`_OPENMP`; sein Wert ist das Datum der unterstützten Spezifikation im Format "
              "*JJJJMM*. Damit lassen sich OpenMP-spezifische Programmteile **bedingt "
              "übersetzen**, sodass der Code auch ohne OpenMP kompilierbar bleibt:",
              "Si el soporte de OpenMP está activado, el compilador define la **macro** "
              "`_OPENMP`; su valor es la fecha de la especificación soportada en formato "
              "*AAAAMM*. Así se pueden **compilar condicionalmente** las partes del programa "
              "específicas de OpenMP, de modo que el código siga compilando también sin OpenMP:"),
        ("code", "#ifdef _OPENMP\n"
                 "    #include <omp.h>\n"
                 "#else   /* Ersatz im seriellen Fall · sustituto en el caso serial */\n"
                 "    static int omp_get_thread_num(void) { return 0; }\n"
                 "#endif"),
    ]),
    ("Compiler und Übersetzung", "Compiladores y compilación", "Abschnitt 1.1.1, S. 6–7",
     "apartado 1.1.1, pp. 6–7", [
        ("t", "Die meisten verbreiteten C/C++-Compiler unterstützen OpenMP, doch die "
              "Unterstützung muss beim **Übersetzen** ausdrücklich **aktiviert** werden: bei GCC "
              "und Clang mit der Option `-fopenmp`, bei Microsoft Visual C++ mit `/openmp`.",
              "La mayoría de los compiladores de C/C++ habituales soportan OpenMP, pero el "
              "soporte debe **activarse** expresamente al **compilar**: en GCC y Clang con la "
              "opción `-fopenmp`, en Microsoft Visual C++ con `/openmp`."),
        ("code", "gcc -fopenmp -O2 saxpy.c -o saxpy          # mit OpenMP · con OpenMP\n"
                 "gcc -O2 saxpy.c -o saxpy_seriell           # ohne OpenMP · sin OpenMP"),
        ("t", "Ein praktischer Nebeneffekt: Ohne die Option entsteht aus demselben Quelltext "
              "ein rein sequenzielles Programm – eine ideale **Referenz**, um bei der "
              "**Fehlersuche** Ergebnisse zu vergleichen und bei **Zeitmessungen** den Gewinn "
              "der Parallelisierung zu bestimmen.",
              "Un efecto secundario práctico: sin la opción, del mismo código fuente sale un "
              "programa puramente secuencial, una **referencia** ideal para comparar resultados "
              "durante la **depuración** y para determinar la ganancia de la paralelización al "
              "**medir tiempos**."),
    ]),
    ("Prozesse und Threads", "Procesos e hilos", "Abschnitt 1.2.1, S. 8–10",
     "apartado 1.2.1, pp. 8–10", [
        ("t", "Ein **Prozess** ist ein Programm in Ausführung. Für jeden Prozess verwaltet das "
              "**Betriebssystem** unter anderem eine **Prozess-ID**, den **Befehlszähler**, die "
              "**Registerinhalte**, einen **Stack** für lokale Variablen und "
              "Rücksprungadressen, einen **Datenbereich** für globale Variablen und einen "
              "**Heap** für dynamisch angeforderten Speicher.",
              "Un **proceso** es un programa en ejecución. Para cada proceso, el **sistema "
              "operativo** gestiona, entre otras cosas, un **identificador de proceso** (PID), "
              "el **contador de programa**, el **contenido de los registros**, una **pila** "
              "(stack) para variables locales y direcciones de retorno, un **segmento de "
              "datos** para variables globales y un **montículo** (heap) para la memoria "
              "solicitada dinámicamente."),
        ("t", "Meist sind weit mehr Prozesse aktiv, als Prozessorkerne vorhanden sind. Der "
              "**Scheduler** des Betriebssystems teilt ihnen deshalb reihum kurze "
              "**Zeitscheiben** zu. Bei jedem Wechsel wird der Zustand des unterbrochenen "
              "Prozesses gesichert und der des nächsten wiederhergestellt – ein "
              "**Kontextwechsel** (engl. *context switch*).",
              "Normalmente hay muchos más procesos activos que núcleos de procesador. Por eso el "
              "**planificador** (scheduler) del sistema operativo les asigna por turnos breves "
              "**porciones de tiempo**. En cada cambio se guarda el estado del proceso "
              "interrumpido y se restaura el del siguiente: un **cambio de contexto** (ingl. "
              "*context switch*)."),
        ("t", "Ein **Thread** (auch **Ausführungsstrang**) ist ein eigenständiger "
              "**Kontrollfluss** innerhalb eines Prozesses. Jeder Thread hat seinen eigenen "
              "Befehlszähler, eigene Register und einen eigenen Stack. Programmcode, "
              "Datenbereich, Heap und geöffnete Dateien **teilen sich** dagegen alle Threads "
              "eines Prozesses.",
              "Un **hilo** (thread; en alemán también *Ausführungsstrang*) es un **flujo de "
              "control** independiente dentro de un proceso. Cada hilo tiene su propio contador "
              "de programa, sus propios registros y su propia pila. En cambio, el código del "
              "programa, el segmento de datos, el montículo y los archivos abiertos los "
              "**comparten** todos los hilos de un proceso."),
        ("t", "Das hat Vorteile: Threads greifen direkt auf **gemeinsame Daten** zu, und ein "
              "Kontextwechsel zwischen Threads ist **günstiger** als zwischen Prozessen, weil "
              "weniger Zustand gesichert werden muss.",
              "Esto tiene ventajas: los hilos acceden directamente a **datos compartidos**, y "
              "un cambio de contexto entre hilos es **más barato** que entre procesos, porque "
              "hay que guardar menos estado."),
        ("t", "Die gemeinsame Nutzung birgt aber auch eine Gefahr: Greifen mehrere Threads "
              "ungeschützt auf dieselbe Variable zu und schreibt mindestens einer davon, "
              "entsteht eine **Wettlaufsituation** (engl. *race condition*). Das Ergebnis "
              "hängt dann vom zufälligen zeitlichen Ablauf ab.",
              "Pero el uso compartido también entraña un peligro: si varios hilos acceden sin "
              "protección a la misma variable y al menos uno de ellos escribe, se produce una "
              "**condición de carrera** (ingl. *race condition*). El resultado depende entonces "
              "del orden temporal, que es aleatorio."),
        ("t", "OpenMP nimmt dem Programmierer die Verwaltung der Threads ab. Wie sie intern "
              "realisiert werden – unter Linux etwa meist mit **POSIX-Threads** –, braucht ihn "
              "nicht zu interessieren.",
              "OpenMP libera al programador de la gestión de los hilos. Cómo se implementan "
              "internamente —en Linux, por ejemplo, casi siempre con **hilos POSIX**— no tiene "
              "por qué interesarle."),
    ]),
    ("Parallele Hardware", "Hardware paralelo", "Abschnitt 1.2.2, S. 10–13",
     "apartado 1.2.2, pp. 10–13", [
        ("t", "Nach dem **Moore’schen Gesetz** verdoppelt sich die Zahl der **Transistoren** "
              "auf einem Chip etwa alle zwei Jahre. Lange Zeit wurden Programme dadurch ganz "
              "ohne eigenes Zutun schneller, weil gleichzeitig die **Taktfrequenz** stieg.",
              "Según la **ley de Moore**, el número de **transistores** de un chip se duplica "
              "aproximadamente cada dos años. Durante mucho tiempo, los programas se volvían más "
              "rápidos sin hacer nada, porque al mismo tiempo aumentaba la **frecuencia de "
              "reloj**."),
        ("t", "Seit Mitte der 2000er-Jahre stößt die Taktfrequenz jedoch an Grenzen, vor allem "
              "wegen der **Leistungsaufnahme** und der **Wärmeentwicklung**. Seitdem werden die "
              "zusätzlichen Transistoren für **Parallelität** genutzt: "
              "**Mehrkernprozessoren** (engl. *multicore*) vereinen mehrere "
              "**Prozessorkerne** auf einem Chip, und beim **Hyperthreading** teilen sich zwei "
              "Kontrollflüsse die **Recheneinheiten** eines Kerns.",
              "Sin embargo, desde mediados de la década de 2000 la frecuencia de reloj choca con "
              "límites, sobre todo por el **consumo de energía** y la **generación de calor**. "
              "Desde entonces, los transistores adicionales se usan para el **paralelismo**: los "
              "**procesadores multinúcleo** (ingl. *multicore*) reúnen varios **núcleos** en "
              "un chip, y con el **hyperthreading** dos flujos de control comparten las "
              "**unidades de cálculo** de un núcleo."),
        ("t", "Für die Softwareentwicklung bedeutet das: Ein sequenzielles Programm nutzt nur "
              "einen einzigen Kern. Wer die **Rechenleistung** eines modernen Rechners "
              "ausschöpfen will, muss sein Programm parallelisieren.",
              "Para el desarrollo de software esto significa: un programa secuencial solo usa "
              "un único núcleo. Quien quiera aprovechar al máximo la **potencia de cálculo** de "
              "un ordenador moderno tiene que paralelizar su programa."),
        ("t", "Rechnerarchitekturen werden häufig nach der **Flynn’schen Klassifikation** "
              "(Michael J. Flynn, 1966/1972) eingeteilt. Sie fragt, ob ein oder mehrere "
              "**Befehlsströme** auf einen oder mehrere **Datenströme** wirken:",
              "Las arquitecturas de ordenadores se clasifican a menudo según la **taxonomía de "
              "Flynn** (Michael J. Flynn, 1966/1972). Esta se pregunta si uno o varios **flujos "
              "de instrucciones** actúan sobre uno o varios **flujos de datos**:"),
        ("t", "• **SISD** (*Single Instruction, Single Data*): ein klassischer "
              "Einkernprozessor, der Befehl für Befehl auf einzelne Daten anwendet.",
              "• **SISD** (una instrucción, un dato): un procesador clásico de un solo núcleo "
              "que aplica instrucción tras instrucción a datos individuales."),
        ("t", "• **SIMD** (*Single Instruction, Multiple Data*): Ein Befehl verarbeitet viele "
              "Daten auf einmal – etwa die **Vektorbefehle** (SSE, AVX) heutiger CPUs oder "
              "**Grafikprozessoren** (GPUs).",
              "• **SIMD** (una instrucción, múltiples datos): una instrucción procesa muchos "
              "datos a la vez, como las **instrucciones vectoriales** (SSE, AVX) de las CPU "
              "actuales o los **procesadores gráficos** (GPU)."),
        ("t", "• **MISD** (*Multiple Instruction, Single Data*): in der Praxis kaum "
              "anzutreffen; als Beispiel nennt man mitunter **redundante** Steuerrechner, die "
              "dieselben Daten mehrfach verarbeiten.",
              "• **MISD** (múltiples instrucciones, un dato): apenas se da en la práctica; a "
              "veces se citan como ejemplo los ordenadores de control **redundantes**, que "
              "procesan los mismos datos varias veces."),
        ("t", "• **MIMD** (*Multiple Instruction, Multiple Data*): Mehrere Prozessoren arbeiten "
              "unabhängig voneinander an verschiedenen Daten. Dazu gehören Mehrkernprozessoren "
              "ebenso wie **Rechnerverbünde** (*Cluster*).",
              "• **MIMD** (múltiples instrucciones, múltiples datos): varios procesadores "
              "trabajan independientemente sobre datos distintos. A esta clase pertenecen tanto "
              "los procesadores multinúcleo como las **agrupaciones de ordenadores** "
              "(clústeres)."),
        ("t", "MIMD-Systeme unterscheidet man weiter nach der **Speicherorganisation**. Bei "
              "**verteiltem Speicher** hat jeder Knoten seinen eigenen Arbeitsspeicher; Daten "
              "werden als **Nachrichten** über ein Netzwerk ausgetauscht (typisch: MPI). Bei "
              "**gemeinsamem Speicher** greifen alle Kerne auf denselben **Adressraum** zu – "
              "genau das ist das Einsatzgebiet von OpenMP.",
              "Los sistemas MIMD se subdividen además según la **organización de la memoria**. "
              "Con **memoria distribuida**, cada nodo tiene su propia memoria principal; los "
              "datos se intercambian como **mensajes** a través de una red (típicamente con "
              "MPI). Con **memoria compartida**, todos los núcleos acceden al mismo **espacio "
              "de direcciones**: justo ese es el ámbito de aplicación de OpenMP."),
        ("t", "Die Ebenen lassen sich kombinieren: Ein Simulationsprogramm verteilt seine "
              "Arbeit mit MPI auf die Knoten eines Clusters, nutzt auf jedem Knoten mit OpenMP "
              "alle Kerne und setzt in jedem Kern Vektorbefehle ein.",
              "Los niveles pueden combinarse: un programa de simulación reparte su trabajo con "
              "MPI entre los nodos de un clúster, aprovecha con OpenMP todos los núcleos de cada "
              "nodo y emplea instrucciones vectoriales en cada núcleo."),
    ]),
    ("Leistung messen", "Medir el rendimiento", "Abschnitt 1.2.3, S. 13–14",
     "apartado 1.2.3, pp. 13–14", [
        ("t", "Ob sich eine Parallelisierung lohnt, beurteilt man mit zwei **Kenngrößen**. Es "
              "sei *T*_{1} die **Laufzeit** auf einem Kern und *T*_{n} die Laufzeit auf *n* "
              "Kernen. Die **Beschleunigung** (engl. *speedup*) ist dann der Quotient",
              "Si una paralelización compensa se juzga con dos **indicadores**. Sea *T*_{1} el "
              "**tiempo de ejecución** en un núcleo y *T*_{n} el tiempo en *n* núcleos. La "
              "**aceleración** (ingl. *speedup*) es entonces el cociente"),
        ("f", "*S*(*n*) = *T*_{1} / *T*_{n}"),
        ("t", "Die **Effizienz** gibt an, wie gut die eingesetzten Kerne **ausgelastet** sind. "
              "Eine Effizienz von 1 (also 100 %) bedeutet **lineare Beschleunigung**: Jeder "
              "zusätzliche Kern bringt den vollen Gewinn.",
              "La **eficiencia** indica en qué medida se **aprovechan** los núcleos empleados. "
              "Una eficiencia de 1 (es decir, del 100 %) significa **aceleración lineal**: cada "
              "núcleo adicional aporta la ganancia completa."),
        ("f", "*E*(*n*) = *S*(*n*) / *n*"),
        ("t", "Rechenbeispiel: Ein Programm benötigt auf einem Kern 120 s und auf acht Kernen "
              "20 s. Dann gilt *S*(8) = 120 / 20 = 6 und *E*(8) = 6 / 8 = 0,75. Die Kerne "
              "arbeiten also nur zu 75 % produktiv; der Rest geht durch **Verwaltungsaufwand** "
              "(engl. *overhead*), **Synchronisation** und Wartezeiten verloren.",
              "Ejemplo de cálculo: un programa necesita 120 s en un núcleo y 20 s en ocho "
              "núcleos. Entonces *S*(8) = 120 / 20 = 6 y *E*(8) = 6 / 8 = 0,75. Es decir, los "
              "núcleos solo trabajan de forma productiva un 75 %; el resto se pierde en "
              "**costes de gestión** (ingl. *overhead*), **sincronización** y tiempos de espera."),
        ("t", "In Ausnahmefällen ist sogar *S*(*n*) > *n* möglich (**superlineare "
              "Beschleunigung**). Ursache dafür sind meist **Cache-Effekte**: Mit mehr Kernen "
              "steht insgesamt mehr Cache zur Verfügung, sodass ein größerer Teil der Daten im "
              "schnellen **Zwischenspeicher** Platz findet.",
              "En casos excepcionales es posible incluso *S*(*n*) > *n* (**aceleración "
              "superlineal**). La causa suelen ser los **efectos de caché**: con más núcleos hay "
              "en total más caché disponible, de modo que una mayor parte de los datos cabe en "
              "la **memoria intermedia** rápida."),
    ]),
    ("Das Amdahl’sche Gesetz", "La ley de Amdahl", "Abschnitt 1.2.4, S. 14–16",
     "apartado 1.2.4, pp. 14–16", [
        ("t", "Gene Amdahl wies 1967 darauf hin, dass fast jedes Programm Abschnitte enthält, "
              "die sich nicht parallelisieren lassen, etwa das Einlesen der Eingabedaten. Diese "
              "**sequenziellen Anteile** begrenzen die erreichbare Beschleunigung.",
              "Gene Amdahl señaló en 1967 que casi todo programa contiene secciones que no se "
              "pueden paralelizar, como la lectura de los datos de entrada. Estas **fracciones "
              "secuenciales** limitan la aceleración alcanzable."),
        ("t", "Die Laufzeit auf einem Kern sei auf 1 **normiert**, und σ (0 ≤ σ ≤ 1) sei ihr "
              "sequenzieller Anteil. Auf *n* Kernen verkürzt sich nur der parallelisierbare "
              "Anteil 1 − σ. Daraus folgt:",
              "Normalicemos a 1 el tiempo de ejecución en un núcleo, y sea σ (0 ≤ σ ≤ 1) su "
              "fracción secuencial. En *n* núcleos solo se acorta la fracción paralelizable "
              "1 − σ. De ello se deduce:"),
        ("f", "*S*(*n*) = 1 / (σ + (1 − σ) / *n*)  ≤  1 / σ"),
        ("t", "Für *n* → ∞ **strebt** die Beschleunigung **gegen** 1/σ. Ein Programm, das zu "
              "5 % sequenziell ist, wird also selbst mit beliebig vielen Kernen höchstens "
              "20-mal schneller; mit 16 Kernen erreicht es nur *S*(16) ≈ 9,1.",
              "Para *n* → ∞, la aceleración **tiende a** 1/σ. Así, un programa que es "
              "secuencial en un 5 % será, incluso con tantos núcleos como se quiera, como mucho "
              "20 veces más rápido; con 16 núcleos solo alcanza *S*(16) ≈ 9,1."),
        ("t", "Das Gesetz setzt eine **feste Problemgröße** voraus: Dieselbe Aufgabe wird auf "
              "immer mehr Kerne verteilt. Man spricht deshalb von **starker Skalierung** "
              "(engl. *strong scaling*).",
              "La ley presupone un **tamaño de problema fijo**: la misma tarea se reparte entre "
              "cada vez más núcleos. Por eso se habla de **escalabilidad fuerte** (ingl. "
              "*strong scaling*)."),
    ]),
    ("Das Gustafson’sche Gesetz", "La ley de Gustafson", "Abschnitt 1.2.5, S. 16–21",
     "apartado 1.2.5, pp. 16–21", [
        ("t", "John Gustafson hielt 1988 dagegen, dass man mit mehr Kernen in der Praxis selten "
              "dieselbe Aufgabe schneller löst, sondern eine **größere** Aufgabe in derselben "
              "Zeit – zum Beispiel eine Simulation auf einem feineren **Gitter**. Der "
              "sequenzielle Aufwand bleibt dabei meist gleich, während der parallele mit der "
              "**Problemgröße** wächst.",
              "John Gustafson objetó en 1988 que, en la práctica, con más núcleos rara vez se "
              "resuelve más rápido la misma tarea, sino una tarea **mayor** en el mismo tiempo, "
              "por ejemplo una simulación sobre una **malla** más fina. El esfuerzo secuencial "
              "suele mantenerse igual, mientras que el paralelo crece con el **tamaño del "
              "problema**."),
        ("t", "Misst man die Anteile auf dem Parallelrechner selbst – σ sei jetzt der "
              "sequenzielle Anteil der Laufzeit auf *n* Kernen –, so ergibt sich die "
              "**skalierte Beschleunigung**:",
              "Si se miden las fracciones en la propia máquina paralela —sea ahora σ la "
              "fracción secuencial del tiempo de ejecución en *n* núcleos—, se obtiene la "
              "**aceleración escalada**:"),
        ("f", "*S*(*n*) = σ + (1 − σ) · *n*  =  *n* − (*n* − 1) · σ"),
        ("t", "**Achtung:** σ bezieht sich hier auf die Laufzeit **auf dem Parallelrechner**, "
              "nicht – wie bei Amdahl – auf die Laufzeit auf einem Kern. Mit σ = 0,05 und 16 "
              "Kernen ergibt sich *S*(16) = 16 − 15 · 0,05 = 15,25: Die Beschleunigung wächst "
              "nahezu **linear** mit der Zahl der Kerne. Man spricht von **schwacher "
              "Skalierung** (engl. *weak scaling*).",
              "**Atención:** aquí σ se refiere al tiempo de ejecución **en la máquina "
              "paralela**, no —como en Amdahl— al tiempo en un núcleo. Con σ = 0,05 y 16 "
              "núcleos resulta *S*(16) = 16 − 15 · 0,05 = 15,25: la aceleración crece de forma "
              "casi **lineal** con el número de núcleos. Se habla de **escalabilidad débil** "
              "(ingl. *weak scaling*)."),
        ("tabla",),
        ("t", "Die beiden Gesetze widersprechen sich nicht; sie beantworten verschiedene "
              "Fragen. Amdahl fragt: Wie viel schneller wird eine **gegebene** Aufgabe? "
              "Gustafson fragt: Wie viel **mehr** Arbeit schaffe ich in derselben Zeit? Welche "
              "Sicht passt, hängt von der **Anwendung** ab.",
              "Las dos leyes no se contradicen; responden a preguntas distintas. Amdahl "
              "pregunta: ¿cuánto más rápida se vuelve una tarea **dada**? Gustafson pregunta: "
              "¿cuánto trabajo **más** consigo hacer en el mismo tiempo? Qué visión es la "
              "adecuada depende de la **aplicación**."),
    ]),
    ("Fazit für die Praxis", "Conclusión práctica", "Abschnitt 1.2.5, S. 20–21",
     "apartado 1.2.5, pp. 20–21", [
        ("t", "Faustregel: Zuerst mit einem **Profiler** messen, wo das Programm seine Zeit "
              "verbringt; dann die rechenintensivsten Schleifen parallelisieren; nach jedem "
              "Schritt Ergebnis und Laufzeit mit der sequenziellen Version vergleichen.",
              "Regla práctica: primero medir con un **perfilador** (profiler) dónde pasa el "
              "tiempo el programa; después paralelizar los bucles con más carga de cálculo; "
              "tras cada paso, comparar resultado y tiempo de ejecución con la versión "
              "secuencial."),
        ("t", "Bleibt die Beschleunigung deutlich unter der Zahl der Kerne, ist das kein "
              "Fehler, sondern der Normalfall. Aufschlussreich ist die Frage, **woran** es "
              "liegt: am sequenziellen Anteil, am Verwaltungsaufwand oder an der "
              "**Speicherbandbreite**.",
              "Si la aceleración se queda claramente por debajo del número de núcleos, no es un "
              "error, sino lo normal. Lo revelador es preguntarse **a qué se debe**: a la "
              "fracción secuencial, a los costes de gestión o al **ancho de banda de "
              "memoria**."),
    ]),
]


def num(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tabla_amdahl_gustafson():
    """Tabla 1 (calculada aquí, no copiada): aceleración para σ = 0,05."""
    s = 0.05
    filas = [[P("*n* (Kerne · núcleos)", SCELL), P("Amdahl", SCELL), P("Gustafson", SCELL)]]
    for n in (1, 2, 4, 8, 16, 64, 1024):
        filas.append([P(str(n), SNUM), P(num(1 / (s + (1 - s) / n)), SNUM),
                      P(num(n - (n - 1) * s), SNUM)])
    filas.append([P("*n* → ∞", SNUM), P(num(1 / s), SNUM), P("→ ∞", SNUM)])
    t = Table(filas, colWidths=[3.6 * cm, 3.0 * cm, 3.0 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRISC), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.3, LINEA), ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    cap = P("**Tabelle 1 · Tabla 1.** Beschleunigung *S*(*n*) für σ = 0,05 · Aceleración "
            "*S*(*n*) para σ = 0,05 (Amdahl: σ medido en un núcleo; Gustafson: σ medido en la "
            "máquina paralela)", SCAP)
    return [cap, t]


def bloque_bilingue(filas):
    datos = [[Paragraph("DEUTSCH", SCAB), Paragraph("ESPAÑOL", SCAB)]]
    estilo = [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
              ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
    for fila in filas:
        r = len(datos)
        if fila[0] == "t":
            datos.append([P(fila[1], SDE), P(fila[2], SES)])
            estilo += [("BACKGROUND", (0, r), (0, r), FONDO_DE),
                       ("LINEBELOW", (0, r), (-1, r), 0.3, LINEA)]
        elif fila[0] == "code":
            TEXTOS.append(fila[1])
            datos.append([Preformatted(fila[1], SCODE), ""])
            estilo += [("SPAN", (0, r), (1, r)), ("BACKGROUND", (0, r), (1, r), GRISC),
                       ("LEFTPADDING", (0, r), (1, r), 14)]
        elif fila[0] == "f":
            datos.append([P(fila[1], SFORM), ""])
            estilo += [("SPAN", (0, r), (1, r)), ("TOPPADDING", (0, r), (1, r), 6),
                       ("BOTTOMPADDING", (0, r), (1, r), 7),
                       ("LINEBELOW", (0, r), (-1, r), 0.3, LINEA)]
        elif fila[0] == "tabla":
            datos.append([tabla_amdahl_gustafson(), ""])
            estilo += [("SPAN", (0, r), (1, r)), ("ALIGN", (0, r), (1, r), "CENTER"),
                       ("TOPPADDING", (0, r), (1, r), 7), ("BOTTOMPADDING", (0, r), (1, r), 8),
                       ("LINEBELOW", (0, r), (-1, r), 0.3, LINEA)]
    t = Table(datos, colWidths=[ANCHO / 2, ANCHO / 2], repeatRows=1)
    t.setStyle(TableStyle(estilo))
    return t


# ================================================================ PARTE 2: glosario
# Sustantivo: ("n", artículo, singular, plural | None, español, página)
# Verbo:      ("v", infinitivo, presente 3.ª sg., Präteritum, Partizip II con auxiliar,
#              régimen | None, español, página)
# Otro:       ("x", palabra, clase, español, página)
# Página = página impresa del libro donde aparece en ese apartado («–»: solo en este texto).
GLOSARIO = [
    ("Einführung und 1.1 · Merkmale von OpenMP", "pp. 1–7", [
        ("n", "die", "Programmierschnittstelle", "Programmierschnittstellen", "interfaz de programación (API)", "1"),
        ("n", "die", "Parallelität", None, "paralelismo", "1"),
        ("n", "der", "Quelltext", "Quelltexte", "código fuente (también: der Quellcode)", "1"),
        ("n", "die", "Compilerdirektive", "Compilerdirektiven", "directiva de compilador", "1"),
        ("n", "die", "Bibliotheksfunktion", "Bibliotheksfunktionen", "función de biblioteca", "1"),
        ("n", "die", "Umgebungsvariable", "Umgebungsvariablen", "variable de entorno", "1"),
        ("n", "der", "Hersteller", "Hersteller", "fabricante", "1"),
        ("n", "die", "Arbeitsaufteilung", "Arbeitsaufteilungen", "reparto del trabajo", "1"),
        ("n", "der", "Thread", "Threads", "hilo (de ejecución)", "1"),
        ("n", "die", "Anweisung", "Anweisungen", "instrucción, sentencia", "1"),
        ("n", "die", "Parallelisierung", "Parallelisierungen", "paralelización", "1"),
        ("n", "die", "Laufzeitumgebung", "Laufzeitumgebungen", "entorno de ejecución", "2"),
        ("n", "die", "Kommandozeilenoption", "Kommandozeilenoptionen", "opción de línea de comandos", "2"),
        ("n", "die", "Schleife", "Schleifen", "bucle", "3"),
        ("n", "der", "Schleifenkörper", "Schleifenkörper", "cuerpo del bucle", "3"),
        ("n", "der", "Abstraktionsgrad", "Abstraktionsgrade", "nivel de abstracción", "3"),
        ("n", "die", "Klausel", "Klauseln", "cláusula", "4"),
        ("n", "der", "Zeilenumbruch", "Zeilenumbrüche", "salto de línea", "5"),
        ("n", "die", "Headerdatei", "Headerdateien", "archivo de cabecera", "5"),
        ("n", "die", "Laufzeitbibliothek", "Laufzeitbibliotheken", "biblioteca de tiempo de ejecución", "5"),
        ("n", "das", "Makro", "Makros", "macro del preprocesador. El libro llama «Umgebungsvariable» "
                                       "a `_OPENMP`, pero técnicamente es una macro", "–"),
        ("n", "der", "Schalter", "Schalter", "interruptor; opción (del compilador)", "6"),
        ("x", "lauffähig", "Adj.", "ejecutable, que funciona", "3"),
        ("v", "sich zusammensetzen", "setzt sich zusammen", "setzte sich zusammen",
         "hat sich zusammengesetzt", "aus + D", "componerse de", "1"),
        ("v", "unterstützen", "unterstützt", "unterstützte", "hat unterstützt", None,
         "soportar, admitir", "2"),
        ("v", "ausführen", "führt aus", "führte aus", "hat ausgeführt", None, "ejecutar", "3"),
        ("v", "zugreifen", "greift zu", "griff zu", "hat zugegriffen", "auf + A", "acceder a", "3"),
        ("v", "einbinden", "bindet ein", "band ein", "hat eingebunden", None,
         "incluir (un archivo)", "5"),
        ("v", "übersetzen", "übersetzt", "übersetzte", "hat übersetzt", None,
         "compilar (y también: traducir)", "6"),
        ("x", "zur Verfügung stellen / stehen", "Ausdruck", "poner / estar a disposición", "1"),
    ]),
    ("1.2.1 · Prozesse und Threads", "pp. 8–10", [
        ("n", "der", "Prozess", "Prozesse", "proceso", "8"),
        ("n", "das", "Betriebssystem", "Betriebssysteme", "sistema operativo", "8"),
        ("n", "die", "Festplatte", "Festplatten", "disco duro", "8"),
        ("n", "der", "Programmzähler", "Programmzähler", "contador de programa (también: der Befehlszähler)", "8"),
        ("n", "das", "Register", "Register", "registro (de la CPU)", "8"),
        ("n", "der", "Stack", "Stacks", "pila (en alemán también: der Stapelspeicher)", "8"),
        ("n", "der", "Speicherbereich", "Speicherbereiche", "área de memoria", "8"),
        ("n", "die", "Rücksprungadresse", "Rücksprungadressen", "dirección de retorno", "8"),
        ("n", "der", "Heap", "Heaps", "montículo, heap (en alemán también: die Halde)", "9"),
        ("n", "der", "Systemaufruf", "Systemaufrufe", "llamada al sistema", "9"),
        ("n", "der", "Prozesskontrollblock", "Prozesskontrollblöcke", "bloque de control de proceso", "9"),
        ("n", "der", "Kontextwechsel", "Kontextwechsel",
         "cambio de contexto (el libro usa el inglés «Context Switching»)", "9"),
        ("n", "der", "Ausführungsstrang", "Ausführungsstränge", "hilo de ejecución", "9"),
        ("n", "der", "Adressraum", "Adressräume", "espacio de direcciones", "9"),
        ("n", "die", "Benutzereingabe", "Benutzereingaben", "entrada del usuario", "9"),
        ("n", "die", "Oberfläche", "Oberflächen", "interfaz (gráfica); también: superficie", "9"),
        ("n", "der", "Kontrollfluss", "Kontrollflüsse", "flujo de control", "10"),
        ("n", "die", "Wettlaufsituation", "Wettlaufsituationen", "condición de carrera (race condition)", "–"),
        ("v", "zuweisen", "weist zu", "wies zu", "hat zugewiesen", "etw. (A) + D",
         "asignar algo a", "8"),
        ("v", "sichern", "sichert", "sicherte", "hat gesichert", None, "guardar, poner a salvo", "9"),
        ("v", "wiederherstellen", "stellt wieder her", "stellte wieder her", "hat wiederhergestellt",
         None, "restaurar", "9"),
        ("v", "sich (D) etw. teilen", "teilt sich", "teilte sich", "hat sich geteilt", "mit + D",
         "compartir algo con", "9"),
    ]),
    ("1.2.2 · Parallele Hardwarearchitekturen", "pp. 10–13", [
        ("n", "das", "Gesetz", "Gesetze", "ley", "10"),
        ("n", "die", "Faustregel", "Faustregeln", "regla empírica", "10"),
        ("n", "der", "Transistor", "Transistoren", "transistor", "10"),
        ("n", "die", "Taktrate", "Taktraten", "frecuencia de reloj (también: die Taktfrequenz)", "10"),
        ("n", "die", "Leistungssteigerung", "Leistungssteigerungen", "aumento del rendimiento", "10"),
        ("n", "der", "Prozessorkern", "Prozessorkerne", "núcleo del procesador", "11"),
        ("n", "die", "Recheneinheit", "Recheneinheiten", "unidad de cálculo", "11"),
        ("n", "die", "Rechenleistung", "Rechenleistungen", "potencia de cálculo", "11"),
        ("n", "der", "Datenstrom", "Datenströme", "flujo de datos", "11"),
        ("n", "der", "Rechner", "Rechner", "ordenador, computadora", "11"),
        ("n", "die", "Grafikkarte", "Grafikkarten", "tarjeta gráfica", "12"),
        ("n", "die", "Befehlserweiterung", "Befehlserweiterungen", "extensión del juego de instrucciones", "12"),
        ("n", "die", "Massenfertigung", None, "producción en masa", "12"),
        ("n", "die", "Speicherorganisation", "Speicherorganisationen", "organización de la memoria", "12"),
        ("x", "verteilt", "Adj.", "distribuido (verteilter Speicher: memoria distribuida)", "12"),
        ("x", "gemeinsam genutzt", "Adj.", "compartido (gemeinsam genutzter Speicher: memoria compartida)", "12"),
        ("v", "sich verdoppeln", "verdoppelt sich", "verdoppelte sich", "hat sich verdoppelt", None,
         "duplicarse", "10"),
        ("v", "einordnen", "ordnet ein", "ordnete ein", "hat eingeordnet", "in + A", "clasificar en", "11"),
        ("v", "anpassen", "passt an", "passte an", "hat angepasst", "an + A", "adaptar a", "11"),
        ("x", "zum Einsatz kommen (kam, ist gekommen)", "Ausdruck", "emplearse, utilizarse", "13"),
    ]),
    ("1.2.3 · Leistungsmessung", "pp. 13–14", [
        ("n", "die", "Leistungsmessung", "Leistungsmessungen", "medición del rendimiento", "13"),
        ("n", "die", "Laufzeit", "Laufzeiten", "tiempo de ejecución", "13"),
        ("n", "die", "Kenngröße", "Kenngrößen", "indicador, magnitud característica", "13"),
        ("n", "die", "Beschleunigung", "Beschleunigungen", "aceleración (speedup)", "13"),
        ("n", "die", "Effizienz", None, "eficiencia", "13"),
        ("n", "der", "Quotient", "Quotienten", "cociente (declinación en -en: des Quotienten)", "13"),
        ("n", "das", "Verhältnis", "Verhältnisse", "relación, proporción", "13"),
        ("n", "der", "Mehraufwand", None, "coste adicional (overhead)", "13"),
        ("n", "die", "Obergrenze", "Obergrenzen", "límite superior", "14"),
        ("n", "der", "Cache", "Caches", "memoria caché (también: der Cache-Speicher)", "14"),
        ("n", "die", "Speicherzugriffszeit", "Speicherzugriffszeiten", "tiempo de acceso a memoria", "14"),
        ("v", "ausnutzen", "nutzt aus", "nutzte aus", "hat ausgenutzt", None, "aprovechar", "14"),
        ("v", "auftreten", "tritt auf", "trat auf", "ist aufgetreten", None, "aparecer, producirse", "14"),
    ]),
    ("1.2.4 · Das Amdahl’sche Gesetz", "pp. 14–16", [
        ("n", "der", "Anteil", "Anteile", "fracción, proporción", "15"),
        ("n", "die", "Abbildung", "Abbildungen", "figura (abreviado: Abb.)", "15"),
        ("n", "die", "Anzahl", None, "número, cantidad", "15"),
        ("v", "beschränken", "beschränkt", "beschränkte", "hat beschränkt", "(nach oben)",
         "acotar (superiormente)", "14"),
        ("v", "normieren", "normiert", "normierte", "hat normiert", "auf + A", "normalizar a", "15"),
        ("v", "vernachlässigen", "vernachlässigt", "vernachlässigte", "hat vernachlässigt", None,
         "despreciar, no tener en cuenta", "15"),
    ]),
    ("1.2.5 · Das Gustafson’sche Gesetz", "pp. 16–21", [
        ("n", "die", "Sichtweise", "Sichtweisen", "punto de vista", "16"),
        ("n", "der", "Widerspruch", "Widersprüche", "contradicción", "17"),
        ("n", "die", "Vorhersage", "Vorhersagen", "predicción", "17"),
        ("n", "die", "Problemgröße", "Problemgrößen", "tamaño del problema", "18"),
        ("n", "der", "Freiheitsgrad", "Freiheitsgrade", "grado de libertad", "18"),
        ("n", "der", "Engpass", "Engpässe", "cuello de botella", "18"),
        ("n", "die", "Skalierbarkeit", None, "escalabilidad", "19"),
        ("n", "die", "Vorbedingung", "Vorbedingungen", "condición previa", "20"),
        ("x", "streng monoton", "Adj.", "estrictamente monótono", "18"),
        ("v", "skalieren", "skaliert", "skalierte", "hat skaliert", None, "escalar", "19"),
        ("v", "konvergieren", "konvergiert", "konvergierte", "hat konvergiert", "gegen + A",
         "converger a", "19"),
    ]),
]


def celda_aleman(e):
    if e[0] == "n":
        _, art, sg, pl, _, _ = e
        color = COLOR_ARTICULO[art].hexval()[2:]
        plural = f"Pl. die {pl}" if pl else "nur Sg."
        TEXTOS.extend([art, sg, pl or ""])
        return Paragraph(f'<font color="#{color}"><b>{art}</b></font> <b>{md(sg)}</b>'
                         f'<font size="8" color="#555555"> · {md(plural)}</font>', SCELL)
    if e[0] == "v":
        _, inf, pres, prat, perf, reg, _, _ = e
        TEXTOS.extend([inf, pres, prat, perf, reg or ""])
        regimen = f' <b>{md(reg)}</b>' if reg else ""
        return Paragraph(f'<b>{md(inf)}</b>{regimen}<br/><font size="8" color="#555555">'
                         f'{md(pres)} · {md(prat)} · {md(perf)}</font>', SCELL)
    _, palabra, clase, _, _ = e
    TEXTOS.extend([palabra, clase])
    return Paragraph(f'<b>{md(palabra)}</b> <font size="8" color="#555555">({md(clase)})</font>',
                     SCELL)


def tabla_glosario(entradas):
    datos = [[Paragraph("DEUTSCH", SCAB), Paragraph("ESPAÑOL", SCAB), Paragraph("S.", SCAB)]]
    for e in entradas:
        es, pag = (e[4], e[5]) if e[0] == "n" else (e[6], e[7]) if e[0] == "v" else (e[3], e[4])
        datos.append([celda_aleman(e), P(es, SCELL), P(pag, SNUM)])
    t = Table(datos, colWidths=[8.4 * cm, ANCHO - 9.7 * cm, 1.3 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_DE]),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, LINEA),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


# ================================================================ PARTE 3: estructuras
ESTRUCTURAS = [
    ("Pasiva de proceso: **werden** + participio II",
     "Die Schleife **wird** auf mehrere Threads **verteilt**.",
     "El bucle se reparte entre varios hilos.",
     "En español suena mejor la pasiva refleja con «se» que «es repartido»."),
    ("Pasiva con verbo modal",
     "Die Unterstützung **muss** ausdrücklich **aktiviert werden**.",
     "Hay que activar expresamente el soporte.",
     "Se conjuga el modal; al final van el participio II y «werden» en infinitivo."),
    ("**sich lassen** + infinitivo",
     "Der Code **lässt sich** schrittweise **parallelisieren**.",
     "El código se puede paralelizar paso a paso.",
     "Equivale a «kann … werden»: posibilidad en pasiva."),
    ("**sein** + **zu** + infinitivo",
     "MISD-Systeme **sind** in der Praxis kaum **anzutreffen**.",
     "Los sistemas MISD apenas se encuentran en la práctica.",
     "Según el contexto, «se puede» o «hay que»: «Die Ergebnisse sind zu prüfen» = «hay que "
     "comprobar los resultados»."),
    ("Atributo participial extendido",
     "der **dynamisch angeforderte** Speicher · die **unmittelbar folgende** Schleife",
     "la memoria solicitada dinámicamente · el bucle que sigue inmediatamente",
     "Entre artículo y sustantivo cabe una oración entera: lee artículo → sustantivo → vuelve "
     "al participio."),
    ("Nominalización (*Nominalstil*)",
     "**Bei der Parallelisierung** der Schleife … = Wenn man die Schleife parallelisiert, …",
     "Al paralelizar el bucle…",
     "Verbos convertidos en sustantivos (-ung, -keit, -heit); en español suelen volver a ser "
     "verbos."),
    ("Verbos funcionales (*Funktionsverbgefüge*)",
     "**zur Verfügung stehen** · **zum Einsatz kommen** · **eine Rolle spielen** · **ins "
     "Spiel kommen**",
     "estar disponible · emplearse · importar, influir · entrar en juego",
     "El significado lo aporta el sustantivo; el verbo casi no dice nada."),
    ("Compuestos (*Komposita*)",
     "die Speicher·zugriffs·zeit = der Speicher + der Zugriff + s + die Zeit",
     "el tiempo de acceso a memoria",
     "El último elemento fija género y significado: se traduce de derecha a izquierda. La «s» "
     "de unión no es plural: Umgebung·s·variable."),
    ("Subjuntivo I en definiciones",
     "**Es sei** *T*_{1} die Laufzeit auf einem Kern. · σ **sei** der sequenzielle Anteil.",
     "Sea *T*_{1} el tiempo de ejecución en un núcleo. · Sea σ la fracción secuencial.",
     "Típico de las matemáticas. En estilo indirecto: «Gustafson meinte, die Laufzeit **sei** "
     "konstant» = «… que el tiempo era constante»."),
    ("Condicional sin «wenn»",
     "**Ist** die OpenMP-Unterstützung eingeschaltet, **definiert** der Compiler `_OPENMP`.",
     "Si el soporte de OpenMP está activado, el compilador define `_OPENMP`.",
     "Verbo en primera posición = «si…»; la oración principal también empieza por el verbo."),
    ("Infinitivo como instrucción",
     "Zuerst **messen**, dann **parallelisieren**, danach **vergleichen**.",
     "Primero medir, luego paralelizar, después comparar.",
     "Típico de manuales, listas de pasos y recetas."),
    ("Verbos con preposición fija",
     "bestehen **aus** + D · zugreifen **auf** + A · abhängen **von** + D · sich beziehen "
     "**auf** + A · hinweisen **auf** + A · streben **gegen** + A · liegen **an** + D",
     "constar de · acceder a · depender de · referirse a · señalar · tender a · deberse a",
     "Apréndelos con su preposición y su caso, como en el glosario."),
    ("Adjetivos de nombres propios",
     "das **Amdahl’sche** Gesetz (= amdahlsche) · nach dem **Moore’schen** Gesetz",
     "la ley de Amdahl · según la ley de Moore",
     "Nombre + -sch + desinencia de adjetivo; con apóstrofo va con mayúscula."),
    ("Abreviaturas frecuentes",
     "z. B. · d. h. · u. a. · bzw. · o. g. · vgl. · s. · Abb. · ggf. · i. d. R.",
     "p. ej. · es decir · entre otros · o bien / respectivamente · arriba mencionado · cf. · "
     "véase · fig. · en su caso · por lo general",
     "«bzw.» (beziehungsweise) es la más traicionera: «o bien» o «respectivamente» según el "
     "contexto."),
]

TRAMPAS = [
    ("übersetzen", "en informática, **compilar** (además de «traducir»): «den Quelltext neu "
                   "übersetzen» = volver a compilar el código fuente."),
    ("der Rechner", "el **ordenador**, no solo la calculadora (der Taschenrechner)."),
    ("die Leistung", "**rendimiento** o **potencia** (Rechenleistung, Leistungsaufnahme), no "
                     "«logro»."),
    ("gemeinsam", "**compartido** en «gemeinsamer Speicher» (memoria compartida), no solo "
                  "«común»."),
    ("die Anweisung / der Befehl", "**sentencia** de un lenguaje de programación / "
                                   "**instrucción** de máquina u orden."),
    ("sequenziell = seriell", "sinónimos en este libro: **secuencial**, no paralelo."),
    ("der Speicher", "**memoria** (Arbeitsspeicher = RAM) y también almacenamiento; «speichern» "
                     "= guardar."),
    ("bzw.", "«o bien» o «respectivamente»: «Version 2.5 bzw. 3.0» = «versión 2.5 o, en su "
             "caso, 3.0»."),
]


def tabla_estructuras():
    cab = ["ESTRUCTURA", "DEUTSCH", "ESPAÑOL", "NOTA"]
    datos = [[Paragraph(c, SCAB) for c in cab]]
    for est, de, es, nota in ESTRUCTURAS:
        datos.append([P(est, SCELL), P(de, SCELL), P(es, SCELL), P(nota, SCELLS)])
    anchos = [3.9 * cm, 5.0 * cm, 4.2 * cm, ANCHO - 13.1 * cm]
    t = Table(datos, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_DE]),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, LINEA),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def tabla_trampas():
    datos = [[Paragraph("DEUTSCH", SCAB), Paragraph("OJO: SIGNIFICA…", SCAB)]]
    for de, es in TRAMPAS:
        datos.append([P("**" + de + "**", SCELL), P(es, SCELL)])
    t = Table(datos, colWidths=[4.2 * cm, ANCHO - 4.2 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_DE]),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, LINEA),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


# ================================================================ portada y montaje
def portada(story):
    story.append(Spacer(1, 2.2 * cm))
    story.append(P("Alemán técnico", STIT))
    story.append(Spacer(1, 0.25 * cm))
    story.append(P("OpenMP und parallele Programmierung", St(
        "t2", parent=STIT, fontSize=17, leading=22, textColor=AZUL2)))
    story.append(Spacer(1, 0.5 * cm))
    story.append(P("Cuaderno bilingüe alemán | español sobre los temas del capítulo 1 "
                   "(«Einführung»)", SSUB))
    story.append(Spacer(1, 1.1 * cm))

    caja = [
        P("**Qué es.** Un texto propio, escrito para aprender alemán técnico, que recorre los "
          "mismos temas que el capítulo 1 (pp. 1–21) de S. Hoffmann y R. Lienhart, *OpenMP. "
          "Eine Einführung in die parallele Programmierung mit C/C++* (Springer, 2008). "
          "**No es una traducción del libro**, que tiene derechos de autor: los ejemplos y las "
          "frases son nuevos. Cada apartado indica las páginas del original para leerlo "
          "después.", SCAJA),
        P("**Cómo usarlo.**", SCAJA),
        P("1. Lee la columna izquierda (alemán) tapando la derecha e intenta entender cada fila.",
          SCAJA),
        P("2. Comprueba con la columna derecha (español). Las palabras clave van en **negrita** "
          "en los dos idiomas.", SCAJA),
        P("3. Lee después las páginas indicadas del libro: el vocabulario ya te sonará.", SCAJA),
        P("4. Repasa el glosario (sustantivos con género y plural; verbos con sus tres formas y "
          "su preposición) y las estructuras típicas del alemán técnico.", SCAJA),
    ]
    t = Table([[caja]], colWidths=[ANCHO - 2 * cm])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, AZUL2),
                           ("BACKGROUND", (0, 0), (-1, -1), FONDO_DE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 14),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                           ("TOPPADDING", (0, 0), (-1, -1), 12),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    story.append(t)
    story.append(Spacer(1, 1.0 * cm))

    story.append(P("**Contenido**", SB))
    indice = [f"**Parte 1 · Texto bilingüe** — {len(SECCIONES)} apartados:"]
    for i, (de, es, *_r) in enumerate(SECCIONES, 1):
        indice.append(f"    {i}. {de} · *{es}*")
    indice += ["**Parte 2 · Glosario del capítulo** (con la página del libro)",
               "**Parte 3 · Estructuras típicas del alemán técnico** y trampas frecuentes"]
    SIX = St("ix", parent=SB, spaceAfter=1.5)
    for linea in indice:
        TEXTOS.append(linea)
        story.append(Paragraph(md(linea).replace("    ", "&nbsp;" * 6), SIX))


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont(SANS, 7.8)
    canvas.setFillColor(GRIS)
    canvas.drawString(MARGEN, 1.05 * cm, "Alemán técnico · OpenMP, cap. 1 · texto propio de estudio")
    canvas.drawRightString(A4[0] - MARGEN, 1.05 * cm, f"{doc.page}")
    canvas.setStrokeColor(LINEA)
    canvas.setLineWidth(0.5)
    canvas.line(MARGEN, 1.4 * cm, A4[0] - MARGEN, 1.4 * cm)
    canvas.restoreState()


def construir():
    story = []
    portada(story)
    story.append(PageBreak())

    story.append(P("Parte 1 · Texto bilingüe", SH1))
    story.append(P("Cada fila dice lo mismo en los dos idiomas. Las fórmulas y el código "
                   "ocupan el ancho completo.", SREF))
    for i, (de, es, ref_de, ref_es, filas) in enumerate(SECCIONES, 1):
        story.append(CondPageBreak(5.5 * cm))
        story.append(Paragraph(f"{i} · {md(de)} <font color=\"#555555\">— {md(es)}</font>", SH2))
        TEXTOS.extend([de, es, ref_de, ref_es])
        story.append(Paragraph(f"→ Buch: {md(ref_de)} · Libro: {md(ref_es)}", SREF))
        story.append(bloque_bilingue(filas))

    story.append(PageBreak())
    story.append(P("Parte 2 · Glosario del capítulo", SH1))
    story.append(Paragraph(
        f'Sustantivos con artículo y plural (<font color="#{DER.hexval()[2:]}"><b>der</b></font> · '
        f'<font color="#{DIE.hexval()[2:]}"><b>die</b></font> · '
        f'<font color="#{DAS.hexval()[2:]}"><b>das</b></font>); verbos con presente, Präteritum '
        f'y Partizip II, y su preposición. «S.» = página del libro donde aparece; «–» = solo en '
        f'este cuaderno.', SREF))
    for titulo, paginas, entradas in GLOSARIO:
        TEXTOS.extend([titulo, paginas])
        story.append(CondPageBreak(4 * cm))
        story.append(Paragraph(f"{md(titulo)} <font color=\"#555555\" size=\"9\">({md(paginas)})"
                               f"</font>", SH2))
        story.append(tabla_glosario(entradas))

    story.append(PageBreak())
    story.append(P("Parte 3 · Estructuras típicas del alemán técnico", SH1))
    story.append(P("Los ejemplos salen del texto de la parte 1: búscalos allí en su contexto.",
                   SREF))
    story.append(tabla_estructuras())
    story.append(Spacer(1, 0.4 * cm))
    story.append(KeepTogether([P("Trampas frecuentes", SH2), tabla_trampas()]))

    doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=MARGEN, rightMargin=MARGEN,
                            topMargin=1.6 * cm, bottomMargin=1.9 * cm,
                            title="Alemán técnico: OpenMP, capítulo 1 (texto bilingüe)",
                            author="indescifrable · material de estudio",
                            subject="Texto propio alemán-español sobre OpenMP y programación "
                                    "paralela, con glosario y estructuras del alemán técnico")
    doc.build(story, onLaterPages=pie)


def verificar_glifos():
    if CMAP is None:
        return
    faltan = sorted({c for t in TEXTOS for c in t if c.strip() and ord(c) not in CMAP})
    if faltan:
        raise SystemExit(f"Glifos sin fuente: {' '.join(faltan)}")


if __name__ == "__main__":
    construir()
    verificar_glifos()
    print(f"PDF escrito: {SALIDA}")
