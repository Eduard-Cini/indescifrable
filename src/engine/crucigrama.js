// engine/crucigrama.js
// Núcleo puro de la Sección 4 (Juegos): generación de crucigramas por
// BACKTRACKING. Las entradas (palabra alemana + pista en español) salen del
// corpus vía pipeline/juegos.py; aquí se decide la colocación.
//
// Búsqueda: se parte de una palabra semilla en horizontal y se extiende el
// tablero palabra a palabra. Cada candidata genera sus colocaciones legales
// (ancladas en un cruce con una letra ya puesta, reglas clásicas de
// crucigrama: extremos libres y sin contactos laterales fuera de los cruces),
// se prueban de mejor a peor (más cruces primero) y si una rama no alcanza el
// objetivo se DESHACE la colocación y se prueba la siguiente (backtracking
// con presupuesto de nodos; si el objetivo n no cabe, se reintenta con n−1).
//
// Sin DOM ni localStorage; azar solo por el LCG determinista de board.js →
// mismo crucigrama para la misma semilla.

import { barajar, crearGeneradorNormalizado } from './board.js';

const PRESUPUESTO_NODOS = 5000;

const clave = (fila, col) => `${fila},${col}`;

/**
 * ¿Se puede poner `palabra` en (fila, col, dir) sobre las celdas actuales?
 * Devuelve el número de cruces (letras que ya estaban) o -1 si es ilegal.
 * Reglas: en cada celda o coincide la letra (cruce) o está vacía; una celda
 * vacía no puede tocar lateralmente otra palabra; la celda anterior al inicio
 * y la posterior al final deben estar libres.
 */
export function puedeColocar(celdas, palabra, fila, col, dir) {
  const dF = dir === 'V' ? 1 : 0;
  const dC = dir === 'H' ? 1 : 0;
  if (celdas.has(clave(fila - dF, col - dC))) return -1;
  if (celdas.has(clave(fila + dF * palabra.length, col + dC * palabra.length))) return -1;

  let cruces = 0;
  for (let i = 0; i < palabra.length; i++) {
    const f = fila + dF * i;
    const c = col + dC * i;
    const puesta = celdas.get(clave(f, c));
    if (puesta !== undefined) {
      if (puesta !== palabra[i]) return -1;
      cruces += 1;
    } else if (celdas.has(clave(f - dC, c - dF)) || celdas.has(clave(f + dC, c + dF))) {
      return -1; // contacto lateral fuera de un cruce
    }
  }
  return cruces;
}

/**
 * Colocaciones legales de `palabra` ancladas en algún cruce con el tablero,
 * ordenadas de más a menos cruces (y por posición para desempatar de forma
 * determinista).
 */
export function colocacionesValidas(celdas, palabra) {
  const opciones = [];
  const vistas = new Set();
  for (const [pos, letra] of celdas) {
    const [f, c] = pos.split(',').map(Number);
    for (let i = 0; i < palabra.length; i++) {
      if (palabra[i] !== letra) continue;
      for (const [dir, fila, col] of [
        ['H', f, c - i],
        ['V', f - i, c],
      ]) {
        const firma = `${dir}:${fila},${col}`;
        if (vistas.has(firma)) continue;
        vistas.add(firma);
        const cruces = puedeColocar(celdas, palabra, fila, col, dir);
        if (cruces > 0) opciones.push({ fila, col, dir, cruces });
      }
    }
  }
  return opciones.sort(
    (a, b) => b.cruces - a.cruces || a.fila - b.fila || a.col - b.col || (a.dir < b.dir ? -1 : 1)
  );
}

function pintar(celdas, palabra, { fila, col, dir }) {
  const nuevas = [];
  for (let i = 0; i < palabra.length; i++) {
    const pos = clave(fila + (dir === 'V' ? i : 0), col + (dir === 'H' ? i : 0));
    if (!celdas.has(pos)) {
      celdas.set(pos, palabra[i]);
      nuevas.push(pos);
    }
  }
  return nuevas; // solo las celdas añadidas, para poder deshacer el cruce
}

/**
 * Genera un crucigrama determinista por semilla con (hasta) n palabras.
 * Baraja las entradas, toma un pool de candidatas y busca por backtracking
 * una colocación con n palabras; si el presupuesto se agota sin lograrlo,
 * reintenta con n−1 (siempre termina: con 1 palabra nunca falla).
 * Devuelve { palabras: [{palabra, pista, numero, fila, col, dir}], filas, columnas }.
 */
