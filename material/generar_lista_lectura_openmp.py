# -*- coding: utf-8 -*-
"""Genera material/lista-lectura-openmp-cap1.pdf: lista de lectura PÁGINA A PÁGINA para leer
el capítulo 1 («Einführung», pp. 1-21) de S. Hoffmann y R. Lienhart, «OpenMP. Eine Einführung
in die parallele Programmierung mit C/C++» (Springer 2008) con nivel B1−.

Por cada página del libro: el vocabulario por encima de B1 en orden de aparición (solo la
primera vez; sustantivos con género y plural, verbos con presente, Präteritum, Partizip II y
régimen) y la gramática nueva, localizada con un fragmento BREVE del libro («…» recorta).
Además: mapa de la gramática, palabras pequeñas (conectores), internacionalismos e índice.
No reproduce el libro: solo palabras sueltas y citas cortas para encontrar cada estructura.

Reutiliza fuentes, colores y el marcado mínimo de generar_aleman_tecnico_openmp.py.
Uso:  PYTHONUTF8=1 python material/generar_lista_lectura_openmp.py
"""
import re
import unicodedata
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, CondPageBreak)

from generar_aleman_tecnico_openmp import (md, CMAP, SANS, SANS_B, AZUL, AZUL2, GRIS, GRISC,
                                           LINEA, FONDO_DE, COLOR_ARTICULO, MARGEN, ANCHO,
                                           STIT, SSUB, SH1, SH2, SREF, SB, SCELL, SCELLS, SCAB,
                                           SNUM, SCAJA)

SALIDA = Path(__file__).with_name("lista-lectura-openmp-cap1.pdf")
TEC = colors.HexColor("#8a5a00")
St = ParagraphStyle
SV = St("v", parent=SCELL, fontSize=8.9, leading=11.2)
SVS = St("vs", parent=SV, fontSize=7.8, leading=9.6, textColor=GRIS)
SFRAG = St("frag", parent=SCELL, fontSize=8.9, leading=11.4)
SEXP = St("exp", parent=SCELL, fontSize=8.7, leading=11.2)
SIDX = St("idx", parent=SCELL, fontSize=8, leading=9.6)
STEMA = St("tema", parent=SREF, fontSize=8.2, spaceAfter=3)

TEXTOS = []


def P(t, estilo):
    TEXTOS.append(t)
    return Paragraph(md(t), estilo)


# ---------------------------------------------------------------- tipos de entrada
def N(art, sg, pl, es, txt=None):
    """Sustantivo: artículo, singular, plural (None = solo singular), español, forma en el texto."""
    return ("n", art, sg, pl, es, txt)


def V(inf, pres, prat, perf, reg, es, txt=None):
    """Verbo: infinitivo, 3.ª sg. presente, Präteritum, Partizip II con auxiliar, régimen."""
    return ("v", inf, pres, prat, perf, reg, es, txt)


def X(palabra, clase, es, txt=None):
    """Adjetivo, adverbio, conector o expresión."""
    return ("x", palabra, clase, es, txt)


def G(tipo, fragmento, explicacion):
    """Nota de gramática: tipo (ver TIPOS), fragmento BREVE del libro, explicación."""
    return (tipo, fragmento, explicacion)


TIPOS = {
    "part": ("Atributo participial extendido",
             "artículo + complementos + participio + sustantivo = «el X que…»: lee artículo → "
             "sustantivo → vuelve atrás"),
    "gerund": ("Gerundivo: zu + participio I", "«die zu lösenden Aufgaben» = las tareas que hay "
                                               "que resolver"),
    "pasmod": ("Pasiva con modal y tiempos compuestos", "«… eingefügt werden müssen» = hay que "
                                                        "insertar"),
    "pasimp": ("Pasiva impersonal", "«auf … wird zugegriffen» = se accede a (sin sujeto)"),
    "zustand": ("Pasiva de estado", "sein + participio II = está(n) + participio"),
    "lassen": ("sich lassen + infinitivo", "= se puede + infinitivo"),
    "seinzu": ("sein + zu + infinitivo", "= se puede / hay que + infinitivo"),
    "v1": ("Condicional sin «wenn»", "verbo al principio de la oración = «si…»"),
    "konj1": ("Subjuntivo I", "estilo indirecto («según él…») y definiciones («Sea σ…»)"),
    "konj2": ("Subjuntivo II", "hipótesis: wäre, hätte, käme, würde… = sería, tendría…"),
    "fvg": ("Verbos funcionales", "zum Ausdruck bringen = expresar; Verwendung finden = usarse"),
    "trenn": ("Verbo separable con el prefijo lejos", "busca el prefijo al final de la oración"),
    "korr": ("Correlatos", "darauf / davon / darüber / dadurch … dass / ob / wie"),
    "rel": ("Relativos difíciles", "dessen, deren, derer, mit Hilfe dessen, wonach, was"),
    "infzu": ("Infinitivo con zu", "es ist …, … zu; um / ohne / statt … zu"),
    "orden": ("Orden de palabras", "complemento delante y sujeto detrás del verbo"),
    "guion": ("Guion de ahorro", "an- und ausschalten = anschalten und ausschalten"),
    "otros": ("Fórmulas, erratas y otros", "es handelt sich um, es empfiehlt sich, was … angeht…"),
}

