// engine/juegos.js
// Núcleo puro de la Sección 4: selección del pool (todo el corpus o una
// lectura concreta) y DISPONIBILIDAD de cada juego según la riqueza del
// vocabulario — la misma organización por lectura que la Sección 3.
//
// Cada juego tiene un criterio formal, no una lista curada a mano:
//  - escalera: existe al menos un reto (un par de palabras a distancia >= 3
//    en el grafo de Hamming 1). Las lecturas de principiante suelen tener
//    grafos casi sin aristas → el juego se oculta solo.
//  - wordle: alguna longitud con >= MIN_WORDLE palabras (con menos, un par
//    de intentos agotan las candidatas y no hay juego).
//  - crucigrama / sopa: >= MIN_TABLERO entradas con pista.
//  - sudoku: >= 1 palabra de 9 letras todas distintas (los 9 símbolos).
// Los selectores de la UI también salen de aquí (longitudes y nº de pasos
// realmente jugables por pool), así nunca ofrecen combinaciones vacías.

import { construirGrafo, distanciasDesde } from './escalera.js';

export const MIN_WORDLE = 12;
export const MIN_TABLERO = 6;
export const PASOS_ESCALERA = [3, 4, 5, 6];
export const SLUG_CORPUS = 'corpus';

/** Pool del slug: 'corpus' = todo el léxico; si no, la lectura (o null). */
export function poolDe(data, slug = SLUG_CORPUS) {
  if (slug === SLUG_CORPUS) {
    return {
      slug: SLUG_CORPUS,
      titulo: 'Todo el corpus',
      nivel: null,
      escalera: data.escalera,
      crucigrama: data.crucigrama,
      sudoku: data.sudoku,
    };
  }
  return data.lecturas?.find((l) => l.slug === slug) ?? null;
}

/**
 * Distancias de PASOS_ESCALERA alcanzadas por algún par del grafo de estas
 * palabras (BFS desde cada nodo). Decide qué dificultades ofrece el selector
 * y, de paso, si la escalera es jugable (lista no vacía).
 */
export function pasosDisponibles(palabras) {
  const grafo = construirGrafo(palabras);
  const alcanzadas = new Set();
  const maximo = Math.max(...PASOS_ESCALERA);
  for (const origen of grafo.keys()) {
    for (const d of distanciasDesde(grafo, origen).values()) {
      if (d >= 3 && d <= maximo) alcanzadas.add(d);
    }
    if (alcanzadas.size === PASOS_ESCALERA.length) break;
  }
  return PASOS_ESCALERA.filter((p) => alcanzadas.has(p));
}

/** Longitudes del pool con escalera jugable (algún par a distancia >= 3). */
export function longitudesEscalera(escalera) {
  return Object.keys(escalera ?? {})
    .filter((L) => pasosDisponibles(Object.keys(escalera[L])).length > 0)
    .sort();
}

/** Longitudes del pool con Wordle jugable (>= MIN_WORDLE palabras). */
export function longitudesWordle(escalera) {
  return Object.keys(escalera ?? {})
    .filter((L) => Object.keys(escalera[L]).length >= MIN_WORDLE)
    .sort();
}

/** Tamaños de tablero ofrecibles (crucigrama/sopa) para un pool. */
export function tamanosTablero(entradas, opciones = [6, 8, 10]) {
  return opciones.filter((n) => (entradas?.length ?? 0) >= n);
}

/** Juegos jugables con este pool, en el orden del hub. */
export function juegosDisponibles(pool) {
  if (!pool) return [];
  const juegos = [];
  if (longitudesEscalera(pool.escalera).length > 0) juegos.push('escalera');
  if ((pool.crucigrama?.length ?? 0) >= MIN_TABLERO) juegos.push('crucigrama');
  if (longitudesWordle(pool.escalera).length > 0) juegos.push('wordle');
  if ((pool.crucigrama?.length ?? 0) >= MIN_TABLERO) juegos.push('sopa');
  if ((pool.sudoku?.length ?? 0) > 0) juegos.push('sudoku');
  return juegos;
}

// Orden de niveles para listar lecturas (como la Sección 3).
const ORDEN_NIVEL = { principiante: 0, intermedio: 1, avanzado: 2 };

/** Lecturas del JSON ordenadas por nivel y título (ya vienen así del pipeline,
 *  pero el orden es contrato de la UI, no del generador). */
export function lecturasOrdenadas(data) {
  return [...(data.lecturas ?? [])].sort(
    (a, b) =>
      (ORDEN_NIVEL[a.nivel] ?? 9) - (ORDEN_NIVEL[b.nivel] ?? 9) ||
      a.titulo.localeCompare(b.titulo)
  );
}

/** Lecturas cuyo vocabulario aguanta un juego concreto, en orden de nivel.
 *  Alimenta el índice de vocabularios de cada juego (la UI añade además
 *  «Todo el corpus», que los aguanta todos). */
export function lecturasConJuego(data, juego) {
  return lecturasOrdenadas(data).filter((l) => juegosDisponibles(l).includes(juego));
}
