import { describe, it, expect } from 'vitest';
import {
  DIFICULTADES,
  esValido,
  generarSolucion,
  contarSoluciones,
  excavar,
  generarSudoku,
} from './sudoku';
import { crearGeneradorNormalizado } from './board';
import juegosPorIdioma from '../data/juegos.json';
const juegos = juegosPorIdioma.de;

const ENTRADAS = [
  { palabra: 'auswendig', pista: 'de memoria' },
  { palabra: 'mondlicht', pista: 'luz de luna' },
];

// ¿Es una solución de sudoku válida? filas, columnas y cajas con 9 símbolos.
function esSolucionValida(matriz) {
  const grupos = [];
  for (let f = 0; f < 9; f++) grupos.push(matriz[f]);
  for (let c = 0; c < 9; c++) grupos.push(matriz.map((fila) => fila[c]));
  for (let bf = 0; bf < 9; bf += 3) {
    for (let bc = 0; bc < 9; bc += 3) {
      const caja = [];
      for (let f = bf; f < bf + 3; f++) {
        for (let c = bc; c < bc + 3; c++) caja.push(matriz[f][c]);
      }
      grupos.push(caja);
    }
  }
  return grupos.every((g) => new Set(g).size === 9 && !g.includes(null));
}

describe('generarSolucion y esValido', () => {
  it('produce una cuadrícula válida (filas, columnas y cajas)', () => {
    const plano = generarSolucion(crearGeneradorNormalizado('S'));
    const matriz = Array.from({ length: 9 }, (_, f) => plano.slice(f * 9, f * 9 + 9));
    expect(esSolucionValida(matriz)).toBe(true);
  });

  it('esValido detecta choques de fila, columna y caja', () => {
    const tablero = new Array(81).fill(0);
    tablero[0] = 5; // (0,0)
    expect(esValido(tablero, 8, 5)).toBe(false); // misma fila
    expect(esValido(tablero, 72, 5)).toBe(false); // misma columna
    expect(esValido(tablero, 10, 5)).toBe(false); // misma caja
    expect(esValido(tablero, 40, 5)).toBe(true); // centro: sin conflicto
  });
});

describe('contarSoluciones y excavar', () => {
  const rng = crearGeneradorNormalizado('EX');
  const solucion = generarSolucion(rng);

  it('una solución completa cuenta exactamente 1', () => {
    expect(contarSoluciones(solucion)).toBe(1);
  });

  it('el tablero vacío tiene más de una solución', () => {
    expect(contarSoluciones(new Array(81).fill(0), 2)).toBe(2);
  });

  it('el excavado conserva la unicidad', () => {
    const inicial = excavar(solucion, DIFICULTADES.medio, rng);
    expect(contarSoluciones(inicial, 2)).toBe(1);
    // y las dadas que quedan son las de la solución
    inicial.forEach((v, i) => {
      if (v !== 0) expect(v).toBe(solucion[i]);
    });
  });
});

describe('generarSudoku', () => {
  const sudoku = generarSudoku(ENTRADAS, { dificultad: 'facil', semilla: 'T' });

  it('la solución es un sudoku válido sobre las 9 letras de la palabra', () => {
    expect(esSolucionValida(sudoku.solucion)).toBe(true);
    expect(new Set(sudoku.solucion.flat())).toEqual(new Set(sudoku.palabra));
  });

  it('la fila escondida lee la palabra completa', () => {
    expect(sudoku.solucion[sudoku.fila].join('')).toBe(sudoku.palabra);
  });

  it('el inicial es un sub-tablero de la solución con las dadas anunciadas', () => {
    let dadas = 0;
    sudoku.inicial.forEach((fila, f) =>
      fila.forEach((letra, c) => {
        if (letra !== null) {
          dadas += 1;
          expect(letra).toBe(sudoku.solucion[f][c]);
        }
      })
    );
    expect(dadas).toBe(sudoku.dadas);
    expect(sudoku.dadas).toBeGreaterThanOrEqual(DIFICULTADES.facil);
  });

  it('las dificultades dejan menos dadas al subir', () => {
    const facil = generarSudoku(ENTRADAS, { dificultad: 'facil', semilla: 'D' });
    const medio = generarSudoku(ENTRADAS, { dificultad: 'medio', semilla: 'D' });
    const dificil = generarSudoku(ENTRADAS, { dificultad: 'dificil', semilla: 'D' });
    expect(facil.dadas).toBeGreaterThan(medio.dadas);
    expect(medio.dadas).toBeGreaterThan(dificil.dadas);
  });

  it('es determinista por semilla y varía con ella', () => {
    expect(generarSudoku(ENTRADAS, { dificultad: 'medio', semilla: 'X' })).toEqual(
      generarSudoku(ENTRADAS, { dificultad: 'medio', semilla: 'X' })
    );
    const tableros = ['a', 'b', 'c'].map((s) =>
      JSON.stringify(generarSudoku(ENTRADAS, { semilla: s }).solucion)
    );
    expect(new Set(tableros).size).toBeGreaterThan(1);
  });

  it('sin entradas devuelve null', () => {
    expect(generarSudoku([], {})).toBeNull();
  });

  it('funciona con el pool real del corpus', () => {
    const real = generarSudoku(juegos.sudoku, { dificultad: 'dificil', semilla: 'DEMO' });
    expect(esSolucionValida(real.solucion)).toBe(true);
    expect(real.letras).toHaveLength(9);
    expect(new Set(real.letras).size).toBe(9);
  });
});