# ================================================================ PÁGINA A PÁGINA
# (página del libro, apartado, vocabulario en orden de aparición, gramática)
PAGINAS = [
    (1, "Kap. 1 · Einführung", [
        N("die", "Programmierschnittstelle", "Programmierschnittstellen", "interfaz de programación (API)"),
        N("die", "Parallelität", None, "paralelismo"),
        V("spezifizieren", "spezifiziert", "spezifizierte", "hat spezifiziert", None,
          "especificar, definir con precisión"),
        X("konkurrierend", "Adj.", "que compite, alternativo", "konkurrierende Ansätze"),
        N("der", "Ansatz", "Ansätze", "enfoque, planteamiento"),
        N("die", "Parallelisierung", "Parallelisierungen", "paralelización"),
        V("erfordern", "erfordert", "erforderte", "hat erfordert", None, "requerir, exigir"),
        X("ursprünglich", "Adj./Adv.", "original(mente)"),
        X("sequenziell", "Adj.", "secuencial (también se escribe sequentiell)"),
        N("der", "Quellcode", "Quellcodes", "código fuente (= der Quelltext, Pl. die Quelltexte)"),
        V("beitragen", "trägt bei", "trug bei", "hat beigetragen", "zu + D", "contribuir a",
          "trägt … zu der Lesbarkeit … bei"),
        X("erheblich", "Adj./Adv.", "considerable(mente)"),
        N("die", "Lesbarkeit", None, "legibilidad"),
        X("resultierend", "Adj.", "resultante"),
        N("die", "Anweisung", "Anweisungen", "téc. instrucción, sentencia (normalmente: orden, "
                                              "indicación)"),
        V("einfügen", "fügt ein", "fügte ein", "hat eingefügt", None, "insertar"),
        X("sofern", "Konj.", "siempre que, en la medida en que (verbo al final)"),
        V("sich eignen", "eignet sich", "eignete sich", "hat sich geeignet", "zu + D / für + A",
          "ser adecuado para"),
        N("die", "Spezifizierung", "Spezifizierungen", "especificación"),
        X("kaum", "Adv.", "apenas, casi no (kaum einen schnelleren Weg = casi ningún camino más "
                          "rápido)"),
        V("parallelisieren", "parallelisiert", "parallelisierte", "hat parallelisiert", None,
          "paralelizar"),
        V("sich zusammensetzen", "setzt sich zusammen", "setzte sich zusammen",
          "hat sich zusammengesetzt", "aus + D", "componerse de"),
        N("die", "Menge", "Mengen", "téc. conjunto (en matemáticas; normalmente: cantidad)"),
        N("die", "Compilerdirektive", "Compilerdirektiven", "directiva de compilador"),
        N("die", "Bibliotheksfunktion", "Bibliotheksfunktionen", "función de biblioteca"),
        N("die", "Umgebungsvariable", "Umgebungsvariablen", "variable de entorno"),
        X("portabel", "Adj.", "portable (funciona en distintas plataformas)", "ein portables Modell"),
        N("das", "Programmiermodell", "Programmiermodelle", "modelo de programación"),
        N("der", "Hersteller", "Hersteller", "fabricante"),
        X("zur Verfügung stellen", "Ausdruck", "poner a disposición, ofrecer (stellte, hat gestellt)"),
        V("erweitern", "erweitert", "erweiterte", "hat erweitert", "mit + D / um + A",
          "ampliar, extender (con)"),
        V("zugrunde liegen", "liegt zugrunde", "lag zugrunde", "hat zugrunde gelegen", None,
          "servir de base (die zugrunde liegende Sprache = el lenguaje de base)"),
        N("das", "Konstrukt", "Konstrukte", "construcción (de un lenguaje de programación)"),
        N("die", "Arbeitsaufteilung", "Arbeitsaufteilungen", "reparto del trabajo"),
        V("laufen", "läuft", "lief", "ist gelaufen", None,
          "téc. ejecutarse (un programa) (normalmente: correr, andar)", "parallel laufende Threads"),
        N("die", "Synchronisierung", "Synchronisierungen", "sincronización (= die Synchronisation)"),
        V("ermöglichen", "ermöglicht", "ermöglichte", "hat ermöglicht", None,
          "hacer posible, permitir (+ D: a alguien)"),
    ], [
        G("rel", "mit deren Hilfe … spezifiziert werden kann",
          "**Relativo en genitivo** (*deren* = cuya, de la cual) + **pasiva con modal** al final: "
          "«mediante la cual se puede especificar…»."),
        G("trenn", "trägt … zu der Lesbarkeit … bei",
          "**beitragen zu**: el prefijo *bei* llega al final. Si un verbo no tiene sentido, busca "
          "su prefijo al final de la oración: «contribuye… a la legibilidad»."),
        G("pasmod", "müssen nur … Anweisungen … eingefügt werden",
          "**Pasiva con modal**: modal conjugado + participio II + *werden* al final: «solo hay "
          "que insertar… instrucciones»."),
        G("infzu", "Das Ziel … ist es, … zur Verfügung zu stellen",
          "**es** anticipa un infinitivo con *zu*: «el objetivo es ofrecer…»."),
    ]),
    (2, "Einführung → 1.1 Merkmale von OpenMP", [
        X("gemeinsam", "Adj.", "téc. compartido (normalmente: común, juntos)",
          "gemeinsamer Zugriff = acceso compartido"),
        X("getrennt", "Adj.", "separado (de trennen)"),
        N("der", "Zugriff", "Zugriffe", "acceso (auf + A: a)"),
        V("steuern", "steuert", "steuerte", "hat gesteuert", None, "controlar, regular"),
        N("die", "Laufzeitumgebung", "Laufzeitumgebungen", "entorno de ejecución"),
        X("zahlreich", "Adj.", "numeroso"),
        V("unterstützen", "unterstützt", "unterstützte", "hat unterstützt", None,
          "téc. soportar, ser compatible con (normalmente: apoyar)"),
        X("entsprechend", "Adj.", "correspondiente, adecuado"),
        V("verfügen", "verfügt", "verfügte", "hat verfügt", "über + A", "disponer de, tener"),
        N("die", "Kommandozeilenoption", "Kommandozeilenoptionen", "opción de línea de comandos"),
        X("mit Hilfe + G", "Präp.", "con ayuda de, mediante (también: mithilfe)"),
        N("die", "Compileranweisung", "Compileranweisungen", "instrucción para el compilador"),
        V("anschalten / ausschalten", "schaltet an / aus", "schaltete an / aus",
          "hat an- / ausgeschaltet", None, "activar / desactivar"),
        V("vermuten", "vermutet", "vermutete", "hat vermutet", None,
          "suponer (vermuten lassen = hacer suponer)"),
        X("ausgezeichnet", "Adj./Adv.", "excelente(mente)"),
        X("lesbar", "Adj.", "legible (-bar = que se puede)"),
        V("herunterladen", "lädt herunter", "lud herunter", "hat heruntergeladen", None, "descargar"),
        X("ebenfalls", "Adv.", "también, igualmente"),
        V("erwähnen", "erwähnt", "erwähnte", "hat erwähnt", None, "mencionar"),
        N("die", "Gemeinschaft", "Gemeinschaften", "comunidad"),
        N("der", "Benutzer", "Benutzer", "usuario"),
        N("das", "Merkmal", "Merkmale", "característica, rasgo"),
        N("die", "ganze Zahl", "ganzen Zahlen", "número entero"),
        V("initialisieren", "initialisiert", "initialisierte", "hat initialisiert", None, "inicializar"),
        N("der", "Vorgeschmack", None, "anticipo, primera muestra (einen Vorgeschmack bieten)"),
        V("aufzeigen", "zeigt auf", "zeigte auf", "hat aufgezeigt", None,
          "mostrar, poner de manifiesto"),
        N("die", "Eigenschaft", "Eigenschaften", "propiedad, característica"),
        X("namens", "Präp.", "llamado, de nombre"),
        N("die", "Größe", "Größen", "téc. tamaño (normalmente: talla, estatura)"),
        V("begegnen", "begegnet", "begegnete", "ist begegnet", "+ D",
          "encontrarse con (¡dativo y «sein»!)"),
        N("der", "Ausdruck", "Ausdrücke", "expresión"),
    ], [
        G("rel", "mit Hilfe derer sich … lässt",
          "*derer* = genitivo del relativo tras preposición: «con ayuda de la cual». Es más "
          "frecuente *mit deren Hilfe* (p. 1)."),
        G("lassen", "… an- und ausschalten lässt",
          "**sich lassen + infinitivo** = «se puede»: «con la cual se puede activar y desactivar…»."),
        G("guion", "an- und ausschalten",
          "**Guion de ahorro**: el guion sustituye a la parte repetida (*an-* = *anschalten*). "
          "Igual: *Daten- und Kontrollflüsse* (p. 11), *Ein- und Ausgabe* (p. 18)."),
        G("otros", "Wie das „Open“ … vermuten lässt",
          "**vermuten lassen** (sin *sich*) = «dejar suponer»: «como ya deja suponer el “Open”…»."),
        G("part", "die – … ausgezeichnet lesbare – … Spezifikation",
          "**Atributo extendido**: entre *die* y *Spezifikation* va todo un inciso adjetival. "
          "Lee *die* → *Spezifikation* → vuelve atrás: «la especificación, excelentemente legible…»."),
        G("orden", "Ebenfalls erwähnt werden sollte die Webseite …",
          "**Sujeto al final**: participio y modal delante, el sujeto (*die Webseite*) detrás: "
          "«también debería mencionarse la web…»."),
    ]),
    (3, "1.1 Merkmale von OpenMP", [
        X("genannt", "Part. II", "llamado, denominado (de nennen)", "(auch Pragma genannte)"),
        V("bewirken", "bewirkt", "bewirkte", "hat bewirkt", None, "provocar, hacer que"),
        X("folgend", "Adj.", "siguiente"),
        N("die", "Schleife", "Schleifen", "téc. bucle (normalmente: lazo)"),
        V("ausführen", "führt aus", "führte aus", "hat ausgeführt", None, "téc. ejecutar"),
        N("der", "Schleifenkörper", "Schleifenkörper", "cuerpo del bucle"),
        V("zuweisen", "weist zu", "wies zu", "hat zugewiesen", "D + A", "asignar algo a"),
        X("zum Einsatz kommen", "Ausdruck", "emplearse, utilizarse (kam, ist gekommen)",
          "die zum Einsatz kommenden Threads"),
        N("der", "Bereich", "Bereiche", "téc. rango, zona (de un vector)"),
        V("zugreifen", "greift zu", "griff zu", "hat zugegriffen", "auf + A", "acceder a"),
        V("eingehen", "geht ein", "ging ein", "ist eingegangen", "auf + A",
          "tratar, entrar en (näher auf … eingehen = entrar en detalle)"),
        N("der", "Abstraktionsgrad", "Abstraktionsgrade", "nivel de abstracción"),
        X("explizit / implizit", "Adj./Adv.", "explícito / implícito"),
        X("separat", "Adj.", "separado, aparte"),
        N("die", "Zuordnung", "Zuordnungen", "asignación, correspondencia"),
        V("erfolgen", "erfolgt", "erfolgte", "ist erfolgt", None,
          "producirse, realizarse (¡con «sein»!)"),
        V("beeinflussen", "beeinflusst", "beeinflusste", "hat beeinflusst", None, "influir en (+ A)"),
        X("erhalten bleiben", "Ausdruck", "conservarse, mantenerse (blieb, ist geblieben)"),
        X("-fähig", "Suffix", "capaz de, compatible con (OpenMP-fähig = compatible con OpenMP)"),
        V("ausgeben", "gibt aus", "gab aus", "hat ausgegeben", None,
          "téc. emitir, mostrar (un mensaje) (normalmente: gastar)"),
        N("die", "Warnmeldung", "Warnmeldungen", "mensaje de advertencia"),
        N("die", "Compilierung", "Compilierungen", "compilación (también: Kompilierung)"),
        V("unterbrechen", "unterbricht", "unterbrach", "hat unterbrochen", None, "interrumpir"),
        X("obig", "Adj.", "anterior, de arriba (die obige Eigenschaft)"),
        V("folgen", "folgt", "folgte", "ist gefolgt", "aus + D",
          "deducirse de (aus … folgt, dass = de … se deduce que)"),
        X("schrittweise", "Adj./Adv.", "gradual, paso a paso"),
        X("wesentlich", "Adj./Adv.", "esencial, sustancialmente"),
        V("ergänzen", "ergänzt", "ergänzte", "hat ergänzt", None, "completar, añadir"),
        X("stets", "Adv.", "siempre (registro formal)"),
        X("lauffähig", "Adj.", "ejecutable, que funciona"),
        X("somit", "Adv.", "por tanto, así pues"),
        N("die", "Korrektheit", None, "corrección (el ser correcto)"),
        V("abschalten", "schaltet ab", "schaltete ab", "hat abgeschaltet", None,
          "desactivar, apagar", "man schaltet … ab (el «ab» está en la p. 4)"),
    ], [
        G("part", "die in Zeile 4 folgende for-Schleife",
          "**Atributo participial extendido** (participio I *folgend*): «el bucle for que sigue "
          "en la línea 4». Truco: artículo → sustantivo → retrocede."),
        G("pasimp", "auf welche Bereiche … zugegriffen wird",
          "**Pasiva impersonal** de un verbo con preposición (*zugreifen auf*): no hay sujeto: "
          "«a qué zonas… se accede»."),
        G("infzu", "Ohne auf Details … näher einzugehen, …",
          "**ohne … zu + infinitivo** muy largo: el infinitivo (*einzugehen*) llega al final del "
          "inciso: «sin entrar aquí en detalles…»."),
        G("gerund", "den sequentiell auszuführenden Anweisungen",
          "**Gerundivo**: *zu* + participio I como adjetivo = «las instrucciones que deben "
          "ejecutarse secuencialmente». En los separables, *zu* va dentro: *aus·zu·führend*."),
        G("otros", "Diese Anweisung ist es, die …",
          "**Oración escindida**: «es esta instrucción la que…»."),
        G("seinzu", "sind … einfach auf Korrektheit zu testen",
          "**sein + zu + infinitivo** = «se pueden» (o «hay que»): «es fácil comprobar su "
          "corrección»."),
    ]),
    (4, "1.1 Merkmale von OpenMP", [
        X("seriell", "Adj.", "serial, secuencial (= sequenziell)"),
        N("der", "Vergleichszweck", "Vergleichszwecke",
          "fin comparativo (zu Vergleichszwecken = para comparar)"),
        X("begrenzt", "Adj.", "limitado (lokal begrenzt = limitado a una zona)"),
        V("genügen", "genügt", "genügte", "hat genügt", None, "bastar, ser suficiente"),
        N("die", "Erweiterung", "Erweiterungen", "ampliación, extensión"),
        X("gering", "Adj.", "pequeño, escaso"),
        N("der", "Umfang", "Umfänge", "extensión, alcance (von geringem Umfang = pequeño)"),
        N("die", "Leistung", "Leistungen", "téc. rendimiento (normalmente: logro, prestación)"),
        N("die", "Leistungsoptimierung", "Leistungsoptimierungen", "optimización del rendimiento"),
        N("der", "Neuentwurf", "Neuentwürfe", "rediseño"),
        N("die", "Applikation", "Applikationen", "aplicación (= die Anwendung)"),
        X("portierbar", "Adj.", "portable (se puede llevar a otra plataforma)"),
        X("nahezu", "Adv.", "casi"),
        X("herstellerübergreifend", "Adj.", "común a varios fabricantes"),
        V("sich etablieren", "etabliert sich", "etablierte sich", "hat sich etabliert", None,
          "consolidarse, establecerse"),
        X("mittlerweile", "Adv.", "entretanto; a estas alturas, ya"),
        V("vorliegen", "liegt vor", "lag vor", "hat vorgelegen", None,
          "existir, estar disponible (in Version 2.5 vorliegen = estar en la versión 2.5)"),
        X("vor der Tür stehen", "Redewendung", "ser inminente, estar a la vuelta de la esquina"),
        N("die", "Umsetzung", "Umsetzungen", "implementación, puesta en práctica"),
        V("verarbeiten", "verarbeitet", "verarbeitete", "hat verarbeitet", None, "procesar"),
        V("anweisen", "weist an", "wies an", "hat angewiesen", "A + zu + Inf.",
          "ordenar a alguien que haga algo"),
        N("der", "Codeabschnitt", "Codeabschnitte", "sección de código"),
        N("die", "Klausel", "Klauseln", "cláusula"),
        N("das", "Verhalten", None, "comportamiento"),
        V("sich beziehen", "bezieht sich", "bezog sich", "hat sich bezogen", "auf + A",
          "referirse a"),
        X("gültig", "Adj.", "válido"),
    ], [
        G("otros", "Es stehen … Compiler … zur Verfügung",
          "**es de relleno**: ocupa la 1.ª posición; el sujeto real es *Compiler* (plural → "
          "*stehen*): «hay compiladores disponibles…»."),
        G("otros", "Auch wenn es … Unterschiede … gibt",
          "**auch wenn** = aunque (verbo al final)."),
        G("seinzu", "OpenMP ist einfach zu verwenden",
          "**sein + zu** con adjetivo: «OpenMP es fácil de usar»."),
        G("infzu", "weisen den Compiler an, … zu parallelisieren",
          "**anweisen + acusativo + zu + infinitivo**: «indican al compilador que paralelice…»."),
        G("rel", "…, auf die sie sich beziehen",
          "**Relativo con preposición** + verbo reflexivo (*sich beziehen auf*): «a la que se "
          "refieren»."),
    ]),
    (5, "1.1 Merkmale von OpenMP", [
        N("der", "Zeilenumbruch", "Zeilenumbrüche", "salto de línea"),
        X("insbesondere", "Adv.", "en particular, sobre todo"),
        X("öffnend", "Adj.", "de apertura (die öffnende Klammer)"),
        N("die", "Klammer", "Klammern",
          "téc. llave, paréntesis (geschweifte Klammer = llave { }) (normalmente: pinza)"),
        X("nachfolgend", "Adj.", "siguiente, posterior"),
        N("der", "Codeblock", "Codeblöcke", "bloque de código"),
        V("setzen", "setzt", "setzte", "hat gesetzt", None,
          "téc. colocar; fijar un parámetro (falsch gesetzte Klammer = llave mal colocada)"),
        X("hauptsächlich", "Adv.", "principalmente"),
        V("abfragen", "fragt ab", "fragte ab", "hat abgefragt", None, "consultar (un valor)"),
        X("bzw. (beziehungsweise)", "Konj.", "o bien; respectivamente"),
        X("darüber hinaus", "Adv.", "además"),
        V("enthalten", "enthält", "enthielt", "hat enthalten", None, "contener"),
        N("die", "Synchronisation", "Synchronisationen", "sincronización"),
        N("die", "Laufzeitbibliothek", "Laufzeitbibliotheken", "biblioteca de tiempo de ejecución"),
        N("die", "Headerdatei", "Headerdateien", "archivo de cabecera"),
        V("einbinden", "bindet ein", "band ein", "hat eingebunden", None, "incluir (un archivo)"),
        V("verzichten", "verzichtet", "verzichtete", "hat verzichtet", "auf + A",
          "prescindir de, renunciar a"),
        X("allerdings", "Adv.", "sin embargo; eso sí"),
        V("erzeugen", "erzeugt", "erzeugte", "hat erzeugt", None, "generar, producir"),
        X("beispielsweise", "Adv.", "por ejemplo"),
        X("ausführbar", "Adj.", "ejecutable"),
        V("sich empfehlen", "empfiehlt sich", "empfahl sich", "hat sich empfohlen", None,
          "ser recomendable (es empfiehlt sich, … zu …)"),
        V("inkludieren", "inkludiert", "inkludierte", "hat inkludiert", None, "incluir (= einbinden)"),
        X("ins Spiel kommen", "Ausdruck", "entrar en juego (kam, ist gekommen)"),
        V("entsprechen", "entspricht", "entsprach", "hat entsprochen", "+ D", "corresponder a"),
        X("bedingt", "Adj.", "condicional"),
        N("die", "Klammerung", "Klammerungen",
          "téc. encierre entre marcas (bedingte Klammerung: código entre #ifdef y #endif)"),
    ], [
        G("korr", "werden … dazu verwendet, … abzufragen",
          "**dazu … zu + infinitivo**: *dazu* anticipa la finalidad: «se usan para consultar…»."),
        G("v1", "Möchte man …, so muss …",
          "**Condicional sin «wenn»**: el verbo va primero = «si uno quiere…». La principal "
          "suele empezar con *so* o *dann*."),
        G("pasimp", "kann auf das Einbinden … verzichtet werden",
          "**Pasiva impersonal** con *verzichten auf*: «se puede prescindir de incluir…». "
          "*das Einbinden* = infinitivo sustantivado («el incluir»)."),
        G("otros", "Es empfiehlt sich also, … zu inkludieren",
          "**es empfiehlt sich + zu**: «es recomendable incluir…»."),
        G("gerund", "für alle zu parallelisierenden Programme",
          "**Gerundivo** (ver p. 3): «para todos los programas que se vayan a paralelizar»."),
        G("v1", "Sollte ein Compiler … nicht unterstützen, so …",
          "**sollte** al principio = «si por casualidad…»: condicional con matiz de posibilidad."),
        G("otros", "bei aktivierter OpenMP-Option",
          "**bei + participio adjetivado** (estilo nominal): «con la opción activada»."),
    ]),
    (6, "1.1 → 1.1.1 OpenMP-fähige Compiler", [
        X("so dass / sodass", "Konj.", "de modo que (verbo al final)"),
        X("ausgewählt", "Adj.", "seleccionado"),
        V("einbeziehen", "bezieht ein", "bezog ein", "hat einbezogen", "in + A",
          "incluir en, tener en cuenta"),
        V("ausschließen", "schließt aus", "schloss aus", "hat ausgeschlossen", "von + D", "excluir de"),
        N("das", "Codestück", "Codestücke", "fragmento de código"),
        N("der", "Anspruch", "Ansprüche",
          "pretensión (ohne Anspruch auf Vollständigkeit = sin pretender ser exhaustivo)"),
        N("die", "Vollständigkeit", None, "exhaustividad, integridad"),
        N("der", "Schalter", "Schalter", "téc. opción (flag) (normalmente: interruptor; ventanilla)"),
        V("hinausgehen", "geht hinaus", "ging hinaus", "ist hinausgegangen", "über + A",
          "ir más allá de"),
        N("der", "Zweck", "Zwecke", "fin, propósito (für nicht kommerzielle Zwecke)"),
        X("erhältlich", "Adj.", "disponible, que se puede conseguir (frei erhältlich = gratuito)"),
        X("zumindest", "Adv.", "al menos"),
        N("die", "Testversion", "Testversionen", "versión de prueba"),
        V("übersetzen", "übersetzt", "übersetzte", "hat übersetzt", None,
          "téc. compilar (normalmente: traducir)"),
    ], [
        G("pasmod", "so dass … einbezogen oder … ausgeschlossen werden können",
          "**so dass** (verbo al final) + **pasiva con modal**: «de modo que puedan incluirse o "
          "excluirse…»."),
        G("lassen", "lässt sich über dessen Eigenschaften … aktivieren",
          "**sich lassen** = se puede. *dessen* = «sus» (de ese proyecto); se usa en lugar de "
          "*seine* para evitar ambigüedades."),
        G("otros", "(ohne Anspruch auf Vollständigkeit)",
          "**Fórmula fija**: «sin pretensión de exhaustividad»."),
        G("v1", "Soll OpenMP zum Einsatz kommen, muss …",
          "**Condicional sin «wenn»** con *sollen*: «si se quiere usar OpenMP, hay que…»."),
    ]),
    (7, "1.1.1 → «Über dieses Buch» → 1.2 Parallele Programmierung", [
        X("o. g. (oben genannt)", "Abk.", "arriba mencionado"),
        X("vorig", "Adj.", "anterior (im vorigen Abschnitt)"),
        N("der", "Abschnitt", "Abschnitte", "apartado, sección"),
        X("etwa", "Adv.", "aquí: por ejemplo (normalmente: aproximadamente)"),
        N("die", "Zeitmessung", "Zeitmessungen",
          "medición del tiempo (zu Zeitmessungszwecken = para medir tiempos)"),
        V("betrachten", "betrachtet", "betrachtete", "hat betrachtet", "als + A",
          "considerar, examinar (como)"),
        V("voraussetzen", "setzt voraus", "setzte voraus", "hat vorausgesetzt", None,
          "presuponer, requerir"),
        N("die", "Kenntnis", "Kenntnisse", "conocimiento (Kenntnisse in + D = conocimientos de)"),
        V("behandeln", "behandelt", "behandelte", "hat behandelt", None,
          "téc. tratar (un tema) (normalmente: tratar a un paciente)"),
        N("der", "Zeitpunkt", "Zeitpunkte", "momento"),
        N("die", "Abfassung", "Abfassungen",
          "redacción (zum Zeitpunkt der Abfassung = cuando se escribió)"),
        N("der", "Entwurf", "Entwürfe", "borrador; diseño"),
        N("die", "Öffentlichkeit", None, "el público, la opinión pública"),
        X("zugänglich", "Adj.", "accesible (zugänglich machen = hacer público)"),
        X("demnach", "Adv.", "según esto, por consiguiente"),
        X("zum Teil", "Adv.", "en parte"),
        X("vorab", "Adv.", "de antemano, previamente"),
        N("die", "Berücksichtigung", None,
          "consideración (Berücksichtigung finden = tenerse en cuenta)"),
        X("vorliegend", "Adj.", "presente (im vorliegenden Buch = en este libro)"),
        X("verbleibend", "Adj.", "restante"),
        X("einführend", "Adj.", "introductorio"),
        N("der", "Überblick", "Überblicke", "visión general, panorama"),
        N("die", "Parallelverarbeitung", None, "procesamiento en paralelo"),
        N("der", "Mehrkernprozessor", "Mehrkernprozessoren",
          "procesador multinúcleo (= der Multicoreprozessor)"),
        N("die", "Leistungsmessung", "Leistungsmessungen", "medición del rendimiento"),
    ], [
        G("v1", "Werden die o. g. Compileroptionen aktiviert, wird …",
          "**Condicional sin «wenn» en pasiva**: *Werden … aktiviert* = «si se activan…»; la "
          "principal empieza también por el verbo (*wird … definiert*)."),
        G("part", "die im vorigen Abschnitt beschriebene Variable",
          "**Atributo participial** (participio II): «la variable descrita en el apartado "
          "anterior». Igual: *ein mit OpenMP parallelisiertes Programm*."),
        G("infzu", "so genügt es, … neu zu übersetzen",
          "**es genügt, … zu** = «basta con volver a compilar…»."),
        G("pasmod", "… zugänglich gemacht worden",
          "**Pluscuamperfecto pasivo** (*war … gemacht worden*): «acababa de hacerse público»."),
        G("fvg", "finden … bereits Berücksichtigung",
          "**Verbo funcional**: *Berücksichtigung finden* = «tenerse en cuenta»."),
    ]),
    (8, "1.2 → 1.2.1 Prozesse und Threads", [
        X("vertraut", "Adj.", "familiarizado (mit + D: con)"),
        V("einsteigen", "steigt ein", "stieg ein", "ist eingestiegen", "in + A",
          "entrar en, empezar con (normalmente: subir a un vehículo)"),
        V("weiterblättern", "blättert weiter", "blätterte weiter", "hat weitergeblättert", None,
          "pasar páginas, saltar (a un capítulo)"),
        X("ausführlich", "Adj.", "detallado (ausführlicher = más detallado)"),
        N("die", "Behandlung", "Behandlungen", "téc. tratamiento (de un tema)"),
        N("die", "Reihe", "Reihen", "téc. colección (de libros) (normalmente: fila)"),
        V("bezeichnen", "bezeichnet", "bezeichnete", "hat bezeichnet", "als + A", "denominar, llamar"),
        N("das", "Betriebssystem", "Betriebssysteme", "sistema operativo"),
        X("im Gegensatz zu + D", "Präp.", "a diferencia de"),
        N("die", "Festplatte", "Festplatten", "disco duro"),
        X("es handelt sich um + A", "Ausdruck", "se trata de"),
        V("vortäuschen", "täuscht vor", "täuschte vor", "hat vorgetäuscht", None,
          "simular, aparentar"),
        X("mehrfach", "Adv.", "varias veces"),
        N("der", "Zeitraum", "Zeiträume", "período de tiempo"),
        V("sich ergeben", "ergibt sich", "ergab sich", "hat sich ergeben", None, "resultar, surgir"),
        N("der", "Eindruck", "Eindrücke", "impresión"),
        N("die", "Gleichzeitigkeit", None, "simultaneidad"),
        V("regeln", "regelt", "regelte", "hat geregelt", None, "regular, organizar"),
        X("zeitlich", "Adj.", "temporal"),
        X("eindeutig", "Adj.", "unívoco, único (sin ambigüedad)"),
        N("die", "Identifikationsnummer", "Identifikationsnummern", "número de identificación"),
        N("der", "Programmschrittzähler", "Programmschrittzähler",
          "contador de programa (= Programmzähler, Befehlszähler)"),
        N("der", "Registerwert", "Registerwerte", "valor de registro"),
        N("der", "Stack", "Stacks", "pila (en alemán también: der Stapelspeicher)"),
        N("der", "Speicher", "Speicher", "téc. memoria (normalmente: almacén)"),
        N("der", "Speicherbereich", "Speicherbereiche", "área de memoria"),
        N("die", "Rücksprungadresse", "Rücksprungadressen", "dirección de retorno"),
        N("der", "Funktionsparameter", "Funktionsparameter", "parámetro de una función"),
    ], [
        G("part", "Mit diesen Themen bereits vertraute Leser",
          "**Atributo extendido** con adjetivo: «los lectores ya familiarizados con estos temas»."),
        G("orden", "Als Prozess bezeichnet man ein Programm, das …",
          "**Complemento delante**: *als X bezeichnet man Y* = «se llama X a Y»."),
        G("otros", "handelt es sich … um eine aktive Instanz",
          "**es handelt sich um + A** = «se trata de»."),
        G("v1", "Können in einem System … aktiv sein, bezeichnet man …",
          "**Condicional sin «wenn»**: «si en un sistema pueden estar activos…, se llama…»."),
        G("korr", "kommt daher, dass … · dadurch …, dass …",
          "**Correlatos**: *daher kommen, dass* = «se debe a que»; *dadurch, dass* = «por el "
          "hecho de que»."),
    ]),
    (9, "1.2.1 Prozesse und Threads", [
        N("der", "Datenbereich", "Datenbereiche", "segmento de datos"),
        V("ablegen", "legt ab", "legte ab", "hat abgelegt", None,
          "téc. guardar, almacenar (normalmente: quitarse la ropa)"),
        N("der", "Heap", "Heaps", "montículo, heap (memoria dinámica)"),
        V("anlegen", "legt an", "legte an", "hat angelegt", None,
          "téc. crear (variables, procesos) (normalmente: colocar; invertir dinero)"),
        N("das", "Mittel", "Mittel", "medio, recurso"),
        N("der", "Systemaufruf", "Systemaufrufe", "llamada al sistema"),
        X("zur Ausführung gelangen", "Ausdruck", "llegar a ejecutarse (gelangte, ist gelangt)"),
        X("derzeit", "Adv.", "actualmente, en ese momento"),
        V("sichern", "sichert", "sicherte", "hat gesichert", None,
          "téc. guardar (una copia) (normalmente: asegurar)"),
        X("indem", "Konj.", "modo → gerundio en español («guardando…»)"),
        X("sogenannt", "Adj.", "llamado, denominado"),
        N("der", "Prozesskontrollblock", "Prozesskontrollblöcke", "bloque de control de proceso"),
        V("wiederherstellen", "stellt wieder her", "stellte wieder her", "hat wiederhergestellt",
          None, "restaurar"),
        X("sobald", "Konj.", "en cuanto, tan pronto como"),
        X("an der Reihe sein", "Ausdruck", "tocarle a uno (el turno)"),
        V("umschalten", "schaltet um", "schaltete um", "hat umgeschaltet", None,
          "conmutar, cambiar (das Umschalten = el cambio)"),
        N("der", "Ausführungsstrang", "Ausführungsstränge", "hilo de ejecución"),
        X("etwaig", "Adj.", "eventual, posible (etwaige weitere Ressourcen)"),
        V("sich (D) etw. teilen", "teilt sich", "teilte sich", "hat sich geteilt", "mit + D",
          "compartir algo con"),
        X("auf einmal", "Adv.", "a la vez (también: de repente)"),
        V("erhöhen", "erhöht", "erhöhte", "hat erhöht", None, "aumentar"),
        N("die", "Reaktionsgeschwindigkeit", "Reaktionsgeschwindigkeiten", "velocidad de respuesta"),
        N("die", "Benutzereingabe", "Benutzereingaben", "entrada del usuario"),
        N("die", "Oberfläche", "Oberflächen",
          "téc. interfaz (grafische Oberfläche) (normalmente: superficie)"),
        X("gemeinsam genutzt", "Adj.", "compartido"),
        N("der", "Adressraum", "Adressräume", "espacio de direcciones"),
    ], [
        G("zustand", "in dem globale Variablen abgelegt sind",
          "**Pasiva de estado** (*sein* + participio II): el resultado, no la acción: «en el que "
          "están almacenadas las variables globales»."),
        G("otros", "Mittel zum Anlegen von Prozessen",
          "**zum + infinitivo sustantivado** = para + infinitivo: «medios para crear procesos»."),
        G("part", "des derzeit dort ausgeführten Prozesses Q",
          "**Atributo participial** en genitivo: «del proceso Q que se está ejecutando allí»."),
        G("otros", "…, indem alle … Elemente … abgelegt werden",
          "**indem** = modo → gerundio: «guardando todos los elementos…»."),
        G("infzu", "an der Reihe ist, ausgeführt zu werden",
          "**Infinitivo pasivo con zu**: «en cuanto le vuelva a tocar ser ejecutado»."),
        G("orden", "Die anderen Elemente … teilt er sich mit …",
          "**Objeto al principio**: la lista de elementos es el acusativo y el sujeto (*er*, el "
          "hilo) va detrás del verbo: «los demás elementos los comparte con…»."),
    ]),
    (10, "1.2.1 → 1.2.2 Parallele Hardwarearchitekturen", [
        X("ökonomisch", "Adj.", "económico; aquí: eficiente (ökonomischer = más eficiente)"),
        V("vollziehen", "vollzieht", "vollzog", "hat vollzogen", None, "realizar, llevar a cabo"),
        X("statt", "Präp./Konj.", "en lugar de (statt … zu + Inf.)"),
        X("tatsächlich", "Adj./Adv.", "real(mente), efectivamente"),
        V("ausnutzen", "nutzt aus", "nutzte aus", "hat ausgenutzt", None, "aprovechar (al máximo)"),
        N("die", "Parallelausführung", "Parallelausführungen", "ejecución en paralelo"),
        X("eine Rolle spielen", "Ausdruck",
          "importar, tener importancia (keine Rolle spielen = dar igual)"),
        N("das", "Threadmodell", "Threadmodelle", "modelo de hilos"),
        V("umsetzen", "setzt um", "setzte um", "hat umgesetzt", None,
          "implementar, llevar a la práctica"),
        X("im Sinne + G", "Ausdruck", "en el sentido de, según (im Sinne von OpenMP)"),
        N("der", "Kontrollfluss", "Kontrollflüsse", "flujo de control"),
        X("markiert", "Adj.", "marcado"),
        N("die", "Faustregel", "Faustregeln", "regla empírica, regla general"),
        X("wonach", "Relativadverb", "según el / la cual"),
        X("handelsüblich", "Adj.", "corriente, de los que se venden normalmente"),
        V("sich verdoppeln", "verdoppelt sich", "verdoppelte sich", "hat sich verdoppelt", None,
          "duplicarse"),
        N("die", "Beobachtung", "Beobachtungen", "observación"),
        X("erstmals", "Adv.", "por primera vez"),
        V("erfahren", "erfährt", "erfuhr", "hat erfahren", None,
          "téc. sufrir, experimentar (cambios) (normalmente: enterarse)"),
        N("die", "Abwandlung", "Abwandlungen", "variación, modificación"),
        N("die", "Gültigkeit", None, "validez"),
        X("in der jüngeren Vergangenheit", "Ausdruck", "en el pasado reciente"),
        V("einhergehen", "geht einher", "ging einher", "ist einhergegangen", "mit + D",
          "ir acompañado de, conllevar"),
        N("die", "Erhöhung", "Erhöhungen", "aumento"),
        N("die", "Leistungssteigerung", "Leistungssteigerungen", "aumento del rendimiento"),
        N("die", "Taktrate", "Taktraten", "frecuencia de reloj (= die Taktfrequenz)"),
        V("erzielen", "erzielt", "erzielte", "hat erzielt", None, "lograr, obtener"),
        N("die", "Gültigkeitsdauer", None, "período de validez"),
        V("vorhersagen", "sagt vorher", "sagte vorher", "hat vorhergesagt", None,
          "predecir, pronosticar"),
    ], [
        G("infzu", "ist es ökonomischer, … statt zwischen Prozessen zu vollziehen",
          "**es ist + adjetivo, … zu** con **statt**: «es más eficiente hacer… entre hilos en "
          "lugar de entre procesos»."),
        G("rel", "…, mit Hilfe dessen …",
          "**Relativo en genitivo** masculino/neutro (se refiere a OpenMP): «con ayuda del cual»."),
        G("orden", "Um diese … Details … muss er sich nicht kümmern",
          "**Complemento preposicional delante** (*sich kümmern um*): «de estos detalles no tiene "
          "que ocuparse»."),
        G("rel", "die Faustregel, wonach sich …",
          "**wonach** = «según la cual» (adverbio relativo; verbo al final)."),
        G("otros", "„Moore’sches Gesetz“",
          "**Adjetivo de nombre propio**: nombre + *-sch* + terminación: *das Moore’sche Gesetz*, "
          "*nach dem Amdahl’schen Gesetz* = «la ley de Moore / según la ley de Amdahl»."),
        G("part", "die mit der Erhöhung … einhergehende Leistungssteigerung",
          "**Atributo con participio I** (*einhergehend*): «el aumento de rendimiento que "
          "acompaña al incremento…»."),
        G("konj1", "bis eine Grenze erreicht sei",
          "**Subjuntivo I** (estilo indirecto: lo dice Moore, no el autor): «hasta que se "
          "alcanzara un límite»."),
    ]),
    (11, "1.2.2 Parallele Hardwarearchitekturen", [
        N("die", "Beschränkung", "Beschränkungen", "limitación, restricción"),
        X("dagegen sprechen", "Ausdruck", "estar en contra, impedirlo (sprach, hat gesprochen)"),
        X("zunehmend", "Adj./Adv.", "creciente, cada vez más"),
        N("die", "Ebene", "Ebenen", "nivel (auf Prozessorebene = a nivel del procesador)"),
        N("der", "Designansatz", "Designansätze", "enfoque de diseño"),
        V("umfassen", "umfasst", "umfasste", "hat umfasst", None, "abarcar, comprender"),
        X("u. a. (unter anderem)", "Abk.", "entre otros"),
        X("sowie", "Konj.", "así como, y también"),
        N("der", "Prozessorkern", "Prozessorkerne", "núcleo del procesador"),
        X("jeweils", "Adv.", "cada uno, respectivamente"),
        N("die", "Recheneinheit", "Recheneinheiten", "unidad de cálculo"),
        V("vertrauen", "vertraut", "vertraute", "hat vertraut", "auf + A",
          "confiar en (darauf vertrauen, dass = confiar en que)"),
        X("allein(e)", "Adv.", "solo, únicamente"),
        X("verfügbar", "Adj.", "disponible"),
        N("die", "Rechenleistung", "Rechenleistungen", "potencia de cálculo"),
        N("die", "Verbreitung", None, "difusión, expansión"),
        N("die", "Gegebenheit", "Gegebenheiten", "circunstancia, condición"),
        V("anpassen", "passt an", "passte an", "hat angepasst", "an + A / + D", "adaptar a"),
        N("das", "Rüstzeug", None, "herramientas, bagaje (de conocimientos)"),
        X("ein jeder", "Pron.", "cada (uno) (eines jeden Programmierers = de todo programador)"),
        X("inkrementell", "Adj./Adv.", "incremental, paso a paso"),
        V("darstellen", "stellt dar", "stellte dar", "hat dargestellt", None,
          "téc. suponer, constituir (normalmente: representar)"),
        V("einordnen", "ordnet ein", "ordnete ein", "hat eingeordnet", "in + A", "clasificar en"),
        N("der", "Rechner", "Rechner", "ordenador, computadora"),
        X("weder … noch", "Konj.", "ni … ni"),
        N("der", "Datenstrom", "Datenströme", "flujo de datos"),
    ], [
        G("korr", "konnte man darauf vertrauen, dass …",
          "**Correlato** *darauf … dass* (*vertrauen auf*): «se podía confiar en que…»."),
        G("infzu", "Um … auszunutzen, ist es … notwendig geworden, … anzupassen",
          "**um … zu** (finalidad) + *es ist … geworden* (perfecto de *werden*) + infinitivos con "
          "*zu* intercalado en separables (*an·zu·passen*): «para aprovechar…, se ha vuelto "
          "necesario adaptar…»."),
        G("trenn", "stellt damit eine attraktive Möglichkeit … dar",
          "**darstellen**: el prefijo *dar* va al final: «constituye así una opción atractiva»."),
        G("part", "eine der … von Michael J. Flynn vorgeschlagenen Kategorien",
          "**Atributo participial** con agente (*von …*): «una de las categorías propuestas por "
          "Flynn»."),
        G("otros", "weder auf der Daten- noch auf der Anweisungsebene",
          "**weder … noch** = ni … ni, con **guion de ahorro** (*Daten-* = *Datenebene*)."),
    ]),
    (12, "1.2.2 Parallele Hardwarearchitekturen", [
        N("die", "Grafikkarte", "Grafikkarten", "tarjeta gráfica"),
        X("mittels + G", "Präp.", "mediante, por medio de"),
        V("einführen", "führt ein", "führte ein", "hat eingeführt", None,
          "introducir, lanzar (al mercado)"),
        N("der", "Befehl", "Befehle", "téc. instrucción de máquina (normalmente: orden)"),
        N("die", "Befehlserweiterung", "Befehlserweiterungen",
          "extensión del juego de instrucciones"),
        X("eher", "Adv.", "más bien"),
        X("bislang", "Adv.", "hasta ahora"),
        N("die", "Massenfertigung", None, "producción en masa"),
        X("Verwendung finden", "Ausdruck", "usarse, emplearse (fand, hat gefunden)"),
        X("voneinander", "Adv.", "el uno del otro, entre sí"),
        X("hierfür", "Adv.", "para esto, de esto"),
        X("verteilt", "Adj.", "distribuido"),
        X("heutig", "Adj.", "actual, de hoy"),
        X("wiederum", "Adv.", "a su vez"),
        V("einteilen", "teilt ein", "teilte ein", "hat eingeteilt", "in + A",
          "dividir, clasificar en"),
        N("die", "Unterklasse", "Unterklassen", "subclase"),
        X("jene", "Pron.", "aquellos, aquellas"),
        X("vorhanden", "Adj.", "existente, disponible"),
        X("physikalisch", "Adj.", "físico, de la física (≠ physisch = corporal)"),
        X("letzterer", "Adj.", "este último (in letzterem Fall = en este último caso)"),
        V("anmerken", "merkt an", "merkte an", "hat angemerkt", None, "señalar, observar"),
        N("die", "Parallelitätsebene", "Parallelitätsebenen", "nivel de paralelismo"),
    ], [
        G("fvg", "… Verwendung gefunden hat",
          "**Verbo funcional**: *Verwendung finden* = «usarse»: «que hasta ahora no se ha usado…»."),
        G("part", "voneinander unabhängig … arbeitenden Prozessoren",
          "**Atributo participial largo** (participio I): «procesadores que trabajan "
          "independientemente sobre datos distintos»."),
        G("otros", "Jene mit … und jene mit … · In letzterem Fall",
          "*jene* = «aquellas»; *letzterer* = «el último mencionado»: «en este último caso»."),
        G("konj1", "Es sei noch angemerkt, dass …",
          "**Subjuntivo I** impersonal, fórmula académica: «cabe señalar que…»."),
        G("zustand", "… kombiniert sein können",
          "**Pasiva de estado con modal**: «pueden estar combinados»."),
    ]),
    (13, "1.2.2 → 1.2.3 Leistungsmessung", [
        X("äußer-", "Adj.", "exterior (auf einer äußeren Ebene)"),
        X("d. h. (das heißt)", "Abk.", "es decir"),
        N("die", "Programminstanz", "Programminstanzen", "instancia del programa"),
        N("der", "Laufzeitvorteil", "Laufzeitvorteile", "ventaja en tiempo de ejecución"),
        X("abzüglich + G", "Präp.", "descontando, menos"),
        N("der", "Mehraufwand", None, "trabajo adicional, sobrecoste (overhead)"),
        N("die", "Verwaltung", "Verwaltungen", "gestión, administración"),
        V("heranziehen", "zieht heran", "zog heran", "hat herangezogen", None,
          "recurrir a, utilizar (para comparar, juzgar)"),
        N("die", "Kenngröße", "Kenngrößen", "indicador, magnitud característica"),
        N("die", "Beschleunigung", "Beschleunigungen", "aceleración (speedup)"),
        N("die", "Effizienz", None, "eficiencia"),
        N("der", "Quotient", "Quotienten", "cociente (n-Deklination: des Quotienten)"),
        N("die", "Laufzeit", "Laufzeiten", "tiempo de ejecución"),
        N("das", "Verhältnis", "Verhältnisse", "téc. proporción, razón (normalmente: relación)"),
        N("die", "Ausführungsdauer", None, "duración de la ejecución (= die Ausführungszeit)"),
        V("beschleunigen", "beschleunigt", "beschleunigte", "hat beschleunigt", None, "acelerar"),
        V("aussagen", "sagt aus", "sagte aus", "hat ausgesagt", "über + A",
          "decir, indicar (nichts darüber aussagen = no decir nada sobre ello)"),
        N("der", "Parallelbetrieb", None, "funcionamiento en paralelo"),
        N("das", "Viertel", "Viertel", "cuarto (ein Viertel so lange = la cuarta parte del tiempo)"),
        X("kommen auf + A", "Ausdruck", "llegar a, alcanzar (un valor)"),
    ], [
        G("konj2", "… könnten auf einem Cluster verteilt ausgeführt werden",
          "**Subjuntivo II** de posibilidad + pasiva: «podrían ejecutarse repartidas en un "
          "clúster»."),
        G("orden", "Bleibt die Frage, welchen Laufzeitvorteil …",
          "**Verbo al principio sin es** (= *Es bleibt die Frage*): «queda la pregunta de qué "
          "ventaja…»."),
        G("trenn", "zieht man die beiden Kenngrößen … heran",
          "**heranziehen**: prefijo al final: «se recurre a los dos indicadores…»."),
        G("korr", "sagt … noch nichts darüber aus, wie gut …",
          "**aussagen über** + correlato *darüber* + pregunta indirecta: «no dice nada sobre lo "
          "bien que…»."),
        G("konj2", "dessen … Ausführung … ein Viertel so lange dauert wie …, käme …",
          "**dessen** (cuya) + comparación *so lange wie* + **subjuntivo II** *käme* (de "
          "*kommen*): «un algoritmo cuya ejecución durara la cuarta parte… llegaría a…»."),
    ]),
    (14, "1.2.3 → 1.2.4 Das Amdahl’sche Gesetz", [
        V("betragen", "beträgt", "betrug", "hat betragen", None, "ascender a, ser (una cantidad)",
          "betrüge (subjuntivo II)"),
        X("dennoch", "Adv.", "sin embargo, aun así"),
        N("die", "Obergrenze", "Obergrenzen", "límite superior"),
        V("auftreten", "tritt auf", "trat auf", "ist aufgetreten", None, "aparecer, producirse"),
        X("um + A", "Präp.", "en (diferencia): um einen Faktor = en un factor"),
        N("der", "Cache-Speicher", "Cache-Speicher", "memoria caché (= der Cache, Pl. die Caches)"),
        N("die", "Gesamtgröße", "Gesamtgrößen", "tamaño total"),
        V("halten", "hält", "hielt", "hat gehalten", None,
          "téc. mantener, conservar datos (normalmente: sostener; parar)"),
        N("die", "Speicherzugriffszeit", "Speicherzugriffszeiten", "tiempo de acceso a memoria"),
        V("profitieren", "profitiert", "profitierte", "hat profitiert", "von + D",
          "beneficiarse de (davon profitieren, dass)"),
        N("der", "Mitläufer", "Mitläufer",
          "compañero; aquí: los otros hilos (normalmente: simpatizante pasivo)"),
        X("unmittelbar", "Adj./Adv.", "directo, inmediatamente"),
        N("die", "Berechnung", "Berechnungen", "cálculo"),
        N("die", "Vorarbeit", "Vorarbeiten", "trabajo previo"),
        X("sich Gedanken machen", "Ausdruck", "reflexionar (zu / über + A: sobre)"),
        N("die", "Grundlage", "Grundlagen", "fundamento, base"),
        V("feststellen", "stellt fest", "stellte fest", "hat festgestellt", None,
          "constatar, comprobar"),
        V("beschränken", "beschränkt", "beschränkte", "hat beschränkt", None,
          "limitar (nach oben beschränken = acotar superiormente)"),
        X("grundsätzlich", "Adj./Adv.", "por principio, en esencia"),
        X("… Natur sein", "Ausdruck", "ser de naturaleza … (sequenzieller Natur = de naturaleza "
                                      "secuencial)"),
        X("parallelisierbar", "Adj.", "paralelizable (-bar = que se puede)"),
        V("schließen", "schließt", "schloss", "hat geschlossen", "aus + D",
          "concluir, deducir de (daraus schließen, dass)"),
        N("die", "Steigerung", "Steigerungen", "aumento"),
        X("im gleichen Maß", "Ausdruck", "en la misma medida"),
        V("mitwachsen", "wächst mit", "wuchs mit", "ist mitgewachsen", None, "crecer a la par"),
        X("benannt nach + D", "Part. II", "llamado en honor a (benennen, benannte, hat benannt)"),
    ], [
        G("konj2", "betrüge · ausnutzte · wäre · hätte",
          "**Subjuntivo II** (caso hipotético): *betrüge* (de *betragen*) = «sería»; *ausnutzte* "
          "= «aprovechara»; *wäre* = «fuera»; *hätte* = «tendría»."),
        G("rel", "…, der … ausnutzte und dessen Beschleunigung … wäre",
          "**Dos relativas coordinadas**: *der* (sujeto) y *dessen* (cuyo): «que aprovechara… y "
          "cuya aceleración fuera…»."),
        G("rel", "…, was die Speicherzugriffszeiten reduziert",
          "**was** se refiere a toda la oración anterior: «lo cual reduce…»."),
        G("korr", "können davon profitieren, dass …",
          "**Correlato** *davon … dass* (*profitieren von*): «se benefician de que…»."),
        G("part", "der von Multiprozessorarchitekturen benötigte Mehraufwand",
          "**Atributo participial** con agente: «el sobrecoste que necesitan las arquitecturas "
          "multiprocesador»."),
        G("konj1", "Darüber hinaus sei dieser Mehraufwand … · nur möglich sei",
          "**Subjuntivo I = estilo indirecto**: es la opinión de Amdahl, no la del autor: "
          "«además, (según él) este sobrecoste sería…»."),
        G("part", "Das nach ihm benannte Amdahl’sche Gesetz",
          "**Atributo participial**: «la ley de Amdahl, que lleva su nombre»."),
        G("otros", "läßt · schloß (p. 18) · Kontrollfluß",
          "**Ortografía antigua** (antes de 1996): *ß* tras vocal breve. Hoy: *lässt, schloss, "
          "Kontrollfluss*."),
    ]),
    (15, "1.2.4 Das Amdahl’sche Gesetz", [
        N("der", "Anteil", "Anteile", "fracción, parte, proporción"),
        X("unveränderlich", "Adj.", "invariable"),
        V("normieren", "normiert", "normierte", "hat normiert", "auf + A", "normalizar a"),
        N("der", "Zeitanteil", "Zeitanteile", "fracción de tiempo"),
        X("unverändert", "Adj.", "sin cambios"),
        X("unter Vernachlässigung + G", "Ausdruck", "sin tener en cuenta, despreciando"),
        X("es gilt", "Ausdruck", "téc. se cumple (en matemáticas) (gelten: normalmente valer)"),
        X("erreichbar", "Adj.", "alcanzable"),
        V("besagen", "besagt", "besagte", "hat besagt", None, "decir, afirmar (una ley, una regla)"),
        N("die", "Abbildung", "Abbildungen", "figura (abreviatura: Abb.)"),
        V("anzeigen", "zeigt an", "zeigte an", "hat angezeigt", None, "mostrar, indicar",
          "zeigt … an"),
        X("in Abhängigkeit von + D", "Ausdruck", "en función de"),
        N("der", "Codeanteil", "Codeanteile", "fracción de código"),
    ], [
        G("part", "durch die im Code verbleibenden seriellen Anteile",
          "**Atributo participial**: «por las partes seriales que quedan en el código»."),
        G("konj1", "Sei σ der … Anteil",
          "**Subjuntivo I en definiciones** matemáticas: «Sea σ la fracción…». Igual: "
          "*Sei … bezeichnet* (p. 18)."),
        G("part", "Die serielle auf 1 normierte Ausführungszeit",
          "**Atributo participial**: «el tiempo de ejecución serial normalizado a 1»."),
        G("otros", "unter Vernachlässigung des …",
          "**Estilo nominal**: *unter* + sustantivo en *-ung* + genitivo = «sin tener en cuenta "
          "el…»."),
        G("v1", "Werden beispielsweise 10 % … ausgeführt, … besagt …",
          "**Condicional sin «wenn» en pasiva**: «si se ejecuta, por ejemplo, el 10 %…, la ley "
          "dice…»."),
        G("trenn", "Abbildung 1.1 zeigt … an",
          "**anzeigen**: el prefijo *an* llega unas 25 palabras después: «la figura 1.1 muestra…»."),
    ]),
    (16, "Abb. 1.1 → 1.2.5 Das Gustafson’sche Gesetz", [
        N("der", "Idealfall", "Idealfälle", "caso ideal"),
        N("die", "Sichtweise", "Sichtweisen", "punto de vista, perspectiva"),
        X("zum Ausdruck bringen", "Ausdruck", "expresar (brachte, hat gebracht)"),
        X("grundlegend", "Adj.", "fundamental, básico"),
        X("gegenüber + D", "Präp.", "frente a, respecto a"),
        V("vernachlässigen", "vernachlässigt", "vernachlässigte", "hat vernachlässigt", None,
          "descuidar, no tener en cuenta"),
        X("wachsend", "Adj.", "creciente"),
        X("höchstens", "Adv.", "como mucho, a lo sumo"),
        N("der", "Forschungszweck", "Forschungszwecke",
          "fin de investigación (zu Forschungszwecken)"),
        X("gegeben", "Adj.", "dado (ein Problem gegebener Größe = de tamaño dado)"),
        X("verschieden viele", "Ausdruck", "distintas cantidades de"),
        X("stattdessen", "Adv.", "en su lugar, en cambio"),
    ], [
        G("part", "mit zunehmender Anzahl verwendeter Prozessoren",
          "**Participio I como adjetivo** (*zunehmend*) + **genitivo sin artículo** (*verwendeter "
          "Prozessoren*): «con un número creciente de procesadores usados»."),
        G("fvg", "bringt … eine grundlegende Skepsis … zum Ausdruck",
          "**Verbo funcional**: *zum Ausdruck bringen* = «expresar»."),
        G("part", "mit wachsender zur Verfügung stehender Rechenleistung",
          "**Dos participios I seguidos**: «con una potencia de cálculo disponible cada vez "
          "mayor»."),
        G("gerund", "die zu lösenden Aufgaben",
          "**Gerundivo** (ver p. 3): «las tareas que hay que resolver»."),
        G("otros", "lässt man ein Problem … lösen",
          "**lassen + infinitivo** (¡sin *sich*!) = hacer que algo se haga: «se hace resolver un "
          "problema…»."),
        G("konj2", "würde man stattdessen … versuchen, … zu lösen",
          "**Subjuntivo II con würde**: «en su lugar, se intentaría resolver…»."),
    ]),
    (17, "1.2.5 Das Gustafson’sche Gesetz", [
        X("genauer bestimmen", "Ausdruck", "determinar con más precisión"),
        X("gemessen", "Adj.", "medido (de messen)"),
        X("im Widerspruch stehen zu + D", "Ausdruck",
          "estar en contradicción con (stand, hat gestanden)"),
        N("die", "Vorhersage", "Vorhersagen", "predicción"),
        X("laut + D / G", "Präp.", "según"),
        V("abfallen", "fällt ab", "fiel ab", "ist abgefallen", None, "descender, caer (una curva)"),
        X("steil", "Adj.", "empinado, pronunciado"),
        X("überhaupt", "Adv.", "siquiera; en absoluto"),
        X("in der Lage sein", "Ausdruck", "ser capaz (zu + Inf.: de)"),
        N("das", "Messergebnis", "Messergebnisse", "resultado de medición"),
    ], [
        G("trenn", "stellten … fest, dass …",
          "**feststellen**: el prefijo *fest* llega tras un complemento largo: «constataron que…»."),
        G("fvg", "im Widerspruch zu den Vorhersagen … standen",
          "**Verbo funcional**: «estaban en contradicción con las predicciones»."),
        G("trenn", "Wie man sieht, fällt die Kurve sehr steil ab",
          "**abfallen**: prefijo al final: «como se ve, la curva cae muy bruscamente»."),
        G("konj2", "wären überhaupt in der Lage … · betrüge … nur 24",
          "**Subjuntivo II** (hipótesis según Amdahl): «solo serían capaces… · sería solo 24»."),
    ]),
    (18, "1.2.5 Das Gustafson’sche Gesetz", [
        X("um (+ número)", "Präp.", "alrededor de (eine Beschleunigung um 1020)"),
        N("die", "Größenordnung", "Größenordnungen", "orden de magnitud"),
        N("die", "Annahme", "Annahmen", "suposición, hipótesis"),
        V("zurückweisen", "weist zurück", "wies zurück", "hat zurückgewiesen", None, "rechazar"),
        X("vorgegeben", "Adj.", "prefijado, dado"),
        N("das", "Zeitfenster", "Zeitfenster", "ventana de tiempo, plazo"),
        V("abschließen", "schließt ab", "schloss ab", "hat abgeschlossen", None,
          "terminar, completar (abgeschlossen sein = estar terminado)"),
        X("vielmehr", "Adv.", "más bien, por el contrario"),
        N("die", "Problemgröße", "Problemgrößen", "tamaño del problema"),
        V("annehmen", "nimmt an", "nahm an", "hat angenommen", None,
          "suponer, asumir (als konstant annehmen)"),
        N("der", "Freiheitsgrad", "Freiheitsgrade", "grado de libertad"),
        X("Ein- und Ausgabe", "Ausdruck", "entrada y salida (E/S)"),
        X("durchlaufbar", "Adj.", "que se puede recorrer (nur seriell durchlaufbar = solo en serie)"),
        N("der", "Engpass", "Engpässe", "cuello de botella"),
        X("dagegen", "Adv.", "en cambio, por el contrario"),
        V("umdrehen", "dreht um", "drehte um", "hat umgedreht", None,
          "dar la vuelta (die Fragestellung umdrehen = plantear la pregunta al revés)"),
        N("die", "Fragestellung", "Fragestellungen", "planteamiento (de la pregunta)"),
        X("verbracht", "Adj.", "empleado, pasado (tiempo) (de verbringen)"),
        X("streng monoton", "Adj.", "estrictamente monótono"),
        V("sich annähern", "nähert sich an", "näherte sich an", "hat sich angenähert", "+ D",
          "aproximarse a", "nähert sich … an (el «an» está en la p. 19)"),
    ], [
        G("konj1", "…, 1 − σ sei konstant …, zurückzuweisen sei",
          "**Estilo indirecto (subjuntivo I)**: todo el párrafo cuenta lo que dijo Gustafson: "
          "«que la suposición de que 1 − σ es constante debía rechazarse»."),
        G("seinzu", "zurückzuweisen sei · als konstant anzunehmen",
          "**sein + zu + infinitivo** (= hay que) en subjuntivo I: «había que rechazar · había "
          "que suponer constante»."),
        G("konj2", "hätten … könnten … wären … bliebe",
          "**Subjuntivo II como sustituto** del I cuando este coincide con el indicativo (*sie "
          "haben* → *sie hätten*); sigue siendo estilo indirecto."),
        G("v1", "Verdoppele man …, verdoppele man auch …",
          "**Condicional sin «wenn»** en subjuntivo I con *man*: «si se duplica…, se duplica "
          "también…»."),
        G("konj1", "Sei mit t_{p} und t_{s} die … verbrachte Laufzeit bezeichnet",
          "**Definición** con subjuntivo I + pasiva: «designemos con t_{p} y t_{s} el tiempo "
          "empleado en…»."),
        G("trenn", "nähert sich die Beschleunigung … an",
          "**sich annähern + D**: ¡el prefijo *an* aparece en la página siguiente!: «la "
          "aceleración se aproxima al número de procesadores»."),
    ]),
    (19, "1.2.5 Das Gustafson’sche Gesetz", [
        N("die", "Skalierbarkeit", None, "escalabilidad"),
        V("ausfallen", "fällt aus", "fiel aus", "ist ausgefallen", None,
          "téc. resultar (positiver ausfallen) (normalmente: suspenderse, fallar)"),
        X("bedeutend", "Adv.", "considerablemente"),
        N("der", "Graph", "Graphen", "gráfica (n-Deklination: des Graphen)"),
        X("im Falle + G", "Ausdruck", "en el caso de"),
        X("steigend", "Adj.", "creciente"),
        V("konvergieren", "konvergiert", "konvergierte", "hat konvergiert", "gegen + A",
          "converger a"),
    ], [
        G("otros", "fallen bedeutend positiver aus",
          "**ausfallen + comparativo** = «resultar»: «resultan considerablemente más positivas»."),
        G("infzu", "Statt wie im Falle des … Gesetzes … zu konvergieren, …",
          "**statt … zu + infinitivo** = «en lugar de converger (como en el caso de la ley de "
          "Amdahl)…»."),
        G("otros", "Für ein 1024-Prozessor-System und einem seriellen Anteil",
          "**¡Errata del libro!** Tras *für* va acusativo: debería ser *einen seriellen Anteil* "
          "(o *bei einem …*)."),
    ]),
    (20, "1.2.5 → «Und wer hat nun Recht?»", [
        X("Recht haben", "Ausdruck", "tener razón"),
        X("letztlich", "Adv.", "en última instancia, al final"),
        N("das", "Missverständnis", "Missverständnisse", "malentendido"),
        X("was … angeht", "Ausdruck", "en lo que respecta a"),
        N("die", "Vorbedingung", "Vorbedingungen", "condición previa"),
        N("die", "Anwendbarkeit", None, "aplicabilidad"),
        V("herrühren", "rührt her", "rührte her", "hat hergerührt", "von + D",
          "provenir de, deberse a"),
        X("irgendwo dazwischen", "Ausdruck", "en algún punto intermedio"),
        X("skalierbar", "Adj.", "escalable"),
        X("umgekehrt", "Adv.", "a la inversa"),
        X("anscheinend", "Adv.", "aparentemente"),
        X("einerseits … andererseits", "Konj.", "por un lado … por otro"),
    ], [
        G("konj1", "dass beide Gesetze … äquivalent seien",
          "**Subjuntivo I** (estilo indirecto: opinión de Yuan Shi): «que ambas leyes serían "
          "equivalentes»."),
        G("otros", "was die Definition … angeht",
          "**Fórmula**: *was X angeht* = «en lo que respecta a X»."),
        G("lassen", "Es lassen sich Anwendungen finden, für die …",
          "**sich lassen** con *es* de relleno y sujeto plural: «se pueden encontrar aplicaciones "
          "para las que…»."),
    ]),
    (21, "1.2.5 · final del capítulo", [
        X("unerlässlich", "Adj.", "imprescindible"),
        N("die", "Einschränkung", "Einschränkungen", "restricción, limitación"),
        N("der", "Codebestandteil", "Codebestandteile", "parte del código"),
        V("skalieren", "skaliert", "skalierte", "hat skaliert", None, "escalar"),
        X("erst", "Adv.", "no antes de, solo (erst im Betrieb = solo cuando ya funciona)"),
        N("der", "Betrieb", None, "téc. funcionamiento (im Betrieb) (normalmente: empresa)"),
        X("entscheidend", "Adj./Adv.", "decisivo, de forma decisiva"),
    ], [
        G("korr", "sich … darüber Gedanken zu machen, ob denn …",
          "**Correlato** *darüber … ob* + partícula **denn** en la pregunta indirecta (matiz: "
          "«realmente»): «reflexionar sobre si realmente…»."),
        G("lassen", "lässt sich … oft erst im Betrieb feststellen",
          "**sich lassen + erst** (= no antes de): «a menudo solo se puede determinar en "
          "funcionamiento»."),
        G("otros", "die tatsächliche erreichte Leistung",
          "Seguramente quería decir *die tatsächlich erreichte Leistung* (adverbio sin "
          "terminación → modifica a *erreichte*): «el rendimiento realmente alcanzado»."),
    ]),
]

