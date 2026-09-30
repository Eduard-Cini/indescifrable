# -*- coding: utf-8 -*-
"""Genera material/lista-lectura-openmp-cap1.pdf: lista de lectura para leer el prólogo
(«Vorwort», pp. V-VI) y el capítulo 1 («Einführung», pp. 1-21) de S. Hoffmann y R. Lienhart,
«OpenMP. Eine Einführung in die parallele Programmierung mit C/C++» (Springer 2008) con B1−.

Tres partes: (1) GRAMÁTICA EXPLICADA: las estructuras del texto desde cero (qué es, cómo se
forma, cómo reconocerla, cómo traducirla) con ejemplos propios; (2) PÁGINA A PÁGINA, en orden de
lectura: de qué habla cada párrafo (resumen propio), el vocabulario por encima de B1− (solo la
primera vez; sustantivos con género y plural, verbos con presente, Präteritum, Partizip II y
régimen) y la gramática en el texto, localizada con un fragmento BREVE del libro («…» recorta),
analizada pieza a pieza y con remisión a su §; (3) conectores, internacionalismos e índice.
No reproduce el libro: solo palabras sueltas, citas cortas y resúmenes propios.

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
    """Nota de gramática: tipo (clave de GRAMATICA), fragmento BREVE del libro, análisis."""
    return (tipo, fragmento, explicacion)


# Las estructuras explicadas desde cero (parte «Gramática explicada»). El orden fija el número
# de § con el que remiten las notas de cada página. Ejemplos PROPIOS (no salen del libro).
GRAMATICA = [
    dict(clave="part", titulo="Atributo participial extendido",
         aleman="erweitertes Partizipialattribut",
         resumen="artículo + complementos + participio + sustantivo = «el X que…»",
         que="Lo que en español sería una oración de relativo («el bucle *que sigue en la línea 4*») "
             "el alemán lo coloca delante del sustantivo, entre el artículo y el sustantivo, usando un "
             "participio como si fuera un adjetivo. Es el rasgo más típico del alemán técnico y "
             "científico, y el que más cuesta al principio.",
         forma="artículo + [complementos: adverbios, grupos con preposición, objetos] + participio con "
               "terminación de adjetivo + sustantivo\n"
               "• participio I (infinitivo + *d*: *folgend, laufend, arbeitend*) = acción activa y "
               "simultánea: «que sigue, que corre, que trabaja»\n"
               "• participio II (*beschrieben, ausgeführt, benötigt*) = sentido pasivo o acabado: "
               "«descrito, ejecutado, necesitado»",
         reconocer="Un artículo (*der, die, das, ein…*) que NO va seguido de su sustantivo ni de un "
                   "adjetivo normal, sino de una preposición, un adverbio o un número: *die in …*, "
                   "*der von …*, *des derzeit …*, *die mit …*. El artículo «se queda esperando» a su "
                   "sustantivo, que llega varias palabras después, justo detrás de una palabra acabada "
                   "en *-end-e / -end-en* o de un participio II con terminación (*-te, -ten*).",
         traducir="1) Localiza el artículo y busca su sustantivo (mismo género, número y caso). "
                  "2) Traduce «artículo + sustantivo». 3) Añade «que» y traduce el resto como una "
                  "oración, leyendo hacia atrás desde el participio: participio I → verbo en activa "
                  "(«que sigue»); participio II → pasiva o participio español («que se describe», "
                  "«descrito»).",
         ejemplos=[("die von allen Threads gemeinsam genutzten Daten",
                    "los datos que usan en común todos los hilos"),
                   ("ein in C geschriebenes Programm", "un programa escrito en C"),
                   ("der mit jeder Version wachsende Standard",
                    "el estándar, que crece con cada versión")]),
    dict(clave="gerund", titulo="Gerundivo: zu + participio I", aleman="Gerundivum",
         resumen="«die zu lösenden Aufgaben» = las tareas que hay que resolver",
         que="Es un participio I con *zu* delante que funciona como adjetivo. Expresa que con el "
             "sustantivo hay que hacer algo o se puede hacer algo (sentido pasivo): *die zu lösende "
             "Aufgabe* es «la tarea que hay que resolver».",
         forma="artículo + *zu* + participio I (infinitivo + *d*) + terminación de adjetivo + "
               "sustantivo: *die zu lösende Aufgabe*, *den zu testenden Code*.\n"
               "En los verbos separables, el *zu* va entre el prefijo y el verbo: *aus·zu·führend* → "
               "*die auszuführenden Anweisungen*.",
         reconocer="*zu* justo delante de una palabra acabada en *-ende, -enden, -ender, -endes*, "
                   "dentro de un grupo con artículo; o una palabra con *-zu-* en medio que acaba en "
                   "*-end-* (*auszuführenden*).",
         traducir="«el/la … que hay que + infinitivo», «que se debe / se va a + infinitivo», o "
                  "simplemente «a + infinitivo» («las tareas a resolver»).",
         ejemplos=[("die zu testende Funktion", "la función que hay que probar"),
                   ("ein nicht zu unterschätzender Aufwand", "un esfuerzo que no hay que subestimar"),
                   ("die noch zu parallelisierenden Schleifen",
                    "los bucles que aún hay que paralelizar")]),
    dict(clave="pasmod", titulo="La pasiva: con verbo modal y en tiempos compuestos",
         aleman="Passiv mit Modalverb, Perfekt und Plusquamperfekt Passiv",
         resumen="«… eingefügt werden müssen» = hay que insertar; «… gemacht worden» = se había hecho",
         que="La pasiva alemana se forma con *werden* + participio II. En español la traducimos casi "
             "siempre con «se» (*wird übersetzt* = «se compila») o con «ser + participio». Se "
             "complica cuando hay un verbo modal o un tiempo compuesto, porque entonces se acumulan "
             "varios verbos al final de la oración.",
         forma="• presente: *Das Programm wird übersetzt.* = El programa se compila.\n"
               "• con modal: *Das Programm muss übersetzt werden.* = Hay que compilar el programa "
               "(el modal se conjuga; *werden* va en infinitivo al final).\n"
               "• perfecto: *Das Programm ist übersetzt worden.* = El programa se ha compilado "
               "(¡*worden*, no *geworden*!).\n"
               "• pluscuamperfecto: *Das Programm war übersetzt worden.* = Se había compilado.\n"
               "• en oración subordinada todo va al final: *…, dass das Programm übersetzt werden "
               "muss.*",
         reconocer="Al final de la oración aparece un participio II seguido de *werden* o *worden* "
                   "(y a veces de un modal o de *ist/war*: *werden kann, werden muss, worden ist*).",
         traducir="Empieza por el final: participio + *werden* = pasiva; el modal añade «se puede / "
                  "hay que / debe». Tradúcelo con «se» o con «hay que»: *kann spezifiziert werden* → "
                  "«se puede especificar»; *muss eingebunden werden* → «hay que incluir».",
         ejemplos=[("Die Datei muss eingebunden werden.", "Hay que incluir el archivo."),
                   ("Die Option kann abgeschaltet werden.", "La opción se puede desactivar."),
                   ("Der Entwurf war gerade veröffentlicht worden.",
                    "El borrador acababa de publicarse.")]),
    dict(clave="pasimp", titulo="Pasiva impersonal (sin sujeto)", aleman="unpersönliches Passiv",
         resumen="«auf … wird zugegriffen» = se accede a",
         que="En alemán también se ponen en pasiva verbos que no tienen complemento directo, por "
             "ejemplo los verbos con preposición fija (*zugreifen auf*, *verzichten auf*). Como no hay "
             "nada que pueda ser sujeto, la oración pasiva se queda sin sujeto: el verbo va en 3.ª "
             "persona del singular y el complemento conserva su preposición.",
         forma="[complemento con preposición] + *wird / kann …* + participio II (+ *werden*).\n"
               "Si no hay nada delante del verbo, se pone *es*: *Es wird auf den Speicher "
               "zugegriffen.*",
         reconocer="*wird* (o un modal) + participio, pero no encuentras ningún sujeto en "
                   "nominativo; en su lugar hay un grupo con preposición (*auf die Daten*, *auf das "
                   "Einbinden*).",
         traducir="Con «se» impersonal: *Auf die Daten wird zugegriffen* → «se accede a los datos»; "
                  "*Darauf kann verzichtet werden* → «se puede prescindir de ello».",
         ejemplos=[("Auf die Variable wird gleichzeitig zugegriffen.",
                    "Se accede a la variable al mismo tiempo."),
                   ("Auf diese Option kann verzichtet werden.", "Se puede prescindir de esta opción."),
                   ("Hier wird parallel gerechnet.", "Aquí se calcula en paralelo.")]),
    dict(clave="zustand", titulo="Pasiva de estado", aleman="Zustandspassiv",
         resumen="sein + participio II = está(n) + participio",
         que="*sein* + participio II describe un estado: el resultado de una acción ya terminada. La "
             "pasiva normal (*werden* + participio) describe la acción. En español es la diferencia "
             "entre «está definida» y «se define».",
         forma="*ist / sind / war / waren* + participio II: *Die Variable ist definiert.*\n"
               "Con modal: *… kann kombiniert sein.*",
         reconocer="*sein* conjugado + un participio II que se puede entender como adjetivo "
                   "(*definiert, integriert, abgelegt, implementiert*), sin *werden*.",
         traducir="«estar + participio»: *sind abgelegt* → «están almacenadas»; *waren "
                  "implementiert* → «estaban implementadas».",
         ejemplos=[("Die Datei ist eingebunden.",
                    "El archivo está incluido (≠ Die Datei wird eingebunden = se incluye)."),
                   ("Die Kerne sind auf einem Chip integriert.",
                    "Los núcleos están integrados en un chip."),
                   ("Das Programm war schon übersetzt.", "El programa ya estaba compilado.")]),
    dict(clave="lassen", titulo="Los usos de «lassen»", aleman="sich lassen, lassen + Infinitiv",
         resumen="sich lassen + inf. = se puede; lassen + inf. = hacer que",
         que="*lassen* significa básicamente «dejar», pero en el texto aparece sobre todo en tres "
             "construcciones que hay que distinguir:\n"
             "1) *sich lassen* + infinitivo = «se puede + infinitivo» (posibilidad): *Der Code lässt "
             "sich parallelisieren* = el código se puede paralelizar.\n"
             "2) *lassen* + infinitivo, sin *sich* = «hacer que algo se haga» o «dejar que»: *Man "
             "lässt ein Problem lösen* = se hace resolver un problema.\n"
             "3) *etwas vermuten lassen* = «dejar suponer, sugerir».",
         forma="Uso 1: sujeto (la cosa) + *lässt sich* + … + infinitivo al final: *Die Option lässt "
               "sich im Menü aktivieren.*\n"
               "Si el sujeto va detrás, puede aparecer *es* de relleno y el verbo concuerda con el "
               "sujeto real: *Es lassen sich Anwendungen finden* (plural por *Anwendungen*).",
         reconocer="*lässt sich / lassen sich* + un infinitivo al final de la oración = uso 1. "
                   "*lassen* + infinitivo sin *sich* = uso 2 o 3.",
         traducir="Uso 1: «se puede(n) + infinitivo», «es posible + infinitivo». Uso 2: «hacer + "
                  "infinitivo». Uso 3: «hacer pensar, dejar suponer».",
         ejemplos=[("Die Option lässt sich im Menü aktivieren.",
                    "La opción se puede activar en el menú."),
                   ("Das lässt sich leicht messen.", "Eso se puede medir fácilmente."),
                   ("Der Name lässt vermuten, dass …", "El nombre hace suponer que…")]),
    dict(clave="seinzu", titulo="sein + zu + infinitivo", aleman="sein + zu + Infinitiv",
         resumen="= se puede / hay que + infinitivo; ist einfach zu … = es fácil de…",
         que="Es otra manera de decir una pasiva con modal. Según el contexto significa «se puede» "
             "(= *können*) o «hay que» (= *müssen*). Con adjetivos como *einfach, leicht, schwer* "
             "significa «ser fácil / difícil de…».",
         forma="*ist / sind* + … + *zu* + infinitivo al final (no hay otro verbo): *Die Ergebnisse "
               "sind zu prüfen.*\n"
               "Con adjetivo: *OpenMP ist einfach zu verwenden.*\n"
               "En los separables, *zu* dentro: *zurück·zu·weisen*.",
         reconocer="*sein* conjugado y, al final, *zu* + infinitivo, sin ningún otro verbo.",
         traducir="«hay que + infinitivo» (obligación) o «se puede + infinitivo» (posibilidad); con "
                  "adjetivo, «es fácil / difícil de + infinitivo».",
         ejemplos=[("Die Datei ist vorher einzubinden.", "Hay que incluir antes el archivo."),
                   ("Das Problem ist leicht zu lösen.", "El problema es fácil de resolver."),
                   ("Die Annahme ist zurückzuweisen.", "Hay que rechazar la suposición.")]),
    dict(clave="v1", titulo="Condicional sin «wenn»", aleman="uneingeleiteter Konditionalsatz",
         resumen="verbo al principio de la oración = «si…»",
         que="Una condición («si…») puede expresarse sin *wenn*, poniendo el verbo conjugado al "
             "principio de la oración. Es muy frecuente en los textos técnicos y confunde porque "
             "parece una pregunta.",
         forma="[verbo conjugado] + sujeto + … , (*so / dann*) + [verbo] + resto.\n"
               "La oración principal empieza también por el verbo, o por *so / dann*.\n"
               "*Möchte man X, so muss …* = *Wenn man X möchte, muss …*",
         reconocer="Una oración que empieza por un verbo conjugado, no termina en «?» y va seguida "
                   "de una coma y de otra oración que también empieza por verbo o por *so / dann*.",
         traducir="Añade «si»: *Möchte man …, so muss …* → «si uno quiere…, tiene que…». *Sollte …* "
                  "al principio → «si por casualidad…, en caso de que…». *Werden … aktiviert* → «si "
                  "se activan…».",
         ejemplos=[("Fehlt die Option, läuft das Programm seriell.",
                    "Si falta la opción, el programa se ejecuta en serie."),
                   ("Sollte der Compiler OpenMP nicht kennen, ignoriert er die Pragmas.",
                    "Si el compilador no conoce OpenMP, ignora los pragmas."),
                   ("Wird die Variable geändert, muss man neu übersetzen.",
                    "Si se modifica la variable, hay que volver a compilar.")]),
    dict(clave="konj1", titulo="Subjuntivo I", aleman="Konjunktiv I",
         resumen="estilo indirecto («según él…») y definiciones («Sea σ…»)",
         que="Es un modo verbal que el alemán usa sobre todo para dos cosas: (1) el **estilo "
             "indirecto**: al contar lo que dijo otra persona, el autor marca con el subjuntivo I que "
             "no lo afirma él mismo; y (2) las **definiciones y suposiciones** en matemáticas («Sea "
             "σ…»).",
         forma="raíz del infinitivo + *-e*: *er sei* (sein), *er habe*, *er werde*, *er könne*, *er "
               "gelte*, *er verdoppele*. La 3.ª persona del singular es la más frecuente.\n"
               "Cuando la forma coincidiría con el indicativo (por ejemplo en plural: *sie haben*), "
               "se usa el subjuntivo II (*sie hätten*, ver §10).",
         reconocer="*sei, seien, habe, werde, könne, gelte…* y verbos en 3.ª persona del singular "
                   "acabados en *-e* (*verdoppele*), donde en indicativo habría *ist, hat, wird, "
                   "kann, gilt, verdoppelt*.",
         traducir="En estilo indirecto: «que» + imperfecto de subjuntivo o condicional («dijo que "
                  "*era* / que *sería*»); si ayuda, añade «según él». En definiciones: «Sea…», "
                  "«Supongamos que…». En fórmulas como *es sei angemerkt*: «cabe señalar».",
         ejemplos=[("Amdahl meinte, der Aufwand sei sequenziell.",
                    "Amdahl opinaba que el esfuerzo era secuencial."),
                   ("Sei n die Anzahl der Kerne.", "Sea n el número de núcleos."),
                   ("Es sei angemerkt, dass …", "Cabe señalar que…")]),
    dict(clave="konj2", titulo="Subjuntivo II", aleman="Konjunktiv II",
         resumen="hipótesis: wäre, hätte, käme, würde… = sería, tendría, llegaría…",
         que="Expresa lo hipotético o irreal («sería, tendría, podría») y la cortesía. En el estilo "
             "indirecto sustituye al subjuntivo I cuando este no se distingue del indicativo.",
         forma="• *wäre* (de *sein*), *hätte* (de *haben*), *würde* + infinitivo (la forma más usada "
               "con cualquier verbo), *könnte*, *müsste*.\n"
               "• Algunos verbos fuertes tienen forma propia: raíz del Präteritum + Umlaut + *-e*: "
               "*käme* (kommen), *betrüge* (betragen), *bliebe* (bleiben).\n"
               "• En los verbos débiles es igual que el Präteritum: *ausnutzte*.",
         reconocer="Vocal con Umlaut + *-e* en verbos fuertes (*käme, wäre, betrüge*); *würde* + "
                   "infinitivo al final; formas de pasado en un contexto hipotético («un algoritmo "
                   "ideal que aprovechara…»).",
         traducir="Condicional o imperfecto de subjuntivo: *wäre* → «sería / fuera», *hätte* → "
                  "«tendría», *käme auf* → «llegaría a», *würde … versuchen* → «intentaría».",
         ejemplos=[("Mit acht Kernen wäre das Programm schneller.",
                    "Con ocho núcleos el programa sería más rápido."),
                   ("Ein idealer Algorithmus hätte die Effizienz 1.",
                    "Un algoritmo ideal tendría eficiencia 1."),
                   ("Man würde ein größeres Problem lösen.", "Se resolvería un problema mayor.")]),
    dict(clave="fvg", titulo="Verbos funcionales", aleman="Funktionsverbgefüge",
         resumen="zum Ausdruck bringen = expresar; Verwendung finden = usarse…",
         que="Son combinaciones de un verbo casi vacío (*kommen, bringen, finden, stehen, stellen, "
             "sein*) con un sustantivo que aporta el significado. Son típicas del alemán formal y "
             "técnico y casi siempre equivalen a un verbo simple.",
         forma="verbo + (preposición +) sustantivo fijo:\n"
               "• *zum Einsatz kommen* = eingesetzt werden (emplearse)\n"
               "• *zum Ausdruck bringen* = ausdrücken (expresar)\n"
               "• *zur Verfügung stehen / stellen* = estar disponible / ofrecer\n"
               "• *Verwendung finden* = verwendet werden (usarse)\n"
               "• *Berücksichtigung finden* = berücksichtigt werden (tenerse en cuenta)\n"
               "• *im Widerspruch stehen zu* = widersprechen (contradecir)\n"
               "• *in der Lage sein* = können (ser capaz)",
         reconocer="Un sustantivo abstracto (a menudo en *-ung* o *-ation*) acompañado de un verbo "
                   "muy común que, tomado al pie de la letra, no tiene sentido («encuentran "
                   "consideración»).",
         traducir="Por el verbo simple equivalente: *finden … Berücksichtigung* → «se tienen en "
                  "cuenta»; *kommt zum Einsatz* → «se usa».",
         ejemplos=[("OpenMP kommt hier zum Einsatz.", "Aquí se usa OpenMP."),
                   ("Die Bibliothek stellt Funktionen zur Verfügung.", "La biblioteca ofrece funciones."),
                   ("Die Idee fand schnell Verwendung.", "La idea empezó a usarse rápidamente.")]),
    dict(clave="trenn", titulo="Verbos separables: el prefijo al final",
         aleman="trennbare Verben, Satzklammer",
         resumen="busca el prefijo al final de la oración",
         que="En la oración principal, el prefijo de un verbo separable (*an-, aus-, ab-, bei-, dar-, "
             "fest-, heran-, vor-…*) se separa del verbo y se va al final de la oración. Entre el "
             "verbo y su prefijo pueden caber muchas palabras (el «paréntesis verbal»). Y el prefijo "
             "cambia el significado: *stellen* («poner») no es *darstellen* («representar») ni "
             "*feststellen* («constatar»).",
         forma="verbo conjugado en 2.ª posición … prefijo al final: *Die Abbildung zeigt die Kurve … "
               "an.*\n"
               "En oraciones subordinadas y en infinitivo, el verbo va junto: *…, dass sie die Kurve "
               "anzeigt*; *anzuzeigen*.",
         reconocer="Si el verbo que lees no tiene sentido (*trägt* «lleva», *stellt* «pone»), mira al "
                   "final de la oración: si hay una partícula suelta (*an, aus, ab, bei, dar, fest, "
                   "vor, heran, zurück…*), pertenece al verbo.",
         traducir="Une mentalmente el prefijo al verbo (*trägt … bei* → *beitragen*) y busca ese "
                  "verbo compuesto en el diccionario.",
         ejemplos=[("Die Tabelle stellt die Ergebnisse übersichtlich dar.",
                    "La tabla presenta los resultados de forma clara."),
                   ("Er schaltet die Option vor dem Test ab.", "Desactiva la opción antes de la prueba."),
                   ("Wir stellen am Ende fest, dass …", "Al final constatamos que…")]),
    dict(clave="korr", titulo="Correlatos: darauf, davon, darüber… + dass / ob / wie",
         aleman="Korrelate, Pronominaladverbien",
         resumen="da(r) + preposición anuncia una oración: darauf vertrauen, dass…",
         que="Cuando un verbo lleva una preposición fija (*vertrauen auf*, *profitieren von*, "
             "*aussagen über*) y lo que viene detrás es una oración entera, la preposición se une a "
             "*da-* y forma una palabra (*darauf, davon, darüber, dadurch, dazu*) que «anuncia» la "
             "oración que viene después.",
         forma="*da* + preposición (con *-r-* si la preposición empieza por vocal: *dar-auf, "
               "dar-über*) … , *dass / ob / wie* + oración (o *zu* + infinitivo).\n"
               "*vertrauen auf* → *darauf vertrauen, dass …*; *profitieren von* → *davon profitieren, "
               "dass …*",
         reconocer="*darauf, davon, darüber, dadurch, daran, dazu* seguidos (a veces bastante "
                   "después) de una coma y *dass, ob, wie* o *zu*.",
         traducir="Casi siempre basta la preposición española + «que»: *darauf vertrauen, dass* → "
                  "«confiar en que»; *davon profitieren, dass* → «beneficiarse de que»; *dadurch, "
                  "dass* → «por el hecho de que»; *dazu … zu* → «para». El *da(r)-* normalmente no "
                  "se traduce.",
         ejemplos=[("Wir achten darauf, dass der Code lesbar bleibt.",
                    "Nos aseguramos de que el código siga siendo legible."),
                   ("Das hängt davon ab, wie groß σ ist.", "Eso depende de lo grande que sea σ."),
                   ("Die Funktion wird dazu verwendet, die Zeit zu messen.",
                    "La función se usa para medir el tiempo.")]),
    dict(clave="rel", titulo="Oraciones de relativo difíciles", aleman="Relativsätze",
         resumen="dessen, deren, derer, mit Hilfe dessen, wonach, was",
         que="Las oraciones de relativo alemanas empiezan (tras una coma) por un pronombre relativo "
             "que tiene caso, y llevan el verbo conjugado al final. Las difíciles son las que llevan "
             "preposición delante, las de genitivo (*dessen, deren* = «cuyo, cuya») y las que usan "
             "*wo(r)-* + preposición o *was*.",
         forma="• con preposición: *die Direktive, auf die sie sich beziehen* (la directiva a la que "
               "se refieren)\n"
               "• genitivo: *dessen* (masculino y neutro), *deren* / *derer* (femenino y plural) + "
               "sustantivo sin artículo: *ein Algorithmus, dessen Ausführung …* (un algoritmo cuya "
               "ejecución…)\n"
               "• *mit deren Hilfe* / *mit Hilfe derer* / *mit Hilfe dessen* = con ayuda del cual / "
               "de la cual\n"
               "• *wonach* (= nach dem / der) = según el/la cual\n"
               "• *was* = lo cual (se refiere a toda la oración anterior)",
         reconocer="Coma + (preposición +) *der / die / das / dessen / deren / wonach / was* … y el "
                   "verbo conjugado al final.",
         traducir="«que, el cual, la cual, lo cual»; con genitivo, «cuyo / cuya»: *dessen "
                  "Beschleunigung* → «cuya aceleración». Para saber a qué sustantivo se refiere, mira "
                  "el género y el número del relativo.",
         ejemplos=[("der Compiler, dessen Optionen ich kenne", "el compilador cuyas opciones conozco"),
                   ("die Funktion, mit deren Hilfe man die Zeit misst",
                    "la función con la que se mide el tiempo"),
                   ("Die Laufzeit sinkt, was die Effizienz erhöht.",
                    "El tiempo de ejecución baja, lo cual aumenta la eficiencia.")]),
    dict(clave="infzu", titulo="Construcciones de infinitivo con zu", aleman="Infinitivsätze mit zu",
         resumen="es ist …, … zu; um / ohne / statt … zu; die Fähigkeit, … zu",
         que="El infinitivo con *zu* va al final de su grupo, así que puede estar muy lejos de la "
             "palabra que lo introduce. Aparece:\n"
             "1) tras sustantivos y adjetivos: *die Fähigkeit, … zu …* (la capacidad de…), *es ist "
             "notwendig, … zu …* (es necesario…);\n"
             "2) tras verbos: *zwingen, anweisen, versuchen … zu …* (obligar a, ordenar, intentar…);\n"
             "3) con conjunciones: *um … zu* (para), *ohne … zu* (sin), *statt … zu* (en lugar de).",
         forma="… *zu* + infinitivo al final.\n"
               "• separables: *zu* dentro: *aus·zu·nutzen, an·zu·passen, vor·zu·stellen*\n"
               "• con modal: *ausnutzen zu können* (poder aprovechar)\n"
               "• en pasiva: *ausgeführt zu werden* (ser ejecutado)",
         reconocer="Coma + (*um / ohne / statt*) … + *zu* + infinitivo al final; o una palabra con "
                   "*-zu-* en medio (*anzupassen*).",
         traducir="«para / sin / en lugar de + infinitivo»; tras sustantivo o adjetivo, «de + "
                  "infinitivo» o directamente el infinitivo («es necesario paralelizar»).",
         ejemplos=[("Um Zeit zu sparen, parallelisiert man die Schleife.",
                    "Para ahorrar tiempo, se paraleliza el bucle."),
                   ("Er übersetzt das Programm, ohne die Option zu setzen.",
                    "Compila el programa sin poner la opción."),
                   ("Es ist sinnvoll, die Laufzeit vorher zu messen.",
                    "Conviene medir antes el tiempo de ejecución.")]),
    dict(clave="es", titulo="Los usos de «es»", aleman="es als Platzhalter und Korrelat",
         resumen="relleno (Es stehen … Compiler), anuncio (Es ist …, … zu), «es X el que…»",
         que="*es* no siempre significa «ello». En el texto cumple sobre todo tres papeles:\n"
             "1) **relleno**: ocupa la primera posición para que el sujeto real pueda ir detrás (el "
             "verbo concuerda con ese sujeto real);\n"
             "2) **anuncio**: anuncia una oración con *dass* o un infinitivo con *zu* que viene "
             "después (*Das Ziel ist es, … zu …*);\n"
             "3) **oración escindida**: destaca un elemento (*X ist es, die …* = «es X la que…»).",
         forma="1) *Es stehen … Compiler zur Verfügung.* (plural por *Compiler*)\n"
               "2) *Es empfiehlt sich, … zu …*; *Das Ziel ist es, … zu …*\n"
               "3) *Diese Anweisung ist es, die …*",
         reconocer="*es* al principio con un verbo en plural (uso 1); *es* seguido más adelante de "
                   "*dass* o de *zu* + infinitivo (uso 2); *ist es, die / der / das* (uso 3).",
         traducir="1) «hay…» o se omite; 2) se omite: el infinitivo o la oración hacen de sujeto («el "
                  "objetivo es presentar…»); 3) «es … el / la que…».",
         ejemplos=[("Es gibt viele Compiler.", "Hay muchos compiladores."),
                   ("Es ist wichtig, den Code zu testen.", "Es importante probar el código."),
                   ("Die Schleife ist es, die die meiste Zeit braucht.",
                    "Es el bucle el que más tiempo necesita.")]),
    dict(clave="orden", titulo="Orden de palabras: qué va delante del verbo",
         aleman="Wortstellung, Vorfeld",
         resumen="complemento delante y sujeto detrás del verbo",
         que="En la oración principal alemana el verbo conjugado ocupa siempre la segunda posición, "
             "pero delante puede ir casi cualquier elemento, no solo el sujeto: un complemento "
             "directo, un complemento con preposición, un participio… Entonces el sujeto va detrás "
             "del verbo. Lo que se pone delante suele ser lo ya conocido o lo que se quiere destacar.",
         forma="[cualquier elemento] + verbo conjugado + sujeto + resto (+ participio o infinitivo al "
               "final).",
         reconocer="No identifiques el sujeto por la posición, sino por el caso (nominativo: *der, "
                   "die, das, ein, er…*) y por la concordancia con el verbo (singular o plural).",
         traducir="Pon el sujeto delante en español, o mantén el orden alemán con un pronombre de "
                  "refuerzo: «los demás elementos *los* comparte…».",
         ejemplos=[("Diese Aufgabe übernimmt der Scheduler.",
                    "De esta tarea se encarga el planificador."),
                   ("Den Code übersetzt der Compiler.", "El código lo compila el compilador."),
                   ("Erwähnt werden sollte auch die Webseite.", "También debería mencionarse la web.")]),
    dict(clave="nomin", titulo="Estilo nominal e infinitivos sustantivados", aleman="Nominalstil",
         resumen="das Einbinden = el incluir; unter Einhaltung = respetando",
         que="El alemán técnico prefiere sustantivos donde el español usaría verbos. Un infinitivo "
             "se convierte en sustantivo neutro (*das Einbinden*, *das Erlernen* = «el incluir», «el "
             "aprender»), y muchas acciones se expresan con sustantivos en *-ung* dentro de un grupo "
             "con preposición (*unter Einhaltung*, *unter Vernachlässigung*, *bei aktivierter "
             "Option*).",
         forma="• *das* + infinitivo con mayúscula (+ genitivo o *von*): *das Anlegen von Prozessen*\n"
               "• *zum* + infinitivo = para: *Mittel zum Anlegen*\n"
               "• *beim* + infinitivo = al + infinitivo: *beim Übersetzen*\n"
               "• preposición + sustantivo en *-ung* + genitivo: *unter Vernachlässigung des Aufwands*",
         reconocer="Un infinitivo con mayúscula y artículo neutro (*das, dem, zum, beim*); *bei / "
                   "unter / nach / vor* + sustantivo en *-ung*.",
         traducir="Vuelve a convertirlo en verbo: *das Erlernen der Programmierung* → «aprender "
                  "programación»; *unter Vernachlässigung des Aufwands* → «sin tener en cuenta el "
                  "esfuerzo»; *bei aktivierter Option* → «con la opción activada».",
         ejemplos=[("Beim Übersetzen erscheint eine Warnung.", "Al compilar aparece una advertencia."),
                   ("Das Messen der Laufzeit ist einfach.",
                    "Medir el tiempo de ejecución es sencillo."),
                   ("Nach Abschluss der Berechnung …", "Una vez terminado el cálculo…")]),
    dict(clave="guion", titulo="Guion de ahorro", aleman="Ergänzungsstrich",
         resumen="an- und ausschalten = anschalten und ausschalten",
         que="Cuando dos palabras compuestas seguidas comparten una parte, el alemán la escribe una "
             "sola vez y pone un guion en el lugar de la parte que falta.",
         forma="*Dualcore- und Quadcore-CPUs* = Dualcore-CPUs und Quadcore-CPUs\n"
               "*an- und ausschalten* = anschalten und ausschalten\n"
               "*Ein- und Ausgabe* = Eingabe und Ausgabe",
         reconocer="Una palabra que termina en guion seguida de *und*, *oder* o *bzw.*",
         traducir="Completa la palabra cortada con la parte que le falta, que está en la palabra "
                  "siguiente.",
         ejemplos=[("Lese- und Schreibzugriffe", "accesos de lectura y de escritura"),
                   ("Groß- und Kleinbuchstaben", "mayúsculas y minúsculas"),
                   ("Daten- oder Befehlsebene", "nivel de datos o de instrucciones")]),
    dict(clave="conj", titulo="Conjunciones y conectores dobles", aleman="Konjunktionen",
         resumen="sofern, indem, so dass… (verbo al final); weder … noch; nicht …, sondern",
         que="Son las palabras que unen oraciones. Las conjunciones subordinantes envían el verbo "
             "conjugado al final de su oración; los conectores dobles van en pareja y hay que buscar "
             "la segunda parte.",
         forma="• *sofern* = siempre que · *auch wenn* = aunque · *so dass / sodass* = de modo que · "
               "*sobald* = en cuanto · *während* = mientras (que) · *da* = como, ya que\n"
               "• *indem* = modo: se traduce con gerundio (*indem man … sichert* = guardando…)\n"
               "• dobles: *weder … noch* = ni … ni · *einerseits … andererseits* = por un lado … por "
               "otro · *nicht …, sondern …* = no …, sino …",
         reconocer="Tras *sofern, auch wenn, so dass, sobald, während, da, indem*, el verbo conjugado "
                   "está al final de la oración. Si ves *weder*, *einerseits* o *nicht*, busca más "
                   "adelante *noch*, *andererseits* o *sondern*.",
         traducir="Con la conjunción española equivalente; *indem* casi siempre con gerundio.",
         ejemplos=[("Er spart Zeit, indem er die Schleife parallelisiert.",
                    "Ahorra tiempo paralelizando el bucle."),
                   ("Sobald der Thread fertig ist, wartet er.", "En cuanto el hilo termina, espera."),
                   ("Das Programm ist weder schnell noch effizient.",
                    "El programa no es ni rápido ni eficiente.")]),
    dict(clave="formula", titulo="Fórmulas y expresiones fijas", aleman="feste Wendungen",
         resumen="es handelt sich um, es empfiehlt sich, was … angeht, unter X versteht man…",
         que="Expresiones que conviene aprender enteras, porque su significado no se deduce palabra "
             "por palabra.",
         forma="• *es handelt sich um* + A = se trata de\n"
               "• *es empfiehlt sich, … zu …* = es recomendable…\n"
               "• *unter X versteht man Y* = por X se entiende Y\n"
               "• *was X angeht* = en cuanto a X\n"
               "• *es fällt (jdm.) schwer, … zu …* = a alguien le cuesta…; *immer* + comparativo = "
               "cada vez más…\n"
               "• *ausfallen* + adjetivo = resultar…\n"
               "• *Unser Dank gilt* + D = agradecemos a…\n"
               "• *das Moore’sche Gesetz* = la ley de Moore (nombre + *-sch* + terminación)\n"
               "• *jene* = aquellos · *letzterer* = este último · *ohne Anspruch auf "
               "Vollständigkeit* = sin pretender ser exhaustivo",
         reconocer="Cuando la traducción palabra por palabra no tiene sentido, comprueba si es una de "
                   "estas fórmulas.",
         traducir="Como bloque, con la expresión española equivalente.",
         ejemplos=[("Es handelt sich um einen Fehler.", "Se trata de un error."),
                   ("Was die Laufzeit angeht, …", "En cuanto al tiempo de ejecución…"),
                   ("Es fällt mir schwer, das zu erklären.", "Me cuesta explicarlo.")]),
    dict(clave="errata", titulo="Erratas del libro y ortografía antigua",
         aleman="Druckfehler, alte Rechtschreibung",
         resumen="läßt = lässt; für + acusativo; concordancia sujeto-verbo",
         que="El libro es de 2008 y tiene algunas erratas; además usa a veces la ortografía anterior "
             "a la reforma de 1996. Conviene reconocerlas para no aprender formas incorrectas.",
         forma="• Ortografía antigua: *ß* tras vocal breve → hoy *ss*: *läßt* → *lässt*, *schloß* → "
               "*schloss*, *Kontrollfluß* → *Kontrollfluss*. Tras vocal larga sigue siendo *ß* "
               "(*groß*).\n"
               "• p. V: *Produktivitätzuwächse … steigt* → *Produktivitätszuwächse … steigen*\n"
               "• p. 19: *für … einem seriellen Anteil* → *für … einen seriellen Anteil*\n"
               "• p. 21: *die tatsächliche erreichte Leistung* → *die tatsächlich erreichte "
               "Leistung*",
         reconocer="Reglas útiles: tras *für* siempre acusativo; el verbo concuerda en número con el "
                   "sujeto aunque esté lejos; un adverbio delante de un participio no lleva "
                   "terminación.",
         traducir="Lee la forma correcta y tradúcela normalmente.",
         ejemplos=[("Das lässt sich messen. (antes: läßt)", "Eso se puede medir."),
                   ("für einen seriellen Anteil von 4 %", "para una fracción serial del 4 %"),
                   ("die tatsächlich erreichte Leistung", "el rendimiento realmente alcanzado")]),
]

# ================================================================ PÁGINA A PÁGINA
# (página del libro, apartado, vocabulario en orden de aparición)
PAGINAS = [
    ("V", "Vorwort", [
        N("die", "Einführung", "Einführungen", "introducción; aquí: lanzamiento (de una tecnología)"),
        N("der", "Arbeitsplatzrechner", "Arbeitsplatzrechner", "ordenador de escritorio"),
        N("die", "Fähigkeit", "Fähigkeiten", "capacidad"),
        X("echt", "Adj./Adv.", "aquí: realmente (echt gleichzeitig = realmente a la vez)"),
        N("der", "Rechner", "Rechner", "ordenador, computadora"),
        V("ausführen", "führt aus", "führte aus", "hat ausgeführt", None, "téc. ejecutar"),
        V("sich verfestigen", "verfestigt sich", "verfestigte sich", "hat sich verfestigt", None,
          "consolidarse"),
        X("derartig", "Adj.", "semejante, de este tipo (derartige Prozessoren)"),
        V("ausnutzen", "nutzt aus", "nutzte aus", "hat ausgenutzt", None, "aprovechar (al máximo)"),
        X("zwingend", "Adj./Adv.", "obligatorio (zwingend notwendig = absolutamente necesario)"),
        N("die", "Anwendung", "Anwendungen", "téc. aplicación, programa (normalmente: uso, empleo)"),
        V("parallelisieren", "parallelisiert", "parallelisierte", "hat parallelisiert", None,
          "paralelizar"),
        V("verstehen", "versteht", "verstand", "hat verstanden", "unter + D",
          "entender por (unter X versteht man Y)"),
        N("die", "Parallelisierung", "Parallelisierungen", "paralelización"),
        X("nebeneinander", "Adv.", "uno al lado del otro; aquí: en paralelo"),
        N("die", "Gesamtaufgabe", "Gesamtaufgaben", "tarea completa, tarea global"),
        X("seriell", "Adj.", "serial, secuencial (= sequenziell)"),
        N("die", "Verarbeitung", "Verarbeitungen", "procesamiento"),
        X("dabei", "Adv.", "en ello, al respecto; aquí: y es que"),
        V("zwingen", "zwingt", "zwang", "hat gezwungen", "A + zu + Inf.",
          "obligar a alguien a hacer algo"),
        N("der", "Entwurf", "Entwürfe", "diseño; también: borrador"),
        X("langfristig", "Adj./Adv.", "a largo plazo"),
        V("sich befassen", "befasst sich", "befasste sich", "hat sich befasst", "mit + D",
          "ocuparse de"),
        V("sich verdoppeln", "verdoppelt sich", "verdoppelte sich", "hat sich verdoppelt", None,
          "duplicarse"),
        N("der", "Zuwachs", "Zuwächse", "aumento (Produktivitätszuwachs = aumento de productividad)"),
        N("das", "Entwurfswerkzeug", "Entwurfswerkzeuge", "herramienta de diseño"),
        X("zur Verfügung stehen / stellen", "Ausdruck",
          "estar disponible / poner a disposición (stand, hat gestanden · stellte, hat gestellt)"),
        N("das", "Bauteil", "Bauteile", "componente, pieza"),
    ]),
    ("VI", "Vorwort", [
        V("verplanen", "verplant", "verplante", "hat verplant", None,
          "aquí: planificar el uso de (normalmente: comprometer tiempo o dinero)"),
        N("der", "Ausweg", "Auswege", "salida, solución"),
        N("die", "Funktionseinheit", "Funktionseinheiten", "unidad funcional"),
        V("schwerfallen", "fällt schwer", "fiel schwer", "ist schwergefallen", "+ D",
          "resultar difícil (es fällt schwer, … zu …)"),
        N("die", "Einhaltung", None, "cumplimiento, respeto (unter Einhaltung + G = respetando)"),
        X("gegeben", "Adj.", "dado (eine gegebene Leistungsaufnahme; ein Problem gegebener Größe)"),
        N("die", "Leistungsaufnahme", None, "consumo de potencia (eléctrica)"),
        V("verarbeiten", "verarbeitet", "verarbeitete", "hat verarbeitet", None, "procesar"),
        V("erhöhen", "erhöht", "erhöhte", "hat erhöht", None, "aumentar"),
        N("die", "Taktrate", "Taktraten", "frecuencia de reloj (= die Taktfrequenz)"),
        N("die", "Transistorstruktur", "Transistorstrukturen", "estructura de transistores"),
        X("sogenannt", "Adj.", "llamado, denominado"),
        N("der", "Leckstrom", "Leckströme", "corriente de fuga"),
        V("zunehmen", "nimmt zu", "nahm zu", "hat zugenommen", None,
          "aumentar, crecer (también: engordar)"),
        N("der", "Informatiker", "Informatiker", "informático"),
        N("das", "Erlernen", None, "aprendizaje (de erlernen = aprender a fondo)"),
        X("unabdingbar", "Adj.", "imprescindible"),
        X("verständlich", "Adj.", "comprensible"),
        V("durchführen", "führt durch", "führte durch", "hat durchgeführt", None,
          "llevar a cabo, realizar"),
        X("vorliegend", "Adj.", "presente (das vorliegende Buch = este libro)"),
        V("berücksichtigen", "berücksichtigt", "berücksichtigte", "hat berücksichtigt", None,
          "tener en cuenta"),
        N("die", "Öffentlichkeit", None, "el público, la opinión pública"),
        X("zugänglich", "Adj.", "accesible (zugänglich machen = hacer público)"),
        N("der", "Helfer", "Helfer", "ayudante, colaborador"),
        N("der", "Dank", None, "agradecimiento (unser Dank gilt + D = agradecemos a)"),
        N("das", "Korrekturlesen", None, "corrección de pruebas"),
        N("der", "Verlag", "Verlage", "editorial"),
        N("die", "Zusammenarbeit", None, "colaboración"),
        N("die", "Unterstützung", "Unterstützungen", "apoyo (technische Unterstützung = soporte técnico)"),
        N("die", "Zeitersparnis", "Zeitersparnisse", "ahorro de tiempo"),
    ]),
    (1, "Kap. 1 · Einführung", [
        N("die", "Programmierschnittstelle", "Programmierschnittstellen", "interfaz de programación (API)"),
        N("die", "Parallelität", None, "paralelismo"),
        V("spezifizieren", "spezifiziert", "spezifizierte", "hat spezifiziert", None,
          "especificar, definir con precisión"),
        X("konkurrierend", "Adj.", "que compite, alternativo", "konkurrierende Ansätze"),
        N("der", "Ansatz", "Ansätze", "enfoque, planteamiento"),
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
        V("sich zusammensetzen", "setzt sich zusammen", "setzte sich zusammen",
          "hat sich zusammengesetzt", "aus + D", "componerse de"),
        N("die", "Menge", "Mengen", "téc. conjunto (en matemáticas; normalmente: cantidad)"),
        N("die", "Compilerdirektive", "Compilerdirektiven", "directiva de compilador"),
        N("die", "Bibliotheksfunktion", "Bibliotheksfunktionen", "función de biblioteca"),
        N("die", "Umgebungsvariable", "Umgebungsvariablen", "variable de entorno"),
        X("portabel", "Adj.", "portable (funciona en distintas plataformas)", "ein portables Modell"),
        N("das", "Programmiermodell", "Programmiermodelle", "modelo de programación"),
        N("der", "Hersteller", "Hersteller", "fabricante"),
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
    ]),
    (3, "1.1 Merkmale von OpenMP", [
        X("genannt", "Part. II", "llamado, denominado (de nennen)", "(auch Pragma genannte)"),
        V("bewirken", "bewirkt", "bewirkte", "hat bewirkt", None, "provocar, hacer que"),
        X("folgend", "Adj.", "siguiente"),
        N("die", "Schleife", "Schleifen", "téc. bucle (normalmente: lazo)"),
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
    ]),
    (4, "1.1 Merkmale von OpenMP", [
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
        V("anweisen", "weist an", "wies an", "hat angewiesen", "A + zu + Inf.",
          "ordenar a alguien que haga algo"),
        N("der", "Codeabschnitt", "Codeabschnitte", "sección de código"),
        N("die", "Klausel", "Klauseln", "cláusula"),
        N("das", "Verhalten", None, "comportamiento"),
        V("sich beziehen", "bezieht sich", "bezog sich", "hat sich bezogen", "auf + A",
          "referirse a"),
        X("gültig", "Adj.", "válido"),
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
        X("demnach", "Adv.", "según esto, por consiguiente"),
        X("zum Teil", "Adv.", "en parte"),
        X("vorab", "Adv.", "de antemano, previamente"),
        N("die", "Berücksichtigung", None,
          "consideración (Berücksichtigung finden = tenerse en cuenta)"),
        X("verbleibend", "Adj.", "restante"),
        X("einführend", "Adj.", "introductorio"),
        N("der", "Überblick", "Überblicke", "visión general, panorama"),
        N("die", "Parallelverarbeitung", None, "procesamiento en paralelo"),
        N("der", "Mehrkernprozessor", "Mehrkernprozessoren",
          "procesador multinúcleo (= der Multicoreprozessor)"),
        N("die", "Leistungsmessung", "Leistungsmessungen", "medición del rendimiento"),
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
        N("die", "Reaktionsgeschwindigkeit", "Reaktionsgeschwindigkeiten", "velocidad de respuesta"),
        N("die", "Benutzereingabe", "Benutzereingaben", "entrada del usuario"),
        N("die", "Oberfläche", "Oberflächen",
          "téc. interfaz (grafische Oberfläche) (normalmente: superficie)"),
        X("gemeinsam genutzt", "Adj.", "compartido"),
        N("der", "Adressraum", "Adressräume", "espacio de direcciones"),
    ]),
    (10, "1.2.1 → 1.2.2 Parallele Hardwarearchitekturen", [
        X("ökonomisch", "Adj.", "económico; aquí: eficiente (ökonomischer = más eficiente)"),
        V("vollziehen", "vollzieht", "vollzog", "hat vollzogen", None, "realizar, llevar a cabo"),
        X("statt", "Präp./Konj.", "en lugar de (statt … zu + Inf.)"),
        X("tatsächlich", "Adj./Adv.", "real(mente), efectivamente"),
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
        V("erzielen", "erzielt", "erzielte", "hat erzielt", None, "lograr, obtener"),
        N("die", "Gültigkeitsdauer", None, "período de validez"),
        V("vorhersagen", "sagt vorher", "sagte vorher", "hat vorhergesagt", None,
          "predecir, pronosticar"),
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
        X("weder … noch", "Konj.", "ni … ni"),
        N("der", "Datenstrom", "Datenströme", "flujo de datos"),
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
        X("verschieden viele", "Ausdruck", "distintas cantidades de"),
        X("stattdessen", "Adv.", "en su lugar, en cambio"),
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
    ]),
    (21, "1.2.5 · final del capítulo", [
        X("unerlässlich", "Adj.", "imprescindible"),
        N("die", "Einschränkung", "Einschränkungen", "restricción, limitación"),
        N("der", "Codebestandteil", "Codebestandteile", "parte del código"),
        V("skalieren", "skaliert", "skalierte", "hat skaliert", None, "escalar"),
        X("erst", "Adv.", "no antes de, solo (erst im Betrieb = solo cuando ya funciona)"),
        N("der", "Betrieb", None, "téc. funcionamiento (im Betrieb) (normalmente: empresa)"),
        X("entscheidend", "Adj./Adv.", "decisivo, de forma decisiva"),
    ]),
]

# ================================================================ GRAMÁTICA EN EL TEXTO
# Por página: fragmento BREVE del libro («…» recorta) y su análisis pieza a pieza. Cada nota
# remite al § de su tipo en GRAMATICA (verificar() lo exige).
NOTAS = {
    "V": [
        G("infzu", "Seit der Einführung … haben … die Fähigkeit, … auszuführen",
          "Dos cosas. (1) **seit + presente**: *seit der Einführung … haben* describe algo que "
          "empezó en 2002 y sigue siendo verdad; en español también usamos presente: «desde la "
          "introducción… tienen». (2) **Sustantivo + infinitivo con zu** (§15): *die Fähigkeit* "
          "anuncia un infinitivo que llega dos líneas después (*auszuführen*, con el *zu* dentro del "
          "separable *aus·führen*): «tienen la capacidad de ejecutar dos programas a la vez»."),
        G("guion", "mit den aktuellen Dualcore- und Quadcore-CPUs",
          "**Guion de ahorro** (§19): el guion tras *Dualcore-* sustituye a *CPUs*, que solo se "
          "escribe una vez, al final. Completa: *Dualcore-CPUs und Quadcore-CPUs* → «las CPU "
          "actuales de doble y de cuádruple núcleo»."),
        G("infzu", "Um … ausnutzen zu können, ist es zwingend notwendig, … zu parallelisieren",
          "Dos infinitivos con *zu* (§15). *Um … ausnutzen zu können* es una **oración final** "
          "(«para…») con verbo modal: el modal va al final (*zu können*) y el verbo principal "
          "delante (*ausnutzen*): «para poder aprovechar…». Después, *es ist … notwendig, … zu "
          "parallelisieren*: *es* anuncia el infinitivo (§16): «es absolutamente necesario "
          "paralelizar las aplicaciones»."),
        G("formula", "Unter der Parallelisierung … versteht man, dass …",
          "**Fórmula de definición** (§21): *unter X versteht man Y* = «por X se entiende Y». Aquí Y "
          "es toda la oración con *dass*: «por paralelización de un programa se entiende que varias "
          "partes de una tarea se ejecutan a la vez…»."),
        G("infzu", "zwingen … jeden Programmierer, sich … zu befassen",
          "**zwingen + acusativo + zu + infinitivo** (§15): *zwingen* («obligar») pide a quién "
          "(acusativo: *jeden Programmierer*) y a qué (infinitivo con *zu* al final). El verbo es "
          "reflexivo (*sich befassen mit* = ocuparse de) y el *sich* se adelanta: «obligan a todo "
          "programador a ocuparse a largo plazo de la programación paralela»."),
        G("errata", "Die Produktivitätzuwächse … steigt …",
          "**Dos erratas** (§22). (1) En el compuesto falta la *s* de unión: lo correcto es "
          "*Produktivitätszuwächse*. (2) El sujeto es plural (*die … Zuwächse*), así que el verbo "
          "debe ir en plural: *steigen*. Idea: «los aumentos de productividad… solo crecen a un ritmo "
          "mucho menor»."),
        G("part", "die Anzahl der zur Verfügung stehenden Bauteile",
          "**Atributo participial** (§1): entre el artículo *der* y el sustantivo *Bauteile* va "
          "*zur Verfügung stehenden*, participio I de la expresión *zur Verfügung stehen* («estar "
          "disponible», §11). Truco: *der* → busca el sustantivo (*Bauteile*) → vuelve atrás: «el "
          "número de componentes que están disponibles», es decir, «de componentes disponibles»."),
    ],
    "VI": [
        G("infzu", "Ein „einfacher“ Ausweg ist es, … zu replizieren",
          "**es + infinitivo con zu** (§16, §15): *es* ocupa el lugar del sujeto y anuncia el "
          "infinitivo del final (*zu replizieren*). Lo que se dice es: «replicar unidades "
          "funcionales (como CPU enteras) es una salida “fácil”». Las comillas en *„einfacher“* "
          "marcan ironía: no es tan fácil."),
        G("formula", "fällt es immer schwerer, … zu erhöhen",
          "Dos fórmulas (§21). *es fällt schwer, … zu* + infinitivo = «resulta difícil…» (el *es* "
          "anuncia el infinitivo *zu erhöhen*, §16). *immer* + comparativo = «cada vez más»: *immer "
          "schwerer* = «cada vez más difícil». Junto: «cada vez resulta más difícil aumentar la "
          "velocidad…»."),
        G("nomin", "unter Einhaltung einer … Leistungsaufnahme",
          "**Estilo nominal** (§18): en lugar de un verbo («respetar») el alemán usa *unter* + "
          "sustantivo en *-ung* (*Einhaltung*, de *einhalten* = cumplir) + genitivo (*einer … "
          "Leistungsaufnahme*). Tradúcelo con un verbo: «respetando un consumo eléctrico máximo "
          "dado»."),
        G("rel", "die Geschwindigkeit, mit der … verarbeitet werden",
          "**Relativo con preposición** (§14) + **pasiva** (§3): *mit der* = «con la que» (femenino "
          "porque se refiere a *Geschwindigkeit*); dentro, pasiva en presente con el verbo al final "
          "(*verarbeitet werden*): «la velocidad con la que se procesan los hilos individuales»."),
        G("nomin", "das Erlernen der parallelen Programmierung",
          "**Infinitivo sustantivado** (§18): *erlernen* («aprender a fondo») se convierte en "
          "sustantivo neutro con mayúscula (*das Erlernen*) y lleva un genitivo detrás. Tradúcelo "
          "con infinitivo o con «el aprendizaje de»: «aprender programación paralela (es "
          "imprescindible)»."),
        G("infzu", "eine Programmiertechnik, diese … durchführen zu können",
          "**Infinitivo con zu y modal** (§15) que completa al sustantivo *Programmiertechnik*: "
          "*diese … durchführen zu können* = «para poder realizarla», donde *diese* se refiere a la "
          "programación paralela de la frase anterior. La frase del original es algo torpe; la idea "
          "es: «OpenMP es una técnica que permite hacerla de forma fácil y comprensible»."),
        G("infzu", "Das Ziel des vorliegenden Buches ist es, … vorzustellen",
          "**es + infinitivo con zu** (§16, §15): *es* anuncia el infinitivo del final. En el "
          "separable *vorstellen* («presentar») el *zu* va dentro: *vor·zu·stellen*. «El objetivo de "
          "este libro es presentar OpenMP desde la perspectiva del programador de C/C++»."),
        G("pasmod", "wird der … Entwurf …, die … gemacht worden ist, berücksichtigt",
          "**Pasiva** (§3) con una relativa en medio. La oración principal es *Dabei wird der "
          "aktuelle Entwurf … berücksichtigt* = «se tiene en cuenta el borrador actual». Entre "
          "medias, la relativa *die … zugänglich gemacht worden ist* está en **perfecto pasivo** "
          "(*gemacht worden ist* = «ha sido hecha»), y *die* se refiere a *Spezifikation* "
          "(femenino): «la especificación 3.0, que acaba de hacerse pública»."),
        G("formula", "Unser Dank gilt … für …",
          "**Fórmula de agradecimiento** (§21): *jemandes Dank gilt* + dativo = «el agradecimiento "
          "va para». *gelten* no significa aquí «valer» sino «ir dirigido a»: «agradecemos a Anke… "
          "y a Sandra… la corrección de pruebas»."),
    ],
    1: [
        G("rel", "mit deren Hilfe … spezifiziert werden kann",
          "**Relativo en genitivo** (§14) + **pasiva con modal** (§3). *deren* es el relativo en "
          "genitivo femenino (se refiere a *Programmierschnittstelle*, femenino) = «cuya, de la "
          "cual»; *mit deren Hilfe* = «con cuya ayuda», o sea «mediante la cual». Al final, "
          "*spezifiziert werden kann* = «se puede especificar» (el modal conjugado va al final por "
          "ser una relativa). «Una interfaz mediante la cual se puede especificar el paralelismo en "
          "programas de C, C++ y Fortran»."),
        G("trenn", "trägt … zu der Lesbarkeit … bei",
          "**Verbo separable** (§12): *trägt* solo significa «lleva», pero al final de la oración "
          "está el prefijo *bei*: el verbo es *beitragen zu* («contribuir a»). Entre *trägt* y *bei* "
          "hay seis palabras. «Contribuye considerablemente a la legibilidad del código "
          "resultante»."),
        G("conj", "– sofern sich OpenMP … eignet –",
          "**Conjunción subordinante** (§20) dentro de un inciso entre guiones: *sofern* («siempre "
          "que») manda el verbo al final (*eignet*), y el reflexivo *sich* va pronto, justo después "
          "de la conjunción. «…siempre que OpenMP sea adecuado para especificar el paralelismo "
          "deseado…». En una primera lectura puedes saltarte el inciso."),
        G("pasmod", "müssen nur … Anweisungen … eingefügt werden",
          "**Pasiva con modal** (§3): el modal *müssen* está conjugado en 2.ª posición y al final "
          "van el participio (*eingefügt*) y *werden*. El sujeto (*ein paar zusätzliche "
          "Anweisungen*) queda en medio. Tradúcelo con «hay que»: «a menudo solo hay que insertar "
          "unas pocas instrucciones adicionales para el compilador»."),
        G("infzu", "Das Ziel … ist es, … zur Verfügung zu stellen",
          "Como en la p. VI (§16, §15): *es* anuncia el infinitivo con *zu* del final (*zur "
          "Verfügung zu stellen*, verbo funcional de §11 = «ofrecer»). «El objetivo de OpenMP es "
          "ofrecer un modelo de programación portable para arquitecturas de memoria compartida»."),
    ],
    2: [
        G("rel", "mit Hilfe derer sich … lässt",
          "**Relativo en genitivo** (§14): *derer* es otra forma del genitivo femenino (*deren*) que "
          "se usa detrás de *mit Hilfe*; se refiere a *Kommandozeilenoption* (femenino). *mit Hilfe "
          "derer* = «con ayuda de la cual». Es la misma idea que *mit deren Hilfe* (p. 1), con otro "
          "orden."),
        G("lassen", "… an- und ausschalten lässt",
          "**sich lassen + infinitivo** (§6) = «se puede + infinitivo». El *sich* aparece al "
          "principio de la relativa y *lässt* al final (por ser relativa). Además hay un **guion de "
          "ahorro** (§19): *an- und ausschalten* = *anschalten und ausschalten*. «Una opción con la "
          "que se puede activar y desactivar la interpretación de las directivas de OpenMP»."),
        G("lassen", "Wie das „Open“ … vermuten lässt",
          "**lassen + infinitivo sin sich** (§6): *etwas vermuten lassen* = «dejar suponer, hacer "
          "pensar». *Wie* no es aquí «cómo» sino «como» (comparación): «como ya deja suponer el "
          "“Open” del nombre…». El inciso *– das „MP“ steht für multi processing –* explica la "
          "sigla: «MP significa multi processing»."),
        G("part", "die – … ausgezeichnet lesbare – … Spezifikation",
          "**Atributo extendido** (§1): entre el artículo *die* y el sustantivo *Spezifikation* los "
          "autores meten, entre guiones, un inciso con adjetivo: *für ein technisches Dokument "
          "ausgezeichnet lesbare* («excelentemente legible para ser un documento técnico»). Lee "
          "primero *die … offizielle OpenMP-Spezifikation* y después el inciso: «la especificación "
          "oficial, que para ser un documento técnico se lee muy bien»."),
        G("orden", "Ebenfalls erwähnt werden sollte die Webseite …",
          "**Orden de palabras** (§17) + **pasiva con modal** (§3): delante del verbo conjugado "
          "(*sollte*) va el participio *erwähnt*, y el sujeto (*die Webseite …*) queda detrás de "
          "todo. En orden neutro sería *Die Webseite … sollte ebenfalls erwähnt werden*. «También "
          "debería mencionarse la página web de la comunidad de usuarios de OpenMP»."),
    ],
    3: [
        G("part", "die in Zeile 4 folgende for-Schleife",
          "**Atributo participial extendido** (§1): el artículo *die* va seguido de una preposición "
          "(*in Zeile 4*), señal de que el sustantivo llega después. Participio I *folgende* (de "
          "*folgen*, «seguir») + sustantivo *for-Schleife*: «el bucle for que sigue en la línea 4». "
          "La frase dice que la directiva hace que varios hilos ejecuten ese bucle en paralelo."),
        G("pasimp", "auf welche Bereiche … zugegriffen wird",
          "**Pasiva impersonal** (§4): *zugreifen auf* («acceder a») no tiene complemento directo, "
          "así que su pasiva no tiene sujeto; el complemento conserva la preposición (*auf welche "
          "Bereiche*). Además es una pregunta indirecta (verbo al final): «(la cuestión de) a qué "
          "zonas del vector accede cada uno de los hilos»."),
        G("infzu", "Ohne auf Details … näher einzugehen, …",
          "**ohne … zu + infinitivo** (§15) = «sin + infinitivo». El infinitivo *einzugehen* (de "
          "*auf etwas eingehen*, «entrar en algo», con el *zu* dentro del separable) llega al final "
          "de un inciso de tres líneas: «sin entrar todavía en detalles (como el número exacto de "
          "hilos…), se ve lo siguiente:»."),
        G("gerund", "den sequentiell auszuführenden Anweisungen",
          "**Gerundivo** (§2): *zu* + participio I como adjetivo, con sentido pasivo de obligación. "
          "En el separable *ausführen* el *zu* va dentro: *aus·zu·führend-en*. *den … Anweisungen* "
          "es dativo plural (va detrás de *zwischen*): «entre las instrucciones que deben ejecutarse "
          "secuencialmente»."),
        G("es", "Diese Anweisung ist es, die …",
          "**Oración escindida con es** (§16): sirve para destacar un elemento. *X ist es, die / "
          "der / das …* = «es X el / la que…»: «es esta instrucción la que se ejecuta en paralelo»."),
        G("conj", "nicht (wesentlich) verändert, sondern nur ergänzt werden muss",
          "**nicht …, sondern …** (§20) = «no …, sino …», con una **pasiva con modal** (§3) "
          "compartida: *verändert (werden muss)* y *ergänzt werden muss*. La oración empieza por "
          "*Da* («como, ya que»), por eso el verbo va al final: «como el código no tiene que "
          "modificarse (sustancialmente), sino solo ampliarse…»."),
        G("seinzu", "sind … einfach auf Korrektheit zu testen",
          "**sein + zu + infinitivo** (§7): sin otro verbo, *sind … zu testen* equivale a *können "
          "getestet werden* («se pueden comprobar»). Con *einfach*: «las paralelizaciones con "
          "OpenMP son fáciles de comprobar (en cuanto a su corrección)»."),
    ],
    4: [
        G("es", "Es stehen … Compiler … zur Verfügung",
          "**es de relleno** (§16): *es* ocupa la primera posición para que el sujeto real "
          "(*OpenMP-fähige Compiler*, plural) pueda ir detrás; por eso el verbo está en plural "
          "(*stehen*). Con el verbo funcional *zur Verfügung stehen* (§11): «hay compiladores "
          "compatibles con OpenMP de varios fabricantes»."),
        G("conj", "Auch wenn es … Unterschiede … gibt",
          "**auch wenn** (§20) = «aunque»: introduce una subordinada con el verbo al final (*gibt*); "
          "*es gibt* = «hay». «Aunque en la práctica haya pequeñas diferencias en la implementación "
          "concreta del estándar, cualquiera de estos compiladores puede procesar código OpenMP "
          "correcto»."),
        G("seinzu", "OpenMP ist einfach zu verwenden",
          "**sein + adjetivo + zu + infinitivo** (§7) = «ser fácil / difícil de + infinitivo»: "
          "«OpenMP es fácil de usar». Igual: *schwer zu verstehen* = «difícil de entender»."),
        G("infzu", "weisen den Compiler an, … zu parallelisieren",
          "**Verbo separable + infinitivo con zu** (§12, §15): *weisen … an* = *anweisen* "
          "(«ordenar, indicar»), que pide un acusativo (*den Compiler*) y un infinitivo con *zu* "
          "(*bestimmte Codeabschnitte zu parallelisieren*): «las directivas indican al compilador "
          "que paralelice determinadas secciones de código»."),
        G("rel", "…, auf die sie sich beziehen",
          "**Relativo con preposición** (§14): el verbo es *sich beziehen auf* («referirse a»); la "
          "preposición *auf* va delante del relativo *die* (acusativo femenino, se refiere a "
          "*Direktive*), y el verbo al final: «las cláusulas modifican el comportamiento de la "
          "directiva a la que se refieren»."),
    ],
    5: [
        G("korr", "werden … dazu verwendet, … abzufragen",
          "**Correlato dazu … zu** (§13): *dazu* anuncia la finalidad, que llega después como "
          "infinitivo con *zu* (*abzufragen bzw. zu setzen*). La oración principal está en pasiva "
          "(§3): *werden … verwendet*. «Las funciones de la biblioteca se usan principalmente para "
          "consultar o fijar parámetros del entorno de ejecución»."),
        G("v1", "Möchte man …, so muss …",
          "**Condicional sin «wenn»** (§8): la oración empieza por el verbo conjugado *Möchte* y no "
          "es una pregunta; equivale a *Wenn man … verwenden möchte*. La principal empieza por *so* "
          "+ verbo, con una pasiva con modal (*muss … eingebunden werden*, §3): «si se quieren usar "
          "funciones de la biblioteca, hay que incluir el archivo de cabecera omp.h»."),
        G("pasimp", "kann auf das Einbinden … verzichtet werden",
          "**Pasiva impersonal** (§4) con *verzichten auf* («prescindir de»): no hay sujeto y el "
          "complemento conserva *auf*. *das Einbinden* es un **infinitivo sustantivado** (§18): «el "
          "incluir». «Si la aplicación solo usa pragmas, en teoría se puede prescindir de incluir "
          "omp.h»."),
        G("formula", "Es empfiehlt sich also, … zu inkludieren",
          "**Fórmula** (§21) con *es* que anuncia un infinitivo (§16): *es empfiehlt sich, … zu …* "
          "= «es recomendable…». «Así que es recomendable incluir omp.h en todos los programas que "
          "se vayan a paralelizar»."),
        G("gerund", "für alle zu parallelisierenden Programme",
          "**Gerundivo** (§2): *zu* + participio I (*parallelisierend*) con terminación de "
          "adjetivo. Sentido pasivo de obligación o intención: «para todos los programas que se "
          "vayan a paralelizar»."),
        G("v1", "Sollte ein Compiler … nicht unterstützen, so …",
          "**Condicional sin «wenn» con sollte** (§8): *sollte* al principio añade la idea de «en "
          "caso de que, si por casualidad». La principal empieza por *so*: «si un compilador no "
          "soportara OpenMP, tampoco conocería omp.h»."),
        G("nomin", "bei aktivierter OpenMP-Option",
          "**Estilo nominal** (§18): *bei* + participio usado como adjetivo (*aktivierter*, dativo "
          "femenino) + sustantivo, en lugar de una oración (*wenn die Option aktiviert ist*): «con "
          "la opción de OpenMP activada, la variable _OPENMP está definida»."),
    ],
    6: [
        G("pasmod", "so dass … einbezogen oder … ausgeschlossen werden können",
          "*so dass* (§20) introduce una consecuencia con el verbo conjugado al final (*können*). "
          "Dentro, **pasiva con modal** (§3) con dos participios coordinados (*einbezogen oder … "
          "ausgeschlossen*) que comparten *werden können*. *von ihr* = «de ella» (de la "
          "compilación): «…de modo que ciertas secciones de código puedan incluirse en la "
          "compilación o excluirse de ella»."),
        G("formula", "(ohne Anspruch auf Vollständigkeit)",
          "**Fórmula fija** (§21): *der Anspruch auf* = «la pretensión de»: «(sin pretender que la "
          "lista sea completa)»."),
        G("guion", "in der Professional- bzw. Team Edition-Variante",
          "**Guion de ahorro** (§19): *Professional-* = *Professional-Edition-Variante*; *bzw.* = "
          "«o bien»: «en la variante Professional o en la Team Edition»."),
        G("lassen", "lässt sich über dessen Eigenschaften … aktivieren",
          "**sich lassen + infinitivo** (§6) = «se puede activar». *dessen* (§14) es un "
          "demostrativo en genitivo = «sus (de él)» y se refiere a *jedes C/C++-Projekt*; los "
          "autores lo usan en lugar de *seine* para que quede claro de quién son las propiedades: "
          "«en cada proyecto se puede activar, en sus propiedades, el interruptor “OpenMP "
          "support”»."),
        G("v1", "Soll OpenMP zum Einsatz kommen, muss …",
          "**Condicional sin «wenn»** (§8) con *soll* al principio (= *wenn OpenMP zum Einsatz "
          "kommen soll*). *zum Einsatz kommen* es un verbo funcional (§11) = «usarse». «Si se quiere "
          "usar OpenMP, hay que compilar el programa con la opción -fopenmp»."),
    ],
    7: [
        G("v1", "Werden die o. g. Compileroptionen aktiviert, wird …",
          "**Condicional sin «wenn» en pasiva** (§8, §3): *Werden … aktiviert* = *Wenn die … "
          "Compileroptionen aktiviert werden* («si se activan las opciones mencionadas»). La "
          "principal también empieza por el verbo: *wird auch … definiert* («también se define…»). "
          "*o. g.* = *oben genannt*, «arriba mencionado»."),
        G("part", "die im vorigen Abschnitt beschriebene Variable",
          "**Atributo participial** (§1) con participio II (*beschrieben*, sentido pasivo): «la "
          "variable descrita en el apartado anterior». En la misma página: *ein mit OpenMP "
          "parallelisiertes Programm* = «un programa paralelizado con OpenMP»."),
        G("infzu", "so genügt es, … neu zu übersetzen",
          "**es + infinitivo con zu** (§16, §15): *es genügt, … zu* = «basta con…». Va detrás de una "
          "condicional sin *wenn* (*Möchte man …*, §8), por eso empieza con *so*: «…basta con volver "
          "a compilar el código sin las opciones correspondientes»."),
        G("pasmod", "… zugänglich gemacht worden",
          "**Pluscuamperfecto pasivo** (§3): *war … gemacht worden* (el *war* está antes, compartido "
          "con *waren … aktuell*). *worden* (¡no *geworden*!) indica pasiva en tiempo compuesto. "
          "*zugänglich machen* = «hacer accesible, publicar»: «un borrador de la especificación 3.0 "
          "acababa de hacerse público»."),
        G("zustand", "die zum Teil bereits vorab … implementiert waren",
          "**Pasiva de estado en pasado** (§5): *waren* + participio II = «estaban implementadas» "
          "(el resultado, no la acción): «novedades que en parte ya estaban implementadas de "
          "antemano en algunos compiladores»."),
        G("fvg", "finden … bereits Berücksichtigung",
          "**Verbo funcional** (§11): *Berücksichtigung finden* = *berücksichtigt werden* «tenerse "
          "en cuenta»; *finden* no significa aquí «encontrar»: «estas construcciones ya se tienen en "
          "cuenta en este libro»."),
    ],
    8: [
        G("part", "Mit diesen Themen bereits vertraute Leser",
          "**Atributo adjetival extendido** (§1): delante de *Leser* va un grupo entero, *mit "
          "diesen Themen bereits vertraute* (*vertraut mit* = «familiarizado con»). No hay artículo "
          "porque *Leser* está en plural indefinido: «los lectores que ya estén familiarizados con "
          "estos temas pueden pasar directamente al capítulo 3»."),
        G("orden", "Als Prozess bezeichnet man ein Programm, das …",
          "**Orden de palabras** (§17): *bezeichnen als* = «llamar, denominar»; aquí el complemento "
          "*Als Prozess* va delante del verbo y el objeto (*ein Programm, das …*) detrás. En orden "
          "neutro: *Man bezeichnet ein Programm, das … ausgeführt wird, als Prozess*. «Se llama "
          "proceso a un programa que el sistema operativo está ejecutando»."),
        G("formula", "handelt es sich … um eine aktive Instanz",
          "**Fórmula** (§21): *es handelt sich um* + acusativo = «se trata de»; el *es* es fijo (no "
          "significa «ello»). Tras *Im Gegensatz zum … Programmcode* («a diferencia del código "
          "estático») el verbo va en 2.ª posición y *es* detrás: «se trata, pues, de una instancia "
          "activa del código»."),
        G("v1", "Können in einem System … aktiv sein, bezeichnet man …",
          "**Condicional sin «wenn»** (§8): *Können* al principio = *Wenn … mehrere Prozesse "
          "gleichzeitig aktiv sein können*. La principal también empieza por el verbo (*bezeichnet "
          "man dies als …*): «si en un sistema pueden estar activos varios procesos a la vez, se "
          "habla de un sistema de tiempo compartido o multitarea»."),
        G("korr", "kommt daher, dass … · dadurch …, dass …",
          "**Correlatos** (§13): *daher kommen, dass* = «deberse a que»; *dadurch, dass* = «por el "
          "hecho de que, gracias a que». Aquí: el nombre *time-sharing* se debe a que la "
          "simultaneidad solo se simula, por el hecho de que cada proceso se ejecuta varias veces "
          "por segundo durante muy poco tiempo."),
    ],
    9: [
        G("zustand", "in dem globale Variablen abgelegt sind",
          "**Pasiva de estado** (§5): *sind abgelegt* = «están almacenadas» (el resultado). Compara "
          "con la pasiva de acción *abgelegt werden* = «se almacenan», que aparece unas líneas más "
          "abajo. *in dem* es un relativo con preposición (§14) = «en el que»."),
        G("nomin", "Mittel zum Anlegen von Prozessen",
          "**Infinitivo sustantivado con zum** (§18): *zum* (= *zu dem*) + infinitivo con mayúscula "
          "expresa finalidad = «para + infinitivo»; *anlegen* tiene aquí el sentido técnico de "
          "«crear»: «medios para crear procesos»."),
        G("part", "des derzeit dort ausgeführten Prozesses Q",
          "**Atributo participial** (§1) en genitivo: *des … Prozesses* y, entre medias, *derzeit "
          "dort ausgeführten* («ejecutado en ese momento allí»): «el estado actual del proceso Q que "
          "se está ejecutando allí en ese momento»."),
        G("conj", "…, indem alle … Elemente … abgelegt werden",
          "**indem** (§20) indica el modo («de qué manera») y se traduce con gerundio; verbo al "
          "final, en pasiva (§3): *abgelegt werden*. «El sistema operativo debe guardar el estado del "
          "proceso Q, almacenando todos los elementos mencionados en el bloque de control de "
          "proceso»."),
        G("infzu", "an der Reihe ist, ausgeführt zu werden",
          "**Infinitivo pasivo con zu** (§15, §3): *ausgeführt zu werden* = «ser ejecutado»; *an der "
          "Reihe sein* = «tocarle a uno». «En cuanto al proceso Q le vuelva a tocar ser "
          "ejecutado»."),
        G("orden", "Die anderen Elemente … teilt er sich mit …",
          "**Orden de palabras** (§17): la oración empieza por el complemento directo (*Die anderen "
          "Elemente eines Prozesses – Programmcode, … –*) y el sujeto *er* (el hilo) va detrás del "
          "verbo. *sich (D) etwas teilen mit* = «compartir algo con»: «los demás elementos de un "
          "proceso… los comparte con los otros hilos del mismo proceso»."),
    ],
    10: [
        G("infzu", "ist es ökonomischer, … statt zwischen Prozessen zu vollziehen",
          "**es + adjetivo + infinitivo con zu** (§16, §15): *es ist ökonomischer, … zu vollziehen* "
          "= «es más económico (eficiente) realizar…». Dentro, *statt* = «en lugar de» compara "
          "*zwischen Threads* con *zwischen Prozessen*: «es más eficiente hacer el cambio de "
          "contexto entre hilos que entre procesos»."),
        G("rel", "…, mit Hilfe dessen …",
          "**Relativo en genitivo** (§14): *dessen* es masculino/neutro porque se refiere a "
          "*OpenMP* (neutro). *mit Hilfe dessen* = «con ayuda del cual» (compara con *mit deren "
          "Hilfe*, femenino, en la p. 1): «aquí entra en juego OpenMP, con el que se puede "
          "especificar la ejecución en paralelo del código por distintos hilos»."),
        G("orden", "Um diese … Details … muss er sich nicht kümmern",
          "**Orden de palabras** (§17): el complemento con preposición del verbo *sich kümmern um* "
          "(«ocuparse de») va delante: *Um diese und viele weitere Details …*; el sujeto *er* (el "
          "programador) va detrás del verbo: «de estos y muchos otros detalles, como iniciar y "
          "terminar hilos, no tiene que ocuparse»."),
        G("rel", "die Faustregel, wonach sich …",
          "**Adverbio relativo** (§14): *wonach* (= *nach der*) = «según la cual», con el verbo al "
          "final (*verdoppelt*): «la regla empírica según la cual el número de transistores de un "
          "procesador corriente se duplica cada dieciocho meses»."),
        G("formula", "„Moore’sches Gesetz“",
          "**Adjetivo de nombre propio** (§21): nombre + *-sch* + terminación de adjetivo: *das "
          "Moore’sche Gesetz*, *nach dem Amdahl’schen Gesetz*. Con apóstrofo se escribe con "
          "mayúscula; sin él, con minúscula (*mooresche*). En español: «la ley de Moore»."),
        G("part", "die mit der Erhöhung … einhergehende Leistungssteigerung",
          "**Atributo participial** (§1) con el participio I de *einhergehen mit* («ir acompañado "
          "de»): «el aumento de rendimiento que acompaña al incremento del número de transistores». "
          "La oración está en pasiva (§3): esa mejora *wird … nicht mehr durch … erzielt* = «ya no "
          "se logra mediante…»."),
        G("konj1", "bis eine Grenze erreicht sei",
          "**Subjuntivo I** (§9) en estilo indirecto: está en una nota al pie que cuenta la "
          "predicción de Moore, y *sei* (de *sein*) marca que es lo que dijo él. *erreicht sei* es "
          "una pasiva de estado (§5): «hasta que se alcanzara un límite»."),
    ],
    11: [
        G("korr", "konnte man darauf vertrauen, dass …",
          "**Correlato** (§13): *vertrauen auf* («confiar en») + oración → *darauf …, dass* = "
          "«confiar en que»: «en el pasado se podía confiar en que los programas secuenciales se "
          "ejecutarían cada vez más rápido sin modificarlos»."),
        G("infzu", "Um … auszunutzen, ist es … notwendig geworden, … anzupassen",
          "Tres construcciones (§15): *Um … auszunutzen* = «para aprovechar» (oración final); *ist "
          "… notwendig geworden* = perfecto de *werden* («se ha vuelto necesario»); y *es* anuncia "
          "los infinitivos *anzupassen und … zu parallelisieren* (en los separables, *zu* dentro: "
          "*an·zu·passen*). «Para aprovechar la potencia de cálculo…, se ha vuelto necesario "
          "adaptar los programas a estas condiciones y paralelizarlos»."),
        G("trenn", "stellt damit eine attraktive Möglichkeit … dar",
          "**Verbo separable** (§12): *stellt … dar* = *darstellen*, que aquí no es «representar» "
          "sino «suponer, constituir». El prefijo *dar* está al final de una oración larga: «y "
          "constituye así una opción atractiva para programar aplicaciones para chips "
          "multinúcleo»."),
        G("part", "eine der … von Michael J. Flynn vorgeschlagenen Kategorien",
          "**Atributo participial** (§1) con participio II y agente con *von*: «una de las "
          "categorías propuestas en 1972 por Michael J. Flynn». *eine der …* = «una de las…» "
          "(genitivo plural)."),
        G("conj", "weder auf der Daten- noch auf der Anweisungsebene",
          "**weder … noch** (§20) = «ni … ni», combinado con **guion de ahorro** (§19): *Daten-* = "
          "*Datenebene*: «ordenadores secuenciales que no trabajan en paralelo ni a nivel de datos "
          "ni a nivel de instrucciones»."),
    ],
    12: [
        G("fvg", "… Verwendung gefunden hat",
          "**Verbo funcional** (§11): *Verwendung finden* = *verwendet werden* («usarse»), aquí en "
          "perfecto (*hat … gefunden*): «un concepto más bien teórico que hasta ahora no se ha usado "
          "en la fabricación en serie de hardware»."),
        G("part", "voneinander unabhängig … arbeitenden Prozessoren",
          "**Atributo participial largo** (§1) con participio I (*arbeitend*): *Systeme aus "
          "mehreren, voneinander unabhängig auf verschiedenen Daten arbeitenden Prozessoren* = "
          "«sistemas formados por varios procesadores que trabajan independientemente unos de otros "
          "sobre datos distintos»."),
        G("formula", "Jene mit … und jene mit … · In letzterem Fall",
          "**Palabras de referencia** (§21): *jene* = «aquellas» (aquí, las subclases); *letzterer* "
          "= «el último mencionado»: *in letzterem Fall* = «en este último caso» (el de la memoria "
          "compartida)."),
        G("konj1", "Es sei noch angemerkt, dass …",
          "**Subjuntivo I** (§9) en una fórmula impersonal académica: *es sei angemerkt* = «cabe "
          "señalar, hay que añadir». Aquí no es estilo indirecto: «cabe señalar además que en una "
          "aplicación pueden combinarse distintos niveles de paralelismo»."),
        G("zustand", "… kombiniert sein können",
          "**Pasiva de estado con modal** (§5): *kombiniert sein können* = «pueden estar "
          "combinados». Con *werden* sería la acción: *kombiniert werden können* = «pueden "
          "combinarse»."),
    ],
    13: [
        G("konj2", "… könnten auf einem Cluster verteilt ausgeführt werden",
          "**Subjuntivo II** (§10) de posibilidad: *könnten* = «podrían», con una **pasiva** (§3): "
          "*ausgeführt werden* = «ejecutarse»; *verteilt* = «de forma distribuida»: «otras "
          "instancias del programa podrían ejecutarse repartidas en un clúster»."),
        G("orden", "Bleibt die Frage, welchen Laufzeitvorteil …",
          "**Verbo al principio** (§17) en lugar de *Es bleibt die Frage*: en los textos se omite el "
          "*es* y el sujeto (*die Frage*) va detrás. Sigue una pregunta indirecta con el verbo al "
          "final (*erzielen kann*): «queda la pregunta de qué ventaja en tiempo de ejecución se "
          "puede lograr…»."),
        G("trenn", "zieht man die beiden Kenngrößen … heran",
          "**Verbo separable** (§12): *zieht … heran* = *heranziehen* («recurrir a, utilizar»): "
          "«para comparar programas seriales y paralelos se recurre a dos indicadores: la "
          "aceleración y la eficiencia»."),
        G("korr", "sagt … noch nichts darüber aus, wie gut …",
          "**Correlato** (§13) con un verbo separable (§12): *aussagen über* («decir sobre») → "
          "*darüber …, wie gut …*, y *sagt … aus* está separado: «la aceleración sola no dice nada "
          "sobre lo bien que se aprovechan los procesadores adicionales»."),
        G("konj2", "dessen … Ausführung … ein Viertel so lange dauert wie …, käme …",
          "Frase hipotética con tres piezas: el **relativo en genitivo** *dessen* (§14) = «cuya»; la "
          "comparación *so lange wie* («tanto tiempo como»); y el **subjuntivo II** *käme* (§10, de "
          "*kommen*) = «llegaría a». «Un algoritmo cuya ejecución paralela en seis procesadores "
          "durara solo la cuarta parte que la secuencial llegaría a una aceleración de 4»."),
    ],
    14: [
        G("konj2", "betrüge · ausnutzte · wäre · hätte",
          "**Subjuntivo II** (§10) en ejemplos hipotéticos: *betrüge* (de *betragen*, forma propia "
          "con Umlaut) = «sería / ascendería a»; *ausnutzte* (verbo débil: igual que el Präteritum) "
          "= «aprovechara»; *wäre* = «fuera»; *hätte* = «tendría». «La eficiencia sería solo…»; «un "
          "algoritmo ideal… tendría eficiencia 1»."),
        G("rel", "…, der … ausnutzte und dessen Beschleunigung … wäre",
          "**Dos relativas coordinadas** (§14) sobre el mismo sustantivo (*Algorithmus*): *der* "
          "(nominativo: «que») y *dessen* (genitivo: «cuya»): «un algoritmo paralelo ideal, que "
          "aprovechara por completo los procesadores adicionales y cuya aceleración fuera lineal…, "
          "tendría eficiencia 1»."),
        G("rel", "…, was die Speicherzugriffszeiten reduziert",
          "**was relativo** (§14) referido a toda la oración anterior = «lo cual»: «…de modo que se "
          "pueden mantener más datos en la caché, lo cual reduce los tiempos de acceso a memoria»."),
        G("korr", "können davon profitieren, dass …",
          "**Correlato** (§13): *profitieren von* + oración → *davon …, dass* = «beneficiarse de "
          "que»: «los hilos pueden beneficiarse de que otros hilos ya hayan cargado datos en la "
          "caché»."),
        G("part", "der von Multiprozessorarchitekturen benötigte Mehraufwand",
          "**Atributo participial** (§1) con participio II y agente con *von*: «el trabajo adicional "
          "que necesitan las arquitecturas multiprocesador». Es el sujeto de *beschränkt … nach "
          "oben* («limita superiormente»)."),
        G("konj1", "Darüber hinaus sei dieser Mehraufwand … · nur möglich sei",
          "**Subjuntivo I en estilo indirecto** (§9): *sei* en lugar de *ist* indica que es la "
          "opinión de Amdahl, no una afirmación de los autores: «además, (según Amdahl) este trabajo "
          "adicional sería por principio de naturaleza secuencial…»; «un aumento del rendimiento "
          "solo sería posible si…»."),
        G("part", "Das nach ihm benannte Amdahl’sche Gesetz",
          "**Atributo participial** (§1): *nach ihm benannt* = «que lleva su nombre» (*benennen "
          "nach* = «dar nombre según»): «la ley de Amdahl, bautizada con su nombre, limita…»."),
        G("errata", "läßt · schloß (p. 18) · Kontrollfluß",
          "**Ortografía antigua** (§22): antes de 1996 se escribía *ß* también tras vocal breve. "
          "Hoy: *lässt, schloss, Kontrollfluss*. Tras vocal larga o diptongo sigue siendo *ß* "
          "(*groß, heißen*)."),
    ],
    15: [
        G("part", "durch die im Code verbleibenden seriellen Anteile",
          "**Atributo participial** (§1) con participio I (*verbleibend*, de *verbleiben* = "
          "quedar): «por las partes seriales que quedan en el código». Completa la frase de la p. "
          "14: la ley limita la aceleración posible *durch* («por») esas partes."),
        G("konj1", "Sei σ der … Anteil",
          "**Subjuntivo I en una definición** (§9): *Sei* al principio = «Sea», la forma habitual de "
          "introducir una variable en matemáticas: «sea σ la fracción (invariable) de los cálculos "
          "seriales en el código»."),
        G("part", "Die serielle auf 1 normierte Ausführungszeit",
          "**Atributo participial** (§1): entre *Die serielle* y *Ausführungszeit* va *auf 1 "
          "normierte* («normalizada a 1»): «el tiempo de ejecución serial, normalizado a 1, se puede "
          "describir como la suma…»."),
        G("nomin", "unter Vernachlässigung des …",
          "**Estilo nominal** (§18): *unter* + sustantivo en *-ung* + genitivo = «sin tener en "
          "cuenta» (literalmente «bajo desprecio de»): «(despreciando el trabajo adicional de la "
          "paralelización)»."),
        G("v1", "Werden beispielsweise 10 % … ausgeführt, … besagt …",
          "**Condicional sin «wenn» en pasiva** (§8, §3): *Werden … ausgeführt* = *Wenn … ausgeführt "
          "werden*; la principal empieza por el verbo (*besagt*): «si, por ejemplo, el 10 % de un "
          "programa se ejecuta secuencialmente, la ley de Amdahl dice que la aceleración máxima es "
          "10»."),
        G("trenn", "Abbildung 1.1 zeigt … an",
          "**Verbo separable** (§12): *zeigt … an* = *anzeigen* («mostrar, indicar»); el prefijo "
          "*an* llega unas 25 palabras después, al final de la oración: «la figura 1.1 muestra la "
          "aceleración máxima… en función de distintas fracciones de código secuencial σ»."),
    ],
    16: [
        G("part", "mit zunehmender Anzahl verwendeter Prozessoren",
          "Dos cosas. **Participio I como adjetivo** (§1): *zunehmend* («creciente»). Y un "
          "**genitivo sin artículo**: *verwendeter Prozessoren* («de procesadores usados»), donde la "
          "terminación *-er* del adjetivo marca el genitivo plural: «con un número creciente de "
          "procesadores usados»."),
        G("fvg", "bringt … eine grundlegende Skepsis … zum Ausdruck",
          "**Verbo funcional** (§11): *zum Ausdruck bringen* = *ausdrücken* («expresar»): «la ley de "
          "Amdahl expresa, pues, un escepticismo de fondo frente a las posibilidades de los sistemas "
          "paralelos»."),
        G("part", "mit wachsender zur Verfügung stehender Rechenleistung",
          "**Dos participios I seguidos** (§1) delante de *Rechenleistung*: *wachsender* "
          "(«creciente») y *zur Verfügung stehender* («disponible»): «con una potencia de cálculo "
          "disponible cada vez mayor, también crecen las tareas que hay que resolver»."),
        G("gerund", "die zu lösenden Aufgaben",
          "**Gerundivo** (§2): *zu* + participio I (*lösend*): «las tareas que hay que resolver»."),
        G("lassen", "lässt man ein Problem … lösen",
          "**lassen + infinitivo sin sich** (§6) = «hacer que algo se haga»: «solo con fines de "
          "investigación se hace resolver un problema de tamaño dado con distinto número de "
          "procesadores». No confundir con *sich lassen* (= «se puede»)."),
        G("konj2", "würde man stattdessen … versuchen, … zu lösen",
          "**Subjuntivo II con würde** (§10) + **infinitivo con zu** (§15): *würde … versuchen* = "
          "«intentaría»: «en aplicaciones reales, en cambio, se intentaría resolver un problema "
          "mayor con más procesadores»."),
    ],
    17: [
        G("trenn", "stellten … fest, dass …",
          "**Verbo separable** (§12) *feststellen* («constatar»): el prefijo *fest* llega tras un "
          "complemento largo (*bei Experimenten mit einem System mit 1024 Prozessoren*): «Gustafson "
          "y sus colegas constataron en 1988 que…»."),
        G("fvg", "im Widerspruch zu den Vorhersagen … standen",
          "**Verbo funcional** (§11): *im Widerspruch stehen zu* = *widersprechen* («contradecir»): "
          "«…que las aceleraciones medidas contradecían las predicciones de la ley de Amdahl»."),
        G("trenn", "Wie man sieht, fällt die Kurve sehr steil ab",
          "**Verbo separable** (§12) *abfallen* («caer, bajar»); *Wie man sieht* = «como se ve»: "
          "«como se ve, la curva cae muy bruscamente»."),
        G("konj2", "wären überhaupt in der Lage … · betrüge … nur 24",
          "**Subjuntivo II** (§10) para las consecuencias hipotéticas de la ley de Amdahl: *wären … "
          "in der Lage* = «serían capaces» (*in der Lage sein* = «ser capaz», §11); *betrüge* = "
          "«sería»: «pocos programas serían siquiera capaces de superar una aceleración de 100»."),
    ],
    18: [
        G("konj1", "…, 1 − σ sei konstant …, zurückzuweisen sei",
          "**Estilo indirecto con subjuntivo I** (§9): todo el párrafo cuenta lo que concluyó "
          "Gustafson, y cada *sei* marca «según él»: «Gustafson concluyó que había que rechazar la "
          "suposición de que 1 − σ es constante e independiente de n»."),
        G("seinzu", "zurückzuweisen sei · als konstant anzunehmen",
          "**sein + zu + infinitivo** (§7) = «hay que», aquí en subjuntivo I (*sei*). Separables con "
          "*zu* dentro: *zurück·zu·weisen* («rechazar»), *an·zu·nehmen* («suponer»): «había que "
          "rechazar…»; «más bien había que suponer constante el tiempo de ejecución, y no el tamaño "
          "del problema»."),
        G("konj2", "hätten … könnten … wären … bliebe",
          "**Subjuntivo II como sustituto del I** (§10): en plural el subjuntivo I coincidiría con "
          "el indicativo (*sie haben*), así que se usa *hätten, könnten, wären*. Sigue siendo estilo "
          "indirecto: «ya que los usuarios tendrían control… y podrían elegir los parámetros de modo "
          "que los cálculos terminaran dentro de una ventana de tiempo dada»."),
        G("v1", "Verdoppele man …, verdoppele man auch …",
          "**Condicional sin «wenn»** (§8) en subjuntivo I con *man* (estilo indirecto): "
          "*Verdoppele man* = *Wenn man … verdoppelt*: «si se duplica el número de grados de "
          "libertad de una simulación física, se duplica también el número de procesadores»."),
        G("konj1", "Sei mit t_{p} und t_{s} die … verbrachte Laufzeit bezeichnet",
          "**Definición con subjuntivo I + pasiva** (§9, §3): *Sei … bezeichnet* = «sea designado». "
          "En medio hay un atributo participial (§1): *die mit paralleler bzw. serieller Berechnung "
          "verbrachte Laufzeit* = «el tiempo empleado en cálculo paralelo o serial». «Designemos con "
          "t_{p} y t_{s} el tiempo empleado en cálculo paralelo y serial, respectivamente»."),
        G("trenn", "nähert sich die Beschleunigung … an",
          "**Verbo separable** (§12) *sich annähern* + dativo («aproximarse a»): ¡el prefijo *an* "
          "está en la página siguiente (p. 19)!: «la aceleración se aproxima al número de "
          "procesadores usados en paralelo»."),
    ],
    19: [
        G("formula", "fallen bedeutend positiver aus",
          "**ausfallen + adjetivo** (§21) = «resultar»: *positiver ausfallen* = «resultar más "
          "positivo»; *bedeutend* = «considerablemente»: «las predicciones de la ley de Gustafson "
          "resultan considerablemente más positivas»."),
        G("infzu", "Statt wie im Falle des … Gesetzes … zu konvergieren, …",
          "**statt … zu + infinitivo** (§15) = «en lugar de + infinitivo»; *wie im Falle des "
          "Amdahl’schen Gesetzes* = «como en el caso de la ley de Amdahl»: «en lugar de converger "
          "muy rápido hacia 1 (como ocurre con Amdahl), la aceleración máxima baja muy despacio»."),
        G("errata", "Für ein 1024-Prozessor-System und einem seriellen Anteil",
          "**Errata del libro** (§22): *für* rige siempre acusativo, así que debería ser *einen "
          "seriellen Anteil* (o bien *bei einem seriellen Anteil*). Idea: «para un sistema de 1024 "
          "procesadores y una fracción serial del 4 %, la aceleración prevista es 983»."),
    ],
    20: [
        G("konj1", "dass beide Gesetze … äquivalent seien",
          "**Subjuntivo I en estilo indirecto** (§9): *seien* (plural de *sei*) marca que es la tesis "
          "de Yuan Shi: «Yuan Shi sostiene que ambas leyes serían, en el fondo, matemáticamente "
          "equivalentes»."),
        G("formula", "was die Definition … angeht",
          "**Fórmula** (§21): *was X angeht* = «en lo que respecta a X»: «(sobre todo en lo que "
          "respecta a la definición de la “fracción secuencial”)»."),
        G("lassen", "Es lassen sich Anwendungen finden, für die …",
          "**sich lassen + infinitivo** (§6) con **es de relleno** (§16): el sujeto real es "
          "*Anwendungen* (plural), por eso *lassen*: «se pueden encontrar aplicaciones para las que "
          "se cumple la ley de Amdahl y que no escalan»."),
        G("conj", "einerseits … (p. 21) andererseits",
          "**Conector doble** (§20): *einerseits … andererseits* = «por un lado … por otro». La "
          "primera parte está al final de la p. 20 y la segunda al principio de la p. 21."),
    ],
    21: [
        G("korr", "sich … darüber Gedanken zu machen, ob denn …",
          "**Correlato** (§13) con *sich Gedanken machen über* («reflexionar sobre») → *darüber …, "
          "ob* = «reflexionar sobre si…». La partícula *denn* en la pregunta indirecta añade duda "
          "(«realmente»): «es imprescindible pensar, antes de paralelizar, si una versión paralela "
          "puede realmente escalar»."),
        G("lassen", "lässt sich … oft erst im Betrieb feststellen",
          "**sich lassen + infinitivo** (§6) = «se puede»; *erst* = «no antes de, solo»: «el "
          "rendimiento realmente alcanzado a menudo solo se puede determinar y optimizar en "
          "funcionamiento»."),
        G("errata", "die tatsächliche erreichte Leistung",
          "**Probable errata** (§22): lo esperable es *die tatsächlich erreichte Leistung*, con "
          "*tatsächlich* como adverbio (sin terminación) que modifica al participio *erreichte*: «el "
          "rendimiento realmente alcanzado». Con terminación (*tatsächliche*) serían dos adjetivos "
          "sobre *Leistung*."),
    ],
}

# ================================================================ DE QUÉ HABLA CADA PÁRRAFO
# Resumen PROPIO de cada párrafo (no traduce el texto); se localiza por sus primeras palabras.
# «(sigue de la p. …)» = párrafo que empezó en la página anterior.
PARRAFOS = {
    "V": [
        ("Seit der Einführung …",
         "Punto de partida: desde el *hyperthreading* de Intel (2002) y los procesadores de doble y "
         "cuádruple núcleo, también un PC normal ejecuta varios hilos a la vez. Para aprovecharlo hay "
         "que paralelizar las aplicaciones; se define qué significa paralelizar y se anuncian dos "
         "problemas del diseño de procesadores que obligan a todo programador a aprender programación "
         "paralela."),
        ("Alle 18 Monate …",
         "Primer problema: los transistores se duplican cada 18 meses, pero las herramientas de diseño "
         "mejoran mucho más despacio; los diseñadores no saben aprovechar con sentido tantos "
         "componentes, así que la salida «fácil» es copiar unidades enteras. Sigue en la p. VI."),
    ],
    "VI": [
        ("(sigue de la p. V)", "Por eso se copian CPU completas, como se ve en los procesadores actuales."),
        ("Zweitens …",
         "Segundo problema: con un consumo eléctrico máximo fijo cada vez cuesta más acelerar un solo "
         "hilo, porque con frecuencias más altas y transistores más pequeños crecen las corrientes de "
         "fuga. También esto empuja a la industria hacia los procesadores paralelos."),
        ("Für Informatiker …",
         "Conclusión: aprender programación paralela es imprescindible, y OpenMP permite hacerlo de "
         "forma sencilla. Objetivo del libro: presentar OpenMP desde el punto de vista del programador "
         "de C/C++, teniendo en cuenta el borrador de la versión 3.0."),
        ("Jedes Buch …",
         "Agradecimientos: a quienes corrigieron el texto, a la editorial Springer y a quien dio apoyo "
         "técnico en la maquetación."),
        ("Wir wünschen …",
         "Despedida: los autores desean éxito y ahorro de tiempo a los lectores. Firma: Múnich y "
         "Augsburgo, febrero de 2008."),
    ],
    1: [
        ("OpenMP ist eine …",
         "Qué es OpenMP: una interfaz para indicar paralelismo en C, C++ y Fortran. Su gran ventaja es "
         "que apenas cambia el código secuencial original (a menudo basta con añadir unas pocas "
         "instrucciones para el compilador): el código sigue siendo legible y es de las formas más "
         "rápidas de paralelizar."),
        ("OpenMP setzt sich …",
         "De qué consta: directivas de compilador, funciones de biblioteca y variables de entorno. Su "
         "objetivo es un modelo de programación portable para máquinas de memoria compartida; las "
         "directivas sirven para repartir el trabajo entre hilos y sincronizarlos. Sigue en la p. 2."),
    ],
    2: [
        ("(sigue de la p. 1)",
         "Las directivas también regulan si los hilos acceden a los datos de forma compartida o "
         "separada; la biblioteca y las variables de entorno controlan el entorno de ejecución. Los "
         "compiladores suelen tener una opción para activar o desactivar OpenMP."),
        ("Wie das „Open“ …",
         "OpenMP es un estándar abierto («MP» = *multi processing*). Se remite a la web oficial, "
         "donde se descarga la especificación (que, según los autores, se lee bien), y a la web de la "
         "comunidad de usuarios."),
        ("Das folgende minimale …",
         "Empieza el apartado 1.1: un primer ejemplo mínimo en C++, un vector de enteros que varios "
         "hilos inicializan en paralelo (código de 5 líneas)."),
        ("In den beiden ersten …",
         "Explicación del ejemplo: definición del vector, la directiva `#pragma omp parallel for` y "
         "el cuerpo del bucle. Sigue en la p. 3."),
    ],
    3: [
        ("(sigue de la p. 2)",
         "La directiva hace que varios hilos ejecuten el bucle; lo que se paraleliza es la asignación "
         "de cada índice a su elemento. Sin entrar aún en detalles (cuántos hilos, qué hilo hace qué), "
         "el ejemplo muestra varias propiedades:"),
        ("• OpenMP bietet …",
         "Alto nivel de abstracción: el programador no crea ni termina hilos; el código paralelo queda "
         "en su sitio (no en una función aparte, como con Pthreads) y el reparto de índices es "
         "automático, aunque se puede controlar."),
        ("• Die ursprüngliche …",
         "Se conserva la estructura secuencial: un compilador sin OpenMP ignora los pragmas o avisa, "
         "pero compila igual."),
        ("• Aus der obigen …",
         "Consecuencia: se puede paralelizar paso a paso y el código siempre funciona; para comprobar "
         "que es correcto basta con desactivar la opción y comparar con la versión serial. Sigue en la "
         "p. 4."),
    ],
    4: [
        ("(sigue de la p. 3)", "Sin la opción se obtiene una versión serial con la que comparar."),
        ("• Parallelisierungen …", "Las paralelizaciones son locales: a menudo basta con un cambio pequeño."),
        ("• Mit OpenMP …",
         "Permite optimizar el rendimiento «en el último minuto», sin rediseñar la aplicación."),
        ("• OpenMP ist portierbar …",
         "Es portable y lo apoyan casi todos los grandes fabricantes de hardware."),
        ("• OpenMP ist ein offener …",
         "Es un estándar abierto e independiente del fabricante, que existe desde 1997 (versión 2.5; "
         "la 3.0 era inminente). Hay compiladores de varios fabricantes y, aunque difieren en "
         "detalles, todos procesan código OpenMP correcto."),
        ("OpenMP ist einfach …",
         "Uso básico: las directivas (pragmas) le dicen al compilador qué paralelizar; todas empiezan "
         "por `#pragma omp` y los compiladores sin OpenMP las ignoran. Se da su forma general."),
        ("Klauseln sind optional …",
         "Las cláusulas son opcionales y modifican la directiva; cada directiva admite su propio "
         "conjunto de cláusulas (a veces ninguna)."),
    ],
    5: [
        ("Alle Anweisungen …",
         "Detalle de sintaxis: la línea del pragma tiene que terminar con un salto de línea, así que "
         "la llave de apertura no puede ir en esa misma línea (ejemplo correcto e incorrecto)."),
        ("Die Funktionen der …",
         "La biblioteca de tiempo de ejecución sirve para consultar y fijar parámetros y para "
         "sincronizar hilos, y exige incluir `omp.h`. En teoría no hace falta si solo se usan pragmas, "
         "pero algún compilador lo necesita, así que se recomienda incluirlo siempre."),
        ("Sollte ein Compiler …",
         "Si el compilador no soporta OpenMP, tampoco conoce `omp.h`. Solución: `_OPENMP` está "
         "definida cuando OpenMP está activo (su valor es la fecha de la especificación) y permite "
         "incluir o excluir código con `#ifdef`. Sigue en la p. 6 con un ejemplo."),
    ],
    6: [
        ("(sigue de la p. 5)", "Ejemplo: incluir `omp.h` solo si `_OPENMP` está definida."),
        ("Folgende C/C++-Compiler …",
         "Empieza el apartado 1.1.1: lista (no exhaustiva) de compiladores compatibles con OpenMP."),
        ("• Visual Studio …",
         "Visual Studio 2005 y 2008 (no la edición Express): se activa en las propiedades del "
         "proyecto; equivale a la opción `/openmp`."),
        ("• Intels C++-Compiler …",
         "El compilador de Intel (desde la versión 8) implementa el estándar y directivas propias; "
         "gratis para uso no comercial en Linux y en versión de prueba en Windows y Mac."),
        ("• GCC unterstützt …", "GCC lo soporta desde la versión 4.2, con la opción `-fopenmp`."),
        ("• Sun Studio …", "Sun Studio (Solaris) también implementa OpenMP 2.5."),
    ],
    7: [
        ("Werden die o. g. …",
         "Al activar esas opciones también se define `_OPENMP`; para ejecutar un programa en serie "
         "(para depurar o medir tiempos) basta con recompilarlo sin la opción."),
        ("Dieses Buch betrachtet …",
         "«Sobre este libro»: OpenMP desde el punto de vista de C/C++ (se suponen conocimientos de "
         "estos lenguajes); Fortran no se trata."),
        ("Zum Zeitpunkt der …",
         "Estado de la norma al escribir el libro: versión 2.5 (2005) y un borrador recién publicado de "
         "la 3.0, con novedades que algunos compiladores ya ofrecían (por ejemplo, tareas en el de "
         "Intel). El libro ya las incluye (cap. 6.2)."),
        ("Der verbleibende Teil …",
         "Empieza el apartado 1.2: el resto del capítulo da una visión general de la programación "
         "paralela (procesos e hilos, multinúcleo, medición del rendimiento). Sigue en la p. 8."),
    ],
    8: [
        ("(sigue de la p. 7)",
         "Quien ya conozca estos temas puede saltar al capítulo 3; para más detalle se recomienda "
         "otro libro de la misma colección."),
        ("Als Prozess …",
         "Apartado 1.2.1: qué es un proceso (un programa en ejecución, a diferencia del código guardado "
         "en disco) y qué es la multitarea; en máquinas de una sola CPU la simultaneidad es aparente, "
         "porque cada proceso se ejecuta a ratos muy cortos. El planificador decide cuándo y dónde se "
         "ejecuta cada uno."),
        ("Ein Prozess setzt sich …",
         "Lista de lo que forma un proceso: identificador, código, contador de programa, registros, "
         "pila… Sigue en la p. 9."),
    ],
    9: [
        ("(sigue de la p. 8)", "…segmento de datos (variables globales) y montículo (variables dinámicas)."),
        ("Unterschiedliche …",
         "Cada sistema operativo crea procesos a su manera: `fork()` en UNIX, `CreateProcess()` en "
         "Win32."),
        ("Entscheidet der Scheduler …",
         "El cambio de contexto: para ejecutar otro proceso, el sistema guarda el estado del actual en "
         "el bloque de control de proceso y lo restaura cuando le vuelve a tocar."),
        ("In modernen …",
         "Los hilos, versión «ligera» de los procesos: cada uno tiene identificador, contador, "
         "registros y pila propios, pero comparte código, datos, montículo y archivos. Ventajas: varias "
         "tareas a la vez (interfaces más ágiles) y acceso común a los recursos. Sigue en la p. 10."),
    ],
    10: [
        ("(sigue de la p. 9)",
         "Más ventajas: el cambio de contexto entre hilos es más barato y, con varios procesadores, los "
         "hilos corren de verdad en paralelo. Ejemplos de bibliotecas: Pthreads y Win32."),
        ("Hier kommt nun OpenMP …",
         "Papel de OpenMP: permite indicar qué ejecutan en paralelo los hilos sin preocuparse del "
         "modelo de hilos del compilador ni de crearlos o terminarlos. En OpenMP, un hilo es un flujo "
         "de control que ejecuta, junto con otros, una sección de código marcada."),
        ("Als „Moore’sches Gesetz“ …",
         "Apartado 1.2.2: la ley de Moore (los transistores de un procesador se duplican cada 18 "
         "meses), de 1965 y todavía vigente (nota al pie: en 2007 Moore le daba 10–15 años más). "
         "Últimamente el rendimiento ya no crece subiendo la frecuencia de reloj… Sigue en la p. 11."),
    ],
    11: [
        ("(sigue de la p. 10)",
         "…sino con más paralelismo dentro del procesador: *hyperthreading* (varios flujos de control "
         "en un núcleo) y procesadores multinúcleo."),
        ("In der Vergangenheit …",
         "Antes, los programas secuenciales se aceleraban solos con cada nueva generación de "
         "procesadores; ya no. Para aprovechar los chips multinúcleo hay que paralelizar, así que la "
         "programación paralela se vuelve una herramienta básica, y OpenMP permite hacerlo poco a "
         "poco."),
        ("Allgemein lassen sich …",
         "La clasificación de Flynn (1972), según el número de flujos de instrucciones y de datos. "
         "Empieza la lista:"),
        ("• Single Instruction, Single Data …", "SISD: ordenadores secuenciales, como el PC clásico."),
        ("• Single Instruction, Multiple Data …",
         "SIMD: una instrucción sobre muchos datos a la vez. Sigue en la p. 12 con ejemplos."),
    ],
    12: [
        ("(sigue de la p. 11)",
         "Ejemplos de SIMD: las GPU y las instrucciones SIMD de los procesadores (MMX de Intel, 3DNow! "
         "de AMD, la familia SSE)."),
        ("• Multiple Instruction, Single Data …",
         "MISD: concepto casi solo teórico, sin uso en el hardware de serie."),
        ("• Multiple Instruction, Multiple Data …",
         "MIMD: varios procesadores independientes sobre datos distintos (clústeres y procesadores "
         "multinúcleo). Se dividen en memoria distribuida y memoria compartida (SMP); programar "
         "máquinas de memoria compartida es el terreno de OpenMP."),
        ("Es sei noch angemerkt …",
         "Los niveles de paralelismo se pueden combinar: OpenMP en una máquina de memoria compartida, "
         "SIMD (SSE) dentro de cada procesador… Sigue en la p. 13."),
    ],
    13: [
        ("(sigue de la p. 12)",
         "…y, además, el programa puede formar parte de un sistema distribuido en un clúster."),
        ("Bleibt die Frage …",
         "Apartado 1.2.3: ¿cuánto se gana al paralelizar, descontando el trabajo de gestionar los "
         "hilos? Se usan dos indicadores: aceleración y eficiencia."),
        ("Die Beschleunigung s_{n} …",
         "Definición de la aceleración: tiempo en un procesador dividido por el tiempo en n "
         "procesadores."),
        ("Die Beschleunigung alleine …",
         "La aceleración no dice cómo se aprovechan los procesadores; para eso está la eficiencia "
         "(aceleración dividida por el número de procesadores). Ejemplo con seis procesadores. Sigue "
         "en la p. 14."),
    ],
    14: [
        ("(sigue de la p. 13)",
         "En el ejemplo la eficiencia es baja; un algoritmo ideal, con aceleración lineal, tendría "
         "eficiencia 1."),
        ("Dennoch stellt …",
         "La aceleración puede incluso superar n (aceleración superlineal) gracias a la caché: con más "
         "procesadores hay más caché en total y los hilos aprovechan datos que otros ya cargaron."),
        ("Bereits im Jahre 1967 …",
         "Apartado 1.2.4: la tesis de Amdahl (1967): el trabajo de gestión en los multiprocesadores "
         "limita la aceleración y es, por naturaleza, secuencial; por eso el rendimiento paralelo solo "
         "crecería si también crece el secuencial."),
        ("Das nach ihm benannte …",
         "La ley de Amdahl limita la aceleración según la parte serial que queda en el código. Sigue en "
         "la p. 15 con la fórmula."),
    ],
    15: [
        ("(sigue de la p. 14)",
         "Derivación: se normaliza el tiempo serial a 1 y se llama σ a la parte secuencial; en n "
         "procesadores solo se reparte la parte paralela. De ahí salen la aceleración máxima y su "
         "límite 1/σ, que no depende del número de procesadores."),
        ("Werden beispielsweise …",
         "Ejemplo: con un 10 % de código secuencial, la aceleración nunca pasa de 10. La figura 1.1 "
         "muestra las curvas para distintos valores de σ."),
    ],
    16: [
        ("Abb. 1.1",
         "Pie de la figura 1.1: aceleración máxima según Amdahl frente al número de procesadores, para "
         "varios σ; la diagonal es el caso ideal (σ = 0)."),
        ("Das Amdahl’sche Gesetz bringt …",
         "Apartado 1.2.5: la ley de Amdahl es escéptica, pero olvida que con más potencia de cálculo "
         "también crecen los problemas: solo en investigación se resuelve el mismo problema con "
         "distinto número de procesadores; en la práctica se resuelven problemas mayores o con más "
         "precisión. Sigue en la p. 17."),
    ],
    17: [
        ("Abb. 1.2",
         "Pie de la figura 1.2: la aceleración según Amdahl para 1024 procesadores cuando crece σ."),
        ("(sigue de la p. 16)", "…o para calcular la solución con más precisión."),
        ("John Gustafson und …",
         "Los experimentos de Gustafson (1988) con 1024 procesadores contradecían a Amdahl: según su "
         "ley, con solo un 4 % secuencial la aceleración máxima sería 24, pero en simulaciones físicas "
         "con un 4–8 % secuencial midieron… (sigue en la p. 18)."),
    ],
    18: [
        ("(sigue de la p. 17)", "…aceleraciones de unas 1020, es decir, casi lineales."),
        ("Gustafson schloß …",
         "Conclusión de Gustafson: no es realista suponer fija la parte paralela; los usuarios ajustan "
         "el problema para que termine en un tiempo dado, así que lo que se mantiene constante es el "
         "tiempo, no el tamaño del problema. La parte secuencial (carga, entrada y salida, cuellos de "
         "botella) no crece."),
        ("Gustafson drehte …",
         "Por eso invierte la pregunta: ¿cuánto tardaría el programa paralelo en un solo procesador? "
         "Con esa idea deduce su fórmula de la aceleración escalada. Sigue en la p. 19."),
    ],
    19: [
        ("(sigue de la p. 18)",
         "Si la parte secuencial se vuelve despreciable al crecer el problema, la aceleración se "
         "acerca al número de procesadores (figura 1.3)."),
        ("Die Vorhersagen …",
         "Las previsiones de Gustafson son mucho más optimistas: la aceleración máxima baja muy "
         "despacio al aumentar la parte serial (con 1024 procesadores y un 4 % serial, 983)."),
        ("Abb. 1.3", "Pie de la figura 1.3: aceleración máxima según Gustafson para varios σ."),
    ],
    20: [
        ("Abb. 1.4",
         "Pie de la figura 1.4: comparación directa de Amdahl y Gustafson para 1024 procesadores."),
        ("Und wer hat nun Recht?", "Subtítulo: «¿Y quién tiene razón?»."),
        ("Yuan Shi argumentiert …",
         "Según Yuan Shi, las dos leyes son en el fondo equivalentes: las diferencias vienen de "
         "malentendidos (sobre todo sobre qué es la «parte secuencial») y de condiciones que se pasan "
         "por alto."),
        ("In der Praxis liegt …",
         "En la práctica la verdad está en medio: hay aplicaciones que siguen a Amdahl y no escalan, y "
         "otras que escalan casi perfectamente, como dice Gustafson. Sigue en la p. 21."),
    ],
    21: [
        ("(sigue de la p. 20)",
         "Conclusión del capítulo: antes de paralelizar hay que pensar si el algoritmo puede escalar "
         "con sus partes secuenciales, pero el rendimiento real a menudo solo se ve (y se optimiza) al "
         "ejecutarlo: la arquitectura, las cachés y la memoria influyen de forma decisiva."),
    ],
}

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
ORDEN = [p for p, *_r in PAGINAS]
NUM_TIPO = {g["clave"]: n for n, g in enumerate(GRAMATICA, 1)}
VERDE = colors.HexColor("#3d6b4f")
SGX = St("gx", parent=SB, fontSize=9.6, leading=13.3, spaceAfter=3.5)


def mdl(t):
    """md() admitiendo saltos de línea («\\n» → <br/>)."""
    return md(t).replace("\n", "<br/>")


def PL(t, estilo):
    TEXTOS.append(t)
    return Paragraph(mdl(t), estilo)


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


def tabla_parrafos(pag):
    datos = [[Paragraph(f"PÁRRAFO · S. {pag}", SCAB), Paragraph("DE QUÉ HABLA", SCAB)]]
    datos += [[P(f"*{inicio}*", SV), P(resumen, SV)] for inicio, resumen in PARRAFOS[pag]]
    t = Table(datos, colWidths=[4.3 * cm, ANCHO - 4.3 * cm], repeatRows=1)
    t.setStyle(estilo_tabla([("BACKGROUND", (0, 0), (-1, 0), VERDE)]))
    return t


def tabla_vocabulario(entradas, pag):
    datos = [[Paragraph(f"VOKABELN · S. {pag}", SCAB), Paragraph("ESPAÑOL", SCAB)]]
    datos += [[celda_de(e), celda_es(e)] for e in entradas]
    t = Table(datos, colWidths=[8.6 * cm, ANCHO - 8.6 * cm], repeatRows=1)
    t.setStyle(estilo_tabla())
    return t


def tabla_gramatica(notas, pag):
    datos = [[Paragraph(f"GRAMMATIK · S. {pag} · EN EL TEXTO", SCAB),
              Paragraph("QUÉ ES Y CÓMO LEERLO, PIEZA A PIEZA", SCAB)]]
    for tipo, frag, exp in notas:
        TEXTOS.extend([frag, exp])
        n = NUM_TIPO[tipo]
        nombre = md(GRAMATICA[n - 1]["titulo"]).upper()
        datos.append([Paragraph(f'<i>{md(frag)}</i><br/><font size="7" color="#2e5e8c">'
                                f'<b>§{n} · {nombre}</b></font>', SFRAG),
                      Paragraph(mdl(exp), SEXP)])
    t = Table(datos, colWidths=[5.4 * cm, ANCHO - 5.4 * cm], repeatRows=1)
    t.setStyle(estilo_tabla([("BACKGROUND", (0, 0), (-1, 0), AZUL2)]))
    return t


def paginas_por_tipo():
    res = {}
    for pag in ORDEN:
        for tipo, *_r in NOTAS[pag]:
            res.setdefault(tipo, [])
            if pag not in res[tipo]:
                res[tipo].append(pag)
    return res


def indice_gramatica(ppt):
    datos = [[Paragraph(c, SCAB) for c in ("§", "ESTRUCTURA", "EN UNA LÍNEA", "PÁGINAS")]]
    for n, g in enumerate(GRAMATICA, 1):
        datos.append([P(f"**{n}**", SNUM), P("**" + g["titulo"] + "**", SV), P(g["resumen"], SV),
                      P(", ".join(map(str, ppt.get(g["clave"], []))), SV)])
    t = Table(datos, colWidths=[0.8 * cm, 4.7 * cm, ANCHO - 9.3 * cm, 3.8 * cm], repeatRows=1)
    t.setStyle(estilo_tabla())
    return t


def gramatica_explicada(story, ppt):
    for n, g in enumerate(GRAMATICA, 1):
        story.append(CondPageBreak(7 * cm))
        story.append(Paragraph(f'§{n} · {md(g["titulo"])} <font size="9" color="#555555">'
                               f'({md(g["aleman"])})</font>', SH2))
        for etiqueta, clave in (("Qué es", "que"), ("Cómo se forma", "forma"),
                                ("Cómo reconocerla", "reconocer"), ("Cómo traducirla", "traducir")):
            story.append(PL(f"**{etiqueta}.** {g[clave]}", SGX))
        datos = [[Paragraph("EJEMPLO", SCAB), Paragraph("TRADUCCIÓN", SCAB)]]
        datos += [[P(f"*{de}*", SV), P(es, SV)] for de, es in g["ejemplos"]]
        t = Table(datos, colWidths=[ANCHO / 2, ANCHO / 2])
        t.setStyle(estilo_tabla([("BACKGROUND", (0, 0), (-1, 0), AZUL2)]))
        story.append(t)
        paginas = ", ".join(map(str, ppt.get(g["clave"], []))) or "—"
        story.append(P(f"En el libro: pp. {paginas}", SREF))


def palabras_pequenas():
    clases = ("Adv.", "Konj.", "Präp.", "Präp./Konj.", "Abk.", "Relativadverb")
    filas = [(e[1], e[3], pag) for pag, _t, voc in PAGINAS for e in voc
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
    for pag, _t, voc in PAGINAS:
        for e in voc:
            palabra = e[2] if e[0] == "n" else e[1]
            etiqueta = f"{e[1]} {palabra}" if e[0] == "n" else palabra
            items.append((clave_orden(palabra), etiqueta, pag))
    items.sort(key=lambda x: (x[0], x[1]))
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
def portada(story, n_voc, n_gram, n_par):
    story.append(Spacer(1, 2.0 * cm))
    story.append(P("Lista de lectura", STIT))
    story.append(Spacer(1, 0.25 * cm))
    story.append(P("OpenMP · Vorwort y Kapitel 1", St(
        "t2", parent=STIT, fontSize=17, leading=22, textColor=AZUL2)))
    story.append(Spacer(1, 0.45 * cm))
    story.append(P(f"Página a página (pp. V–VI y 1–21) · {n_par} párrafos resumidos · {n_voc} "
                   f"palabras y expresiones · {n_gram} notas de gramática · {len(GRAMATICA)} "
                   f"estructuras explicadas · nivel B1−", SSUB))
    story.append(Spacer(1, 0.9 * cm))
    caja = [
        P("**Cómo usarla.** Ten la lista al lado del libro de S. Hoffmann y R. Lienhart, *OpenMP* "
          "(Springer, 2008). Tiene tres partes:", SCAJA),
        P(f"1. **Gramática explicada**: las {len(GRAMATICA)} estructuras gramaticales del texto, "
          "cada una desde cero —qué es, cómo se forma, cómo reconocerla y cómo traducirla— y con "
          "ejemplos. Léela antes de empezar, o consúltala cuando una nota no te baste.", SCAJA),
        P("2. **Página a página**: para cada página del libro, primero **de qué habla cada "
          "párrafo** (un resumen para orientarte antes de leer), después el **vocabulario** en el "
          "orden en que aparece y, por último, la **gramática en el texto**: el fragmento donde "
          "aparece cada estructura, analizado pieza a pieza, con su traducción y el número (§) de "
          "su explicación.", SCAJA),
        P("3. **Para consultar**: palabras pequeñas (conectores), internacionalismos e índice "
          "alfabético con la página donde se explica cada palabra.", SCAJA),
        P("• Cada palabra se explica solo la primera vez que aparece; el Vorwort va primero, como "
          "en el libro. Se ha dejado fuera lo que un B1− ya conoce y los internacionalismos; sí "
          "están las palabras de B1 con un sentido técnico distinto (marca **TÉC.**).", SCAJA),
        P("• Sustantivos con artículo en color (der · die · das) y plural; verbos con presente, "
          "Präteritum y Partizip II, y la preposición con su caso (+ A = acusativo, + D = dativo, "
          "+ G = genitivo).", SCAJA),
        P("• Los fragmentos del libro son citas breves, recortadas con «…»; los resúmenes de los "
          "párrafos son propios y no traducen el texto.", SCAJA),
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
    canvas.drawString(MARGEN, 1.05 * cm, "Lista de lectura · OpenMP, Vorwort y cap. 1 · nivel B1−")
    canvas.drawRightString(A4[0] - MARGEN, 1.05 * cm, f"{doc.page}")
    canvas.setStrokeColor(LINEA)
    canvas.setLineWidth(0.5)
    canvas.line(MARGEN, 1.4 * cm, A4[0] - MARGEN, 1.4 * cm)
    canvas.restoreState()


def construir():
    n_voc = sum(len(v) for _p, _t, v in PAGINAS)
    n_gram = sum(len(NOTAS[p]) for p in ORDEN)
    n_par = sum(len(PARRAFOS[p]) for p in ORDEN)
    ppt = paginas_por_tipo()
    story = []
    portada(story, n_voc, n_gram, n_par)

    story.append(PageBreak())
    story.append(P("Parte 1 · Gramática explicada", SH1))
    story.append(P(f"Las {len(GRAMATICA)} estructuras del texto, explicadas desde cero. En cada "
                   "página del libro, las notas de gramática remiten aquí con su número (§).", SREF))
    story.append(indice_gramatica(ppt))
    gramatica_explicada(story, ppt)

    story.append(PageBreak())
    story.append(P("Parte 2 · Página a página", SH1))
    story.append(P("Para cada página del libro: de qué habla cada párrafo, el vocabulario en orden "
                   "de aparición y la gramática en el texto, analizada pieza a pieza.", SREF))
    for pag, tema, voc in PAGINAS:
        story.append(CondPageBreak(5 * cm))
        story.append(Paragraph(f"Seite {pag} · página {pag}", SH2))
        story.append(P(tema, STEMA))
        story.append(tabla_parrafos(pag))
        story.append(Spacer(1, 0.18 * cm))
        story.append(tabla_vocabulario(voc, pag))
        if NOTAS[pag]:
            story.append(Spacer(1, 0.18 * cm))
            story.append(tabla_gramatica(NOTAS[pag], pag))

    story.append(PageBreak())
    tabla, n = palabras_pequenas()
    story.append(P("Parte 3 · Para consultar", SH1))
    story.append(P("Palabras pequeñas que estructuran el texto", SH2))
    story.append(P(f"Los {n} conectores, adverbios y preposiciones de la lista, en orden de "
                   "aparición: son lo que más ayuda a leer con fluidez.", SREF))
    story.append(tabla)

    story.append(CondPageBreak(7 * cm))
    story.append(P("Internacionalismos", SH2))
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
                            title="Lista de lectura: OpenMP, Vorwort y capítulo 1 (nivel B1−)",
                            author="indescifrable · material de estudio",
                            subject="Gramática explicada, resumen por párrafos, vocabulario y "
                                    "gramática página a página para leer el Vorwort y el "
                                    "capítulo 1 de OpenMP (Hoffmann/Lienhart) en alemán")
    doc.build(story, onLaterPages=pie)


def verificar():
    assert ORDEN == ["V", "VI", *range(1, 22)], "faltan páginas"
    assert set(NOTAS) == set(ORDEN) and set(PARRAFOS) == set(ORDEN), "NOTAS/PARRAFOS incompletos"
    assert len(NUM_TIPO) == len(GRAMATICA), "claves de GRAMATICA repetidas"
    for pag in ORDEN:
        assert PARRAFOS[pag], f"p. {pag} sin resumen de párrafos"
        for tipo, frag, exp in NOTAS[pag]:
            assert tipo in NUM_TIPO, f"tipo desconocido: {tipo}"
            # cada nota remite al § de su propio tipo (§1 no debe casar con §15)
            assert re.search(rf"§{NUM_TIPO[tipo]}(?!\d)", exp), f"p. {pag}: «{frag}» sin su §"
    # sin palabras repetidas: cada entrada se explica una sola vez
    vistas = {}
    for pag, _t, voc in PAGINAS:
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