export function generarCrucigrama(entradas, { n = 8, semilla = 'cruci', maxCandidatas = 30 } = {}) {
  if (!Array.isArray(entradas) || entradas.length === 0) return null;
  const rng = crearGeneradorNormalizado(semilla);
  const pool = barajar(entradas, rng)
    .slice(0, maxCandidatas)
    .map((e) => ({ ...e, palabra: e.palabra.toLowerCase() }));

  for (let objetivo = Math.min(n, pool.length); objetivo >= 1; objetivo--) {
    let nodos = 0;

    const buscar = (colocadas, celdas, restantes) => {
      if (colocadas.length === objetivo) return colocadas;
      if (++nodos > PRESUPUESTO_NODOS) return null;
      for (let i = 0; i < restantes.length; i++) {
        const cand = restantes[i];
        const siguientes = restantes.slice(0, i).concat(restantes.slice(i + 1));
        for (const opcion of colocacionesValidas(celdas, cand.palabra)) {
          const nuevas = pintar(celdas, cand.palabra, opcion);
          colocadas.push({ ...cand, ...opcion });
          const exito = buscar(colocadas, celdas, siguientes);
          if (exito) return exito;
          colocadas.pop();
          for (const pos of nuevas) celdas.delete(pos);
          if (nodos > PRESUPUESTO_NODOS) return null;
        }
      }
      return null;
    };

    // La semilla del tablero: la palabra más larga del pool ancla mejor.
    const porLongitud = [...pool].sort(
      (a, b) => b.palabra.length - a.palabra.length || (a.palabra < b.palabra ? -1 : 1)
    );
    for (const primera of porLongitud) {
      const celdas = new Map();
      const colocacion = { fila: 0, col: 0, dir: 'H', cruces: 0 };
      pintar(celdas, primera.palabra, colocacion);
      const resto = pool.filter((e) => e !== primera);
      const exito = buscar([{ ...primera, ...colocacion }], celdas, resto);
      if (exito) return normalizar(exito);
    }
  }
  return null; // inalcanzable: objetivo=1 siempre coloca la primera palabra
}

/** Traslada a origen (0,0), calcula dimensiones y numera al estilo clásico. */
function normalizar(colocadas) {
  let minF = Infinity;
  let minC = Infinity;
  let maxF = -Infinity;
  let maxC = -Infinity;
  for (const p of colocadas) {
    const finF = p.fila + (p.dir === 'V' ? p.palabra.length - 1 : 0);
    const finC = p.col + (p.dir === 'H' ? p.palabra.length - 1 : 0);
    minF = Math.min(minF, p.fila);
    minC = Math.min(minC, p.col);
    maxF = Math.max(maxF, finF);
    maxC = Math.max(maxC, finC);
  }
  const palabras = colocadas.map((p) => ({
    palabra: p.palabra,
    pista: p.pista,
    fila: p.fila - minF,
    col: p.col - minC,
    dir: p.dir,
  }));
  // Numeración: casillas iniciales en orden de lectura; dos palabras que
  // empiezan en la misma casilla (una H y una V) comparten número.
  const inicios = [...new Set(palabras.map((p) => clave(p.fila, p.col)))]
    .map((pos) => pos.split(',').map(Number))
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const numeroDe = new Map(inicios.map(([f, c], i) => [clave(f, c), i + 1]));
  for (const p of palabras) p.numero = numeroDe.get(clave(p.fila, p.col));
  palabras.sort((a, b) => a.numero - b.numero || (a.dir < b.dir ? -1 : 1));
  return { palabras, filas: maxF - minF + 1, columnas: maxC - minC + 1 };
}

/** Matriz filas×columnas con la letra de cada casilla (null = casilla negra). */
export function cuadricula(cruci) {
  const grid = Array.from({ length: cruci.filas }, () => Array(cruci.columnas).fill(null));
  for (const p of cruci.palabras) {
    for (let i = 0; i < p.palabra.length; i++) {
      grid[p.fila + (p.dir === 'V' ? i : 0)][p.col + (p.dir === 'H' ? i : 0)] = p.palabra[i];
    }
  }
  return grid;
}

/** Métricas (para docs): casillas, cruces reales y densidad del rectángulo. */
export function metricas(cruci) {
  const ocupadas = new Map();
  for (const p of cruci.palabras) {
    for (let i = 0; i < p.palabra.length; i++) {
      const pos = clave(p.fila + (p.dir === 'V' ? i : 0), p.col + (p.dir === 'H' ? i : 0));
      ocupadas.set(pos, (ocupadas.get(pos) ?? 0) + 1);
    }
  }
  const cruces = [...ocupadas.values()].filter((v) => v > 1).length;
  return {
    palabras: cruci.palabras.length,
    casillas: ocupadas.size,
    cruces,
    densidad: ocupadas.size / (cruci.filas * cruci.columnas),
  };
}