# Internacionalismos: se entienden solos; aquí solo género y plural.
INTERNACIONALISMOS = [
    ("der", "Algorithmus", "Algorithmen"), ("die", "Architektur", "Architekturen"),
    ("der", "Chip", "Chips"), ("der", "Cluster", "Cluster"), ("der", "Code", "Codes"),
    ("der", "Compiler", "Compiler"), ("das", "Detail", "Details"), ("die", "Diagonale", "Diagonalen"),
    ("die", "Direktive", "Direktiven"), ("das", "Dokument", "Dokumente"), ("die", "Domäne", "Domänen"),
    ("der", "Effekt", "Effekte"), ("das", "Element", "Elemente"), ("das", "Experiment", "Experimente"),
    ("der", "Faktor", "Faktoren"), ("die", "Funktion", "Funktionen"),
    ("die", "Funktionalität", "Funktionalitäten"), ("der", "Index", "Indizes"),
    ("die", "Instanz", "Instanzen"), ("die", "Interpretation", "Interpretationen"),
    ("die", "Kategorie", "Kategorien"), ("das", "Konzept", "Konzepte"), ("die", "Kurve", "Kurven"),
    ("die", "Modifikation", "Modifikationen"), ("die", "Option", "Optionen"),
    ("der", "Parameter", "Parameter"), ("das", "Pragma", "Pragmas"), ("der", "Prozess", "Prozesse"),
    ("der", "Prozessor", "Prozessoren"), ("das", "Register", "Register"),
    ("die", "Ressource", "Ressourcen"), ("der", "Scheduler", "Scheduler"),
    ("die", "Simulation", "Simulationen"), ("die", "Skepsis", None),
    ("die", "Spezifikation", "Spezifikationen"), ("der", "Standard", "Standards"),
    ("das", "System", "Systeme"), ("die", "Technologie", "Technologien"),
    ("der", "Thread", "Threads"), ("die", "Topologie", "Topologien"),
    ("der", "Transistor", "Transistoren"), ("die", "Variable", "Variablen"),
    ("der", "Vektor", "Vektoren"), ("die", "Version", "Versionen"),
]


