// engine/examenMazo.js
// Examen escrito sobre los mazos de «Más contenidos»: en vez de voltear la
// ficha y autocalificarse (reconocer), el alumno TECLEA la respuesta y se
// compara con la ficha (producir). Cubre justo lo que el autocalificado
// disimula: el género del sustantivo y el Partizip II del verbo.
//
// Las preguntas salen de los datos que la ficha ya trae (artículo, palabra,
// infinitivo, participio, auxiliar, significado), así que valen para los doce
// capítulos sin escribir un solo ejercicio a mano. La selección de qué se
// pregunta es la de srs.js: el examen comparte el estado SM-2 con las fichas.
//
// Módulo puro: sin DOM, React ni localStorage; `ahora` siempre inyectado.
// Extensión explícita en el import: también lo usa node.

import { crearGeneradorNormalizado } from './board.js';
import { ARTICULOS, claveTarjeta, sesionDeMazo } from './mazos.js';

/** Los cuatro tipos de pregunta, por lo que piden teclear. */
export const TIPOS = {
  articulo: 'articulo', // ves la palabra → escribes der/die/das
  palabra: 'palabra', // ves el significado → escribes la palabra (con artículo)
  participio: 'participio', // ves el infinitivo → escribes el Partizip II
  infinitivo: 'infinitivo', // ves el significado → escribes el verbo
};

const AUXILIARES = ['hat', 'ist', 'haben', 'sein'];
const UMLAUTS = { ä: 'ae', ö: 'oe', ü: 'ue', ß: 'ss' };

/**
 * Forma canónica para comparar: minúsculas, sin puntuación ni espacios de
 * sobra, y los umlauts escritos como ae/oe/ue (así «schön» vale tecleado
 * «schoen», que es lo normal en un teclado español, pero «schon» NO cuela).
 * La barra del separable desaparece: «ab|biegen» = «abbiegen».
 */
