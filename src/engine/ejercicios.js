// engine/ejercicios.js
// Ejercicios de opción múltiple de «Más contenidos» (gramática del capítulo 10).
// Un ejercicio tiene `partes` (el texto alrededor de los huecos) y opciones que
// pueden rellenar VARIOS huecos a la vez, separados por « … »: la pasiva parte
// el verbo en dos («Am Montag wird der Raum aufgeräumt» → «wird … aufgeräumt»).
// Con `partes: null` cada opción es una frase completa (p. ej. «¿cuál está en
// pasiva?»). El barajado determinista y la corrección son los de gramatica.js.
//
// Módulo puro: sin DOM ni localStorage.

export const SEPARADOR = '…';

/** Trozos que rellena una opción, en orden: «wird … gebaut» → ['wird', 'gebaut']. */
export function trozos(opcion) {
  return String(opcion).split(SEPARADOR).map((s) => s.trim());
}

/** Número de huecos del ejercicio (0 si las opciones son frases completas). */
export function numHuecos(ejercicio) {
  return ejercicio.partes ? ejercicio.partes.length - 1 : 0;
}

/**
 * Segmentos para pintar la frase: texto fijo y huecos alternados,
 * [{ texto }, { hueco }, …]. Sin opción, los huecos quedan a null.
 */
export function segmentos(ejercicio, opcion = null) {
  if (!ejercicio.partes) return [];
  const relleno = opcion === null ? [] : trozos(opcion);
  const out = [];
  ejercicio.partes.forEach((texto, i) => {
    if (texto) out.push({ texto });
    if (i < ejercicio.partes.length - 1) out.push({ hueco: relleno[i] ?? null });
  });
  return out;
}

/** Frase completa con la opción puesta en sus huecos. */
export function rellenar(ejercicio, opcion) {
  if (!ejercicio.partes) return opcion;
  return segmentos(ejercicio, opcion)
    .map((s) => s.texto ?? s.hueco)
    .join('');
}

/**
 * Coherencia de un ejercicio (vacío = válido): respuesta fuera de los
 * distractores, sin repetidos y cada opción rellena exactamente sus huecos.
 */
export function problemasDeEjercicio(ej) {
  const p = [];
  if (!ej.id) p.push('id');
  if (!ej.respuesta) p.push('respuesta');
  const distr = ej.distractores ?? [];
  if (distr.length === 0) p.push('sin distractores');
  if (distr.includes(ej.respuesta)) p.push('la respuesta está entre los distractores');
  if (new Set(distr).size !== distr.length) p.push('distractores repetidos');
  if (ej.partes) {
    const n = numHuecos(ej);
    for (const op of [ej.respuesta, ...distr]) {
      if (trozos(op).length !== n) p.push(`«${op}» no rellena ${n} hueco(s)`);
    }
  } else if (!ej.pregunta) {
    p.push('pregunta');
  }
  return p;
}

/** Clave estable del progreso de una tanda: `tema|tanda`. */
export function claveTanda(tema, tandaId) {
  return `${tema}|${tandaId}`;
}