# ================================================================ renderizado
def articulo(art):
    return f'<font color="#{COLOR_ARTICULO[art].hexval()[2:]}"><b>{art}</b></font>'


def celda_de(e):
    txt = None
    if e[0] == "n":
        _, art, sg, pl, _, txt = e
        TEXTOS.extend([sg, pl or ""])
        plural = f"Pl. die {pl}" if pl else "solo sing."
        html = f'{articulo(art)} <b>{md(sg)}</b> <font size="7.8" color="#555555">· {md(plural)}</font>'
    elif e[0] == "v":
        _, inf, pres, prat, perf, reg, _, txt = e
        TEXTOS.extend([inf, pres, prat, perf, reg or ""])
        regimen = f" <b>{md(reg)}</b>" if reg else ""
        html = (f'<b>{md(inf)}</b>{regimen}<br/><font size="7.8" color="#555555">'
                f'{md(pres)} · {md(prat)} · {md(perf)}</font>')
    else:
        _, palabra, clase, _, txt = e
        TEXTOS.extend([palabra, clase])
        html = f'<b>{md(palabra)}</b> <font size="7.8" color="#555555">({md(clase)})</font>'
    if txt:
        TEXTOS.append(txt)
        html += f'<br/><font size="7.8" color="#555555"><i>en el texto: {md(txt)}</i></font>'
    return Paragraph(html, SV)


