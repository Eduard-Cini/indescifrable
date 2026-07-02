// engine/sopa.js
// Núcleo puro de la Sección 4 (Juegos): sopa de letras con palabras alemanas
// del corpus (la lista de pistas va en español: encontrar «regalo» es
// encontrar GESCHENK).
//
// Generación por colocación aleatorizada con reintentos: para cada palabra se
// sortean dirección y origen y se acepta la primera colocación compatible
// (celda vacía o misma letra → los solapes válidos crean cruces gratis). Es
// el hermano probabilista del backtracking del crucigrama: aquí no hay
// restricción de conectividad, así que no hace falta retroceder — basta
// reintentar; si una palabra no cabe tras K sorteos, se salta y se intenta
// la siguiente del pool (la cuadrícula devuelta lista solo las colocadas).
//
// El relleno de las casillas vacías muestrea la distribución de letras de
// las palabras colocadas (no uniforme sobre a-z): así las letras señuelo son
// plausibles en alemán y no delatan las palabras por contraste.
//
// Sin DOM ni localStorage; azar solo por el LCG determinista de board.js.

import { barajar, crearGeneradorNormalizado } from './board.js';

// Direcciones de lectura natural (sin invertidas: es un juego para aprender
// vocabulario, no un test de visión): →, ↓ y ↘.
export const DIRECCIONES = [
  { dF: 0, dC: 1 },
  { dF: 1, dC: 0 },
  { dF: 1, dC: 1 },
];

const INTENTOS_POR_PALABRA = 80;

/**
 * Genera la sopa: cuadrícula filas×columnas y palabras colocadas con su
 * posición. Determinista por semilla. Coloca hasta n palabras del pool que
 * quepan; devuelve { filas, columnas, cuadricula, palabras }.
 */
export function generarSopa(entradas, { n = 8, filas = 10, columnas = 10, semilla = 'sopa' } = {}) {
  if (!Array.isArray(entradas) || entradas.length === 0) return null;
  const rng = crearGeneradorNormalizado(semilla);
  const pool = barajar(entradas, rng).map((e) => ({ ...e, palabra: e.palabra.toLowerCase() }));

  const cuadricula = Array.from({ length: filas }, () => Array(columnas).fill(null));
  const colocadas = [];

  for (const entrada of pool) {
    if (colocadas.length === n) break;
    const L = entrada.palabra.length;
    if (L > Math.max(filas, columnas)) continue;
    for (let intento = 0; intento < INTENTOS_POR_PALABRA; intento++) {
      const { dF, dC } = DIRECCIONES[Math.floor(rng() * DIRECCIONES.length)];
      const maxF = filas - 1 - dF * (L - 1);
      const maxC = columnas - 1 - dC * (L - 1);
      if (maxF < 0 || maxC < 0) continue;
      const fila = Math.floor(rng() * (maxF + 1));
      const col = Math.floor(rng() * (maxC + 1));

      let compatible = true;
      for (let i = 0; i < L; i++) {
        const puesta = cuadricula[fila + dF * i][col + dC * i];
        if (puesta !== null && puesta !== entrada.palabra[i]) {
          compatible = false;
          break;
        }
      }
      if (!compatible) continue;

      for (let i = 0; i < L; i++) {
        cuadricula[fila + dF * i][col + dC * i] = entrada.palabra[i];
      }
      colocadas.push({ palabra: entrada.palabra, pista: entrada.pista, fila, col, dF, dC });
      break;
    }
  }

  // Relleno: muestreo de la distribución de letras de las palabras colocadas.
  const letras = colocadas.flatMap((p) => [...p.palabra]);
  for (let f = 0; f < filas; f++) {
    for (let c = 0; c < columnas; c++) {
      if (cuadricula[f][c] === null) {
        cuadricula[f][c] = letras[Math.floor(rng() * letras.length)];
      }
    }
  }

  colocadas.sort((a, b) => a.pista.localeCompare(b.pista));
  return { filas, columnas, cuadricula, palabras: colocadas };
}

/**
 * Palabra que se lee entre dos casillas (inclusive) si están alineadas en
 * alguna de las DIRECCIONES (en cualquiera de los dos sentidos de la línea);
 * null si no forman línea recta válida. La UI la usa para la selección
 * inicio → fin.
 */
export function extraerPalabra(cuadricula, a, b) {
  const dF = Math.sign(b.fila - a.fila);
  const dC = Math.sign(b.col - a.col);
  const pasosF = Math.abs(b.fila - a.fila);
  const pasosC = Math.abs(b.col - a.col);
  const pasos = Math.max(pasosF, pasosC);
  const recta =
    (pasosF === 0 || pasosC === 0 || pasosF === pasosC) && pasos > 0;
  if (!recta) return null;

  let palabra = '';
  for (let i = 0; i <= pasos; i++) {
    palabra += cuadricula[a.fila + dF * i][a.col + dC * i];
  }
  return palabra;
}

/**
 * ¿La selección inicio → fin marca exactamente una palabra colocada (en su
 * sentido de lectura o al revés)? Devuelve la colocada o null.
 */
export function buscarSeleccion(sopa, a, b) {
  const leida = extraerPalabra(sopa.cuadricula, a, b);
  if (!leida) return null;
  const alReves = [...leida].reverse().join('');
  for (const p of sopa.palabras) {
    if (p.palabra !== leida && p.palabra !== alReves) continue;
    const L = p.palabra.length;
    const fin = { fila: p.fila + p.dF * (L - 1), col: p.col + p.dC * (L - 1) };
    const coincide =
      (a.fila === p.fila && a.col === p.col && b.fila === fin.fila && b.col === fin.col) ||
      (b.fila === p.fila && b.col === p.col && a.fila === fin.fila && a.col === fin.col);
    if (coincide) return p;
  }
  return null;
}

/** Casillas (claves "f,c") que ocupa una palabra colocada — para resaltar. */
export function casillasDe(colocada) {
  const posiciones = [];
  for (let i = 0; i < colocada.palabra.length; i++) {
    posiciones.push(`${colocada.fila + colocada.dF * i},${colocada.col + colocada.dC * i}`);
  }
  return posiciones;
}
