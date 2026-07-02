// engine/wordle.js
// Núcleo puro de la Sección 4 (Juegos): adivinar la palabra (estilo Wordle)
// sobre el vocabulario alemán del corpus.
//
// Dos piezas con matemática de verdad:
//
// 1. evaluar(secreto, intento): el feedback verde/amarillo/gris con letras
//    REPETIDAS bien contadas exige dos pasadas — primero se casan los verdes
//    y solo las letras del secreto que sobran pueden dar amarillo. Con una
//    sola pasada, «anna» contra secreto «nase» marcaría dos amarillos para
//    la «n» cuando el secreto solo tiene una.
//
// 2. El juego visto desde teoría de la información: cada intento induce una
//    PARTICIÓN del conjunto de candidatas (una clase por patrón de feedback)
//    y su calidad es la entropía de Shannon de esa partición — bits que se
//    esperan aprender. filtrarConsistentes/entropiaDe alimentan la pista de
//    la UI y el solver voraz de las métricas (simulacion/juegos-stats.mjs).
//
// Sin DOM ni localStorage; el azar entra por el LCG determinista de board.js.

import { crearGeneradorNormalizado } from './board.js';

export const NO = 'no';
export const CASI = 'casi';
export const BIEN = 'bien';

/**
 * Feedback de un intento contra el secreto: array de 'bien' | 'casi' | 'no'
 * por posición. Letras repetidas: cada letra del secreto solo puede justificar
 * UNA marca (los verdes consumen primero, luego los amarillos por orden).
 */
export function evaluar(secreto, intento) {
  const n = secreto.length;
  const resultado = Array(n).fill(NO);
  const sobrantes = new Map(); // letras del secreto no casadas en verde
  for (let i = 0; i < n; i++) {
    if (intento[i] === secreto[i]) {
      resultado[i] = BIEN;
    } else {
      sobrantes.set(secreto[i], (sobrantes.get(secreto[i]) ?? 0) + 1);
    }
  }
  for (let i = 0; i < n; i++) {
    if (resultado[i] === BIEN) continue;
    const quedan = sobrantes.get(intento[i]) ?? 0;
    if (quedan > 0) {
      resultado[i] = CASI;
      sobrantes.set(intento[i], quedan - 1);
    }
  }
  return resultado;
}

/** ¿El feedback es todo verde? */
export function esVictoria(resultado) {
  return resultado.length > 0 && resultado.every((r) => r === BIEN);
}

/** Clave compacta de un feedback (para particiones y tests): "BC-N…". */
export function patron(resultado) {
  return resultado.map((r) => (r === BIEN ? 'B' : r === CASI ? 'C' : '-')).join('');
}

/** Secreto determinista por semilla, uniforme sobre el diccionario. */
export function elegirSecreto(palabras, semilla = 'wordle') {
  if (!Array.isArray(palabras) || palabras.length === 0) return null;
  const rng = crearGeneradorNormalizado(semilla);
  return [...palabras].sort()[Math.floor(rng() * palabras.length)];
}

/**
 * Candidatas aún posibles dados los intentos jugados: una palabra es
 * consistente si, de ser el secreto, habría producido exactamente el mismo
 * feedback en cada intento. (Es la definición, no una heurística de letras
 * prohibidas: maneja repetidas sin casos especiales.)
 */
export function filtrarConsistentes(palabras, intentos) {
  return palabras.filter((candidata) =>
    intentos.every(({ intento, resultado }) =>
      patron(evaluar(candidata, intento)) === patron(resultado)
    )
  );
}

/**
 * Entropía de Shannon (en bits) de la partición que un intento induce sobre
 * las candidatas: H = −Σ p_i · log2(p_i) con p_i = |clase_i| / |candidatas|.
 * Mide la información ESPERADA del intento; el mejor primer intento es el
 * argmax sobre el diccionario.
 */
export function entropiaDe(intento, candidatas) {
  if (candidatas.length === 0) return 0;
  const clases = new Map();
  for (const secreto of candidatas) {
    const clave = patron(evaluar(secreto, intento));
    clases.set(clave, (clases.get(clave) ?? 0) + 1);
  }
  let h = 0;
  for (const tam of clases.values()) {
    const p = tam / candidatas.length;
    h -= p * Math.log2(p);
  }
  return h;
}

/** El intento de mayor entropía (empates → orden alfabético: determinista). */
export function mejorIntento(palabras, candidatas = palabras) {
  let mejor = null;
  let mejorH = -1;
  for (const palabra of [...palabras].sort()) {
    const h = entropiaDe(palabra, candidatas);
    if (h > mejorH) {
      mejor = palabra;
      mejorH = h;
    }
  }
  return mejor && { intento: mejor, entropia: mejorH };
}