def espanol(e):
    return e[4] if e[0] == "n" else e[6] if e[0] == "v" else e[3]


def celda_es(e):
    es = espanol(e)
    TEXTOS.append(es)
    if es.startswith("téc. "):
        return Paragraph(f'<font size="6.8" color="#{TEC.hexval()[2:]}"><b>TÉC.</b></font> '
                         f'{md(es[5:])}', SV)
    return Paragraph(md(es), SV)


def estilo_tabla(extra=()):
    return TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                       ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_DE]),
                       ("LINEBELOW", (0, 1), (-1, -1), 0.25, LINEA),
                       ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5), *extra])


def tabla_vocabulario(entradas, pag):
    datos = [[Paragraph(f"VOKABELN · S. {pag}", SCAB), Paragraph("ESPAÑOL", SCAB)]]
    datos += [[celda_de(e), celda_es(e)] for e in entradas]
    t = Table(datos, colWidths=[8.6 * cm, ANCHO - 8.6 * cm], repeatRows=1)
    t.setStyle(estilo_tabla())
    return t


def tabla_gramatica(notas, pag):
    datos = [[Paragraph(f"GRAMMATIK · S. {pag} · EN EL TEXTO", SCAB),
              Paragraph("QUÉ ES · CÓMO LEERLO", SCAB)]]
    for tipo, frag, exp in notas:
        TEXTOS.extend([frag, exp])
        nombre = TIPOS[tipo][0]
        datos.append([Paragraph(f"<i>{md(frag)}</i>", SFRAG),
                      Paragraph(f'<font size="7.2" color="#2e5e8c"><b>{md(nombre).upper()}</b>'
                                f'</font><br/>{md(exp)}', SEXP)])
    t = Table(datos, colWidths=[6.4 * cm, ANCHO - 6.4 * cm], repeatRows=1)
    t.setStyle(estilo_tabla([("BACKGROUND", (0, 0), (-1, 0), AZUL2)]))
    return t