export function normalizar(texto) {
  return String(texto ?? '')
    .toLowerCase()
    .replace(/[äöüß]/g, (c) => UMLAUTS[c])
    .replace(/\|/g, '')
    .replace(/[.,;:!?¡¿()«»"']/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Quita el «sich» inicial de un reflexivo. */
const sinSich = (s) => s.replace(/^sich /, '');

/** Separa una primera palabra si está en la lista: «hat X» → ['hat', 'X']. */
function partirPrimera(texto, lista) {
  const [primera, ...resto] = texto.split(' ');
  if (resto.length > 0 && lista.includes(primera)) return [primera, resto.join(' ')];
  return [null, texto];
}

/** «hat sich amüsiert» → ['hat', 'sich amüsiert']. */
const partirAuxiliar = (texto) => partirPrimera(texto, AUXILIARES);

/** «die ausgabe» → ['die', 'ausgabe']. */
const partirArticulo = (texto) => partirPrimera(texto, ARTICULOS);

/** El artículo y la palabra tal como se teclean: «die Ausgabe». */
const conArticulo = (t) => `${t.articulo} ${t.palabra}`;

/**
 * El significado que se enseña como enunciado. El campo `es` suele traer
 * matices entre paréntesis («mirar, contemplar (sich etwas anschauen = …)»);
 * para preguntar se usa entero, que es lo que el alumno ya ha visto en la ficha.
 */
const significado = (t) => t.es;

/** Tipos de pregunta que admite una ficha, según lo que lleva dentro. */
export function tiposDeTarjeta(tarjeta) {
  if (tarjeta.tipo === 'sustantivo') return [TIPOS.articulo, TIPOS.palabra];
  if (tarjeta.tipo === 'verbo') return [TIPOS.participio, TIPOS.infinitivo];
  return [TIPOS.palabra]; // adjetivos, adverbios y expresiones: solo la palabra
}

/**
 * Una pregunta concreta sobre una ficha. `muestra` es lo que se ve,
 * `esperado` lo que hay que escribir y `ayuda` el recordatorio del formato.
 */
export function pregunta(tarjeta, tipo) {
  const clave = `${claveTarjeta(tarjeta)}|${tipo}`;
  if (tipo === TIPOS.articulo) {
    return {
      clave, tipo, tarjeta,
      enunciado: '¿Qué artículo lleva esta palabra?',
      muestra: tarjeta.palabra,
      ayuda: 'der, die o das',
      esperado: tarjeta.articulo,
    };
  }
  if (tipo === TIPOS.participio) {
    return {
      clave, tipo, tarjeta,
      enunciado: '¿Cuál es su Partizip II?',
      muestra: tarjeta.infinitivo,
      ayuda: 'puedes poner también el auxiliar: «hat …» o «ist …»',
      esperado: tarjeta.participio,
    };
  }
  if (tipo === TIPOS.infinitivo) {
    return {
      clave, tipo, tarjeta,
      enunciado: '¿Cuál es el verbo en alemán?',
      muestra: significado(tarjeta),
      ayuda: 'el infinitivo',
      esperado: tarjeta.infinitivo,
    };
  }
  const esSustantivo = tarjeta.tipo === 'sustantivo';
  return {
    clave, tipo, tarjeta,
    enunciado: '¿Cuál es la palabra en alemán?',
    muestra: significado(tarjeta),
    ayuda: esSustantivo ? 'con su artículo: «die …»' : 'la palabra sola',
    esperado: esSustantivo ? conArticulo(tarjeta) : tarjeta.palabra,
  };
}

/**
 * Corrige una respuesta tecleada. Devuelve si acierta, la respuesta correcta y
 * un `fallo` que dice QUÉ falló, para poder explicarlo en vez de un simple ✗:
 *   'articulo'  la palabra está bien pero el género no (o falta)
 *   'auxiliar'  el Partizip II está bien pero el hat/ist no
 *   'vacia'     no escribió nada
 *   'forma'     la palabra en sí no es la que toca
 */
export function comprobar(p, respuesta) {
  const dada = normalizar(respuesta);
  const base = { esperado: p.esperado, tarjeta: p.tarjeta };
  if (!dada) return { ...base, acierto: false, fallo: 'vacia' };

  if (p.tipo === TIPOS.articulo) {
    // Vale «die» y vale «die Ausgabe».
    const solo = normalizar(p.esperado);
    const largo = normalizar(conArticulo(p.tarjeta));
    const acierto = dada === solo || dada === largo;
    return { ...base, acierto, fallo: acierto ? null : 'articulo' };
  }

  if (p.tipo === TIPOS.participio) {
    const [aux, resto] = partirAuxiliar(dada);
    const formaOk = sinSich(resto) === sinSich(normalizar(p.esperado));
    if (!formaOk) return { ...base, acierto: false, fallo: 'forma' };
    if (aux && aux !== p.tarjeta.auxiliar) {
      return { ...base, acierto: false, fallo: 'auxiliar', esperado: `${p.tarjeta.auxiliar} ${p.esperado}` };
    }
    return { ...base, acierto: true, fallo: null };
  }

  if (p.tipo === TIPOS.infinitivo) {
    const acierto = sinSich(dada) === sinSich(normalizar(p.esperado));
    return { ...base, acierto, fallo: acierto ? null : 'forma' };
  }

  // palabra: para un sustantivo hay que acertar artículo Y palabra.
  if (p.tarjeta.tipo !== 'sustantivo') {
    const acierto = dada === normalizar(p.esperado);
    return { ...base, acierto, fallo: acierto ? null : 'forma' };
  }
  if (dada === normalizar(p.esperado)) return { ...base, acierto: true, fallo: null };
  // Acertó la palabra pero no el género (o se dejó el artículo): se distingue,
  // porque es exactamente el fallo que este examen quiere sacar a la luz.
  const [, resto] = partirArticulo(dada);
  const palabraOk = resto === normalizar(p.tarjeta.palabra);
  return { ...base, acierto: false, fallo: palabraOk ? 'articulo' : 'forma' };
}

/**
 * Preguntas de una sesión de examen: las fichas que tocan según SM-2 (las
 * mismas que daría `sesionDeMazo`), una pregunta por ficha, elegida entre las
 * que admite con el generador sembrado → la sesión es reproducible.
 */
export function sesionDeExamen(mazo, estados, ahora, opciones = {}) {
  const { semilla = 'examen', tipos = null, ...resto } = opciones;
  const rng = crearGeneradorNormalizado(semilla);
  const permitidos = tipos ? new Set(tipos) : null;
  return sesionDeMazo(mazo, estados, ahora, resto)
    .map((entrada) => {
      const tarjeta = mazo.tarjetas.find((t) => claveTarjeta(t) === entrada.id);
      if (!tarjeta) return null;
      const candidatos = tiposDeTarjeta(tarjeta).filter((x) => !permitidos || permitidos.has(x));
      if (candidatos.length === 0) return null;
      return pregunta(tarjeta, candidatos[Math.floor(rng() * candidatos.length)]);
    })
    .filter(Boolean);
}
