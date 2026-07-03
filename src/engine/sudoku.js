// engine/sudoku.js
// Núcleo puro de la Sección 4 (Juegos): SUDOKU DE PALABRAS. Un sudoku 9×9
// clásico cuyos nueve símbolos no son dígitos sino las nueve letras (todas
// distintas) de una palabra alemana del corpus; una fila de la solución lee
// la palabra completa, y al resolverlo se descubre cuál (con su traducción).
//
// Tres piezas algorítmicas:
//  1. Solución completa por BACKTRACKING con candidatos barajados (LCG
//     determinista de board.js): una cuadrícula válida uniforme-ish por semilla.
//  2. Excavado con UNICIDAD: se intenta vaciar casillas en orden aleatorio y
//     un contador de soluciones (backtracking con heurística MRV, corta en 2)
//     solo consiente el vaciado si la solución sigue siendo única. La
//     DIFICULTAD es del sudoku en sí: cuántas casillas dadas quedan.
//  3. La palabra entra por una BIYECCIÓN dígito→letra definida por la fila
//     elegida: como toda fila de una solución contiene los 9 dígitos, asignar
//     a cada dígito la letra de la palabra en esa columna garantiza que la
//     fila lea la palabra y que el resto del tablero sea consistente.
//
// Sin DOM ni localStorage; mismo sudoku para la misma semilla.

import { barajar, crearGeneradorNormalizado } from './board.js';

// Casillas DADAS por dificultad (81 − dadas = huecos a excavar). El excavado
// respeta la unicidad, así que puede quedarse con alguna dada de más si ya no
// hay casilla removible.
export const DIFICULTADES = { facil: 40, medio: 32, dificil: 26 };

const filaDe = (i) => Math.floor(i / 9);
const colDe = (i) => i % 9;
const cajaDe = (i) => Math.floor(filaDe(i) / 3) * 3 + Math.floor(colDe(i) / 3);

/** ¿Puede ir el valor v (1-9) en la posición i sin chocar en fila/columna/caja? */
export function esValido(tablero, i, v) {
  const f = filaDe(i);
  const c = colDe(i);
  const b = cajaDe(i);
  for (let j = 0; j < 81; j++) {
    if (tablero[j] !== v) continue;
    if (filaDe(j) === f || colDe(j) === c || cajaDe(j) === b) return false;
  }
  return true;
}

function candidatosDe(tablero, i) {
  const usados = new Set();
  const f = filaDe(i);
  const c = colDe(i);
  const b = cajaDe(i);
  for (let j = 0; j < 81; j++) {
    if (tablero[j] && (filaDe(j) === f || colDe(j) === c || cajaDe(j) === b)) {
      usados.add(tablero[j]);
    }
  }
  const libres = [];
  for (let v = 1; v <= 9; v++) if (!usados.has(v)) libres.push(v);
  return libres;
}

/** Solución completa (array de 81 dígitos 1-9) por backtracking barajado. */
export function generarSolucion(rng) {
  const tablero = new Array(81).fill(0);
  const rellenar = (i) => {
    if (i === 81) return true;
    for (const v of barajar(candidatosDe(tablero, i), rng)) {
      tablero[i] = v;
      if (rellenar(i + 1)) return true;
      tablero[i] = 0;
    }
    return false;
  };
  rellenar(0);
  return tablero;
}

/**
 * Cuenta soluciones de un tablero (0 = hueco) hasta `limite` (con 2 basta
 * para decidir unicidad). Backtracking con MRV: siempre ramifica por la
 * casilla vacía con menos candidatos — poda brutal frente al orden fijo.
 */
export function contarSoluciones(tablero, limite = 2) {
  const t = [...tablero];
  let cuenta = 0;
  const paso = () => {
    if (cuenta >= limite) return;
    let mejor = -1;
    let candidatos = null;
    for (let i = 0; i < 81; i++) {
      if (t[i] !== 0) continue;
      const c = candidatosDe(t, i);
      if (candidatos === null || c.length < candidatos.length) {
        mejor = i;
        candidatos = c;
        if (c.length <= 1) break;
      }
    }
    if (mejor === -1) {
      cuenta += 1;
      return;
    }
    for (const v of candidatos) {
      t[mejor] = v;
      paso();
      t[mejor] = 0;
      if (cuenta >= limite) return;
    }
  };
  paso();
  return cuenta;
}

/**
 * Excava la solución hasta dejar ~`dadas` casillas, vaciando en orden
 * aleatorio y solo si la solución sigue siendo ÚNICA. Devuelve el tablero
 * inicial (0 = hueco).
 */
export function excavar(solucion, dadas, rng) {
  const tablero = [...solucion];
  let quedan = 81;
  for (const i of barajar([...tablero.keys()], rng)) {
    if (quedan <= dadas) break;
    const guardada = tablero[i];
    tablero[i] = 0;
    if (contarSoluciones(tablero, 2) === 1) {
      quedan -= 1;
    } else {
      tablero[i] = guardada;
    }
  }
  return tablero;
}

const aLetras = (tablero, letraDe) =>
  Array.from({ length: 9 }, (_, f) =>
    Array.from({ length: 9 }, (_, c) => {
      const v = tablero[f * 9 + c];
      return v === 0 ? null : letraDe[v];
    })
  );

/**
 * Genera el sudoku de palabras: elige palabra (9 letras distintas) y fila
 * escondida, resuelve, mapea dígito→letra y excava según la dificultad.
 * Devuelve { palabra, pista, fila, letras, dadas, inicial, solucion } con
 * `inicial` y `solucion` como matrices 9×9 de letras (null = hueco).
 */
export function generarSudoku(entradas, { dificultad = 'facil', semilla = 'sudoku' } = {}) {
  if (!Array.isArray(entradas) || entradas.length === 0) return null;
  const rng = crearGeneradorNormalizado(semilla);
  const orden = [...entradas].sort((a, b) => (a.palabra < b.palabra ? -1 : 1));
  const entrada = orden[Math.floor(rng() * orden.length)];
  const palabra = entrada.palabra.toLowerCase();

  const solucion = generarSolucion(rng);
  const fila = Math.floor(rng() * 9);

  // Biyección dígito→letra: la fila elegida contiene los 9 dígitos.
  const letraDe = {};
  for (let c = 0; c < 9; c++) {
    letraDe[solucion[fila * 9 + c]] = palabra[c];
  }

  const dadas = DIFICULTADES[dificultad] ?? DIFICULTADES.facil;
  const inicial = excavar(solucion, dadas, rng);

  return {
    palabra,
    pista: entrada.pista,
    fila,
    letras: [...palabra].sort(),
    dadas: inicial.filter((v) => v !== 0).length,
    inicial: aLetras(inicial, letraDe),
    solucion: aLetras(solucion, letraDe),
  };
}