def mapa_gramatica():
    paginas = {}
    for pag, _t, _v, notas in PAGINAS:
        for tipo, *_r in notas:
            paginas.setdefault(tipo, [])
            if pag not in paginas[tipo]:
                paginas[tipo].append(pag)
    datos = [[Paragraph(c, SCAB) for c in ("ESTRUCTURA", "QUÉ SIGNIFICA", "PÁGINAS")]]
    for tipo, (nombre, resumen) in TIPOS.items():
        if tipo in paginas:
            datos.append([P("**" + nombre + "**", SV), P(resumen, SV),
                          P(", ".join(map(str, paginas[tipo])), SV)])
    t = Table(datos, colWidths=[5.0 * cm, ANCHO - 9.2 * cm, 4.2 * cm], repeatRows=1)
    t.setStyle(estilo_tabla())
    return t


def palabras_pequenas():
    clases = ("Adv.", "Konj.", "Präp.", "Präp./Konj.", "Abk.", "Relativadverb")
    filas = [(e[1], e[3], pag) for pag, _t, voc, _g in PAGINAS for e in voc
             if e[0] == "x" and e[2] in clases]
    datos = [[Paragraph(c, SCAB) for c in ("WORT", "ESPAÑOL", "S.")]]
    datos += [[P("**" + w + "**", SV), P(es, SV), P(str(pag), SNUM)] for w, es, pag in filas]
    t = Table(datos, colWidths=[5.0 * cm, ANCHO - 6.3 * cm, 1.3 * cm], repeatRows=1)
    t.setStyle(estilo_tabla())
    return t, len(filas)


def tabla_internacionalismos():
    celdas = []
    for art, sg, pl in sorted(INTERNACIONALISMOS, key=lambda x: clave_orden(x[1])):
        TEXTOS.extend([sg, pl or ""])
        plural = f"Pl. die {pl}" if pl else "solo sing."
        celdas.append(f'{articulo(art)} <b>{sg}</b> <font size="7.4" color="#555555">'
                      f'· {plural}</font>')
    return rejilla(celdas, 3)


def clave_orden(s):
    s = re.sub(r"^(sich( \(D\))? |etw\. )", "", s.strip("-… "))
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def indice_alfabetico():
    items = []
    for pag, _t, voc, _g in PAGINAS:
        for e in voc:
            palabra = e[2] if e[0] == "n" else e[1]
            etiqueta = f"{e[1]} {palabra}" if e[0] == "n" else palabra
            items.append((clave_orden(palabra), etiqueta, pag))
    items.sort()
    celdas = [f'{md(et)} <font color="#555555">· {pag}</font>' for _k, et, pag in items]
    return bloques_por_pagina(celdas, 3), len(items)


ALTO_UTIL = A4[1] - 1.6 * cm - 1.9 * cm - 12   # alto del marco (márgenes y relleno del frame)


def bloques_por_pagina(celdas, ncol):
    """Parte el índice en bloques que caben en una página: así cada página se lee columna a
    columna y la siguiente continúa donde acaba la anterior (una tabla partida no lo haría)."""
    bloques, i, alto = [], 0, ALTO_UTIL - 52          # la primera página lleva el título
    while i < len(celdas):
        lo, hi, mejor = 1, -(-(len(celdas) - i) // ncol), 1
        while lo <= hi:
            medio = (lo + hi) // 2
            _, h = rejilla(celdas[i:i + medio * ncol], ncol, medio).wrap(ANCHO, alto)
            if h <= alto:
                mejor, lo = medio, medio + 1
            else:
                hi = medio - 1
        bloques.append(rejilla(celdas[i:i + mejor * ncol], ncol, mejor))
        i += mejor * ncol
        alto = ALTO_UTIL - 4
    return bloques


def rejilla(celdas, ncol, filas=None):
    """Reparte celdas HTML en columnas (orden de lectura: columna a columna)."""
    filas = filas or -(-len(celdas) // ncol)
    celdas = [Paragraph(c, SIDX) for c in celdas]
    datos = [[celdas[c * filas + f] if c * filas + f < len(celdas) else ""
              for c in range(ncol)] for f in range(filas)]
    t = Table(datos, colWidths=[ANCHO / ncol] * ncol)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 0.8),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 0.8)]))
    return t


# ================================================================ montaje
def portada(story, n_voc, n_gram):
    story.append(Spacer(1, 2.4 * cm))
    story.append(P("Lista de lectura", STIT))
    story.append(Spacer(1, 0.25 * cm))
    story.append(P("OpenMP · Kapitel 1 «Einführung»", St(
        "t2", parent=STIT, fontSize=17, leading=22, textColor=AZUL2)))
    story.append(Spacer(1, 0.45 * cm))
    story.append(P(f"Página a página (pp. 1–21) · {n_voc} palabras y expresiones · "
                   f"{n_gram} notas de gramática · nivel B1−", SSUB))
    story.append(Spacer(1, 1.0 * cm))
    caja = [
        P("**Cómo usarla.** Ten la lista al lado del libro de S. Hoffmann y R. Lienhart, *OpenMP* "
          "(Springer, 2008). Cada página del libro tiene su bloque: primero el **vocabulario**, en "
          "el orden en que aparece, y después la **gramática** que va más allá de B1.", SCAJA),
        P("• Cada palabra se explica **solo la primera vez**. Si más adelante no la recuerdas, "
          "búscala en el **índice alfabético** del final (con la página).", SCAJA),
        P("• Se ha dejado fuera lo que un nivel B1− ya conoce y los **internacionalismos** "
          "transparentes (Prozessor, Simulation…), que van al final solo con su género y plural. "
          "Sí están las palabras de B1 que aquí tienen un **sentido técnico** distinto (marca "
          "**TÉC.**).", SCAJA),
        P("• Sustantivos con artículo en color (der · die · das) y plural; verbos con presente, "
          "Präteritum y Partizip II, y la preposición con su caso (+ A = acusativo, + D = dativo, "
          "+ G = genitivo).", SCAJA),
        P("• En la gramática, el fragmento es una cita breve del libro, recortada con «…», para "
          "que encuentres la estructura en la página. La tabla siguiente reúne toda la gramática "
          "del capítulo.", SCAJA),
    ]
    t = Table([[caja]], colWidths=[ANCHO - 2 * cm])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, AZUL2),
                           ("BACKGROUND", (0, 0), (-1, -1), FONDO_DE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                           ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    story.append(t)


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont(SANS, 7.8)
    canvas.setFillColor(GRIS)
    canvas.drawString(MARGEN, 1.05 * cm, "Lista de lectura · OpenMP, cap. 1 · nivel B1−")
    canvas.drawRightString(A4[0] - MARGEN, 1.05 * cm, f"{doc.page}")
    canvas.setStrokeColor(LINEA)
    canvas.setLineWidth(0.5)
    canvas.line(MARGEN, 1.4 * cm, A4[0] - MARGEN, 1.4 * cm)
    canvas.restoreState()


def construir():
    n_voc = sum(len(v) for _p, _t, v, _g in PAGINAS)
    n_gram = sum(len(g) for _p, _t, _v, g in PAGINAS)
    story = []
    portada(story, n_voc, n_gram)
    story.append(PageBreak())

    story.append(P("La gramática del capítulo de un vistazo", SH1))
    story.append(P("Cada estructura se explica en la página donde aparece; aquí tienes dónde "
                   "encontrarla.", SREF))
    story.append(mapa_gramatica())

    story.append(PageBreak())
    story.append(P("Página a página", SH1))
    for pag, tema, voc, gram in PAGINAS:
        story.append(CondPageBreak(5 * cm))
        story.append(Paragraph(f"Seite {pag} · página {pag}", SH2))
        story.append(P(tema, STEMA))
        story.append(tabla_vocabulario(voc, pag))
        if gram:
            story.append(Spacer(1, 0.18 * cm))
            story.append(tabla_gramatica(gram, pag))

    story.append(PageBreak())
    tabla, n = palabras_pequenas()
    story.append(P("Palabras pequeñas que estructuran el texto", SH1))
    story.append(P(f"Los {n} conectores, adverbios y preposiciones de la lista, en orden de "
                   "aparición: son lo que más ayuda a leer con fluidez.", SREF))
    story.append(tabla)

    story.append(CondPageBreak(7 * cm))
    story.append(P("Internacionalismos", SH1))
    story.append(P("Se entienden sin traducción; aquí solo el género y el plural (¡ojo: "
                   "Algorithmen, Indizes, Pragmas!).", SREF))
    story.append(tabla_internacionalismos())

    story.append(PageBreak())
    bloques, n = indice_alfabetico()
    story.append(P("Índice alfabético", SH1))
    story.append(P(f"Las {n} entradas de la lista con la página del libro donde se explican.",
                   SREF))
    for k, bloque in enumerate(bloques):
        if k:
            story.append(PageBreak())
        story.append(bloque)

    doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=MARGEN, rightMargin=MARGEN,
                            topMargin=1.6 * cm, bottomMargin=1.9 * cm,
                            title="Lista de lectura: OpenMP, capítulo 1 (nivel B1−)",
                            author="indescifrable · material de estudio",
                            subject="Vocabulario y gramática página a página para leer el "
                                    "capítulo 1 de OpenMP (Hoffmann/Lienhart) en alemán")
    doc.build(story, onLaterPages=pie)


def verificar():
    tipos = {t for _p, _t, _v, g in PAGINAS for t, *_r in g}
    assert tipos <= set(TIPOS), tipos - set(TIPOS)
    assert [p for p, *_r in PAGINAS] == list(range(1, 22)), "faltan páginas"
    # sin palabras repetidas: cada entrada se explica una sola vez
    vistas = {}
    for pag, _t, voc, _g in PAGINAS:
        for e in voc:
            clave = (e[2] if e[0] == "n" else e[1]).lower()
            assert clave not in vistas, f"'{clave}' repetida en p. {vistas[clave]} y p. {pag}"
            vistas[clave] = pag
    if CMAP is not None:
        faltan = sorted({c for t in TEXTOS for c in t if c.strip() and ord(c) not in CMAP})
        if faltan:
            raise SystemExit(f"Glifos sin fuente: {' '.join(faltan)}")


if __name__ == "__main__":
    construir()
    verificar()
    print(f"PDF escrito: {SALIDA}")
