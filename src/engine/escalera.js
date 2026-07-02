// engine/escalera.js
// Núcleo puro de la Sección 4 (Juegos): escalera de palabras.
//
// Modelo: grafo no dirigido cuyos nodos son las palabras del diccionario y
// cuyas aristas unen palabras a distancia de Hamming 1 (misma longitud, una
// sola letra distinta). El reto es transformar una palabra en otra pasando
// solo por palabras del diccionario; el camino mínimo se encuentra por BFS.
//
// La construcción del grafo evita el O(n²) de comparar todas las parejas con
// la técnica de cubetas comodín: cada palabra de longitud L cae en L cubetas
// (una por posición enmascarada, p. ej. hand → *and, h*nd, ha*d, han*) y dos
// palabras son vecinas si y solo si comparten alguna cubeta.
//
// Sin DOM ni localStorage (testeable con Vitest); el azar entra por el LCG
// determinista de board.js → mismos retos para la misma semilla.

import { barajar, crearGeneradorNormalizado } from './board';

/** ¿Difieren exactamente en una letra (misma longitud)? */
export function sonVecinas(a, b) {
  if (a === b || a.length !== b.length) return false;
  let difs = 0;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i] && ++difs > 1) return false;
  }
  return difs === 1;
}

/**
 * Grafo de Hamming 1 sobre el diccionario: Map palabra → vecinas (ordenadas).
 * Cubetas comodín → O(n·L) en construcción; palabras de longitudes distintas
 * nunca comparten cubeta, así que se puede mezclar longitudes sin riesgo.
 */
export function construirGrafo(palabras) {
  const lista = [...new Set(palabras)].sort();
  const cubetas = new Map();
  for (const palabra of lista) {
    for (let i = 0; i < palabra.length; i++) {
      const patron = `${palabra.slice(0, i)}*${palabra.slice(i + 1)}`;
      let grupo = cubetas.get(patron);
      if (!grupo) cubetas.set(patron, (grupo = []));
      grupo.push(palabra);
    }
  }
  const grafo = new Map(lista.map((p) => [p, new Set()]));
  for (const grupo of cubetas.values()) {
    for (const a of grupo) {
      for (const b of grupo) {
        if (a !== b) grafo.get(a).add(b);
      }
    }
  }
  return new Map([...grafo].map(([p, v]) => [p, [...v].sort()]));
}

/** BFS de niveles: Map palabra → distancia mínima desde el origen. */
export function distanciasDesde(grafo, origen) {
  const dist = new Map();
  if (!grafo.has(origen)) return dist;
  dist.set(origen, 0);
  let frontera = [origen];
  while (frontera.length > 0) {
    const siguiente = [];
    for (const palabra of frontera) {
      for (const vecina of grafo.get(palabra)) {
        if (dist.has(vecina)) continue;
        dist.set(vecina, dist.get(palabra) + 1);
        siguiente.push(vecina);
      }
    }
    frontera = siguiente;
  }
  return dist;
}

/**
 * Camino mínimo origen→destino por BFS (incluye ambos extremos) o null si no
 * hay camino. Determinista: las vecinas se recorren en orden alfabético.
 */
export function caminoMinimo(grafo, origen, destino) {
  if (!grafo.has(origen) || !grafo.has(destino)) return null;
  if (origen === destino) return [origen];
  const previo = new Map([[origen, null]]);
  let frontera = [origen];
  while (frontera.length > 0) {
    const siguiente = [];
    for (const palabra of frontera) {
      for (const vecina of grafo.get(palabra)) {
        if (previo.has(vecina)) continue;
        previo.set(vecina, palabra);
        if (vecina === destino) {
          const camino = [];
          for (let p = destino; p !== null; p = previo.get(p)) camino.push(p);
          return camino.reverse();
        }
        siguiente.push(vecina);
      }
    }
    frontera = siguiente;
  }
  return null;
}

/**
 * Genera un reto determinista por semilla: par (origen, destino) a distancia
 * EXACTA de `pasos` movimientos. Devuelve también un camino mínimo (para la
 * pista y para rendirse). null si ningún par del diccionario está a esa
 * distancia.
 */
export function generarReto(palabras, { pasos = 4, semilla = 'reto' } = {}) {
  const grafo = construirGrafo(palabras);
  const rng = crearGeneradorNormalizado(semilla);
  const conVecinas = [...grafo.keys()].filter((p) => grafo.get(p).length > 0);
  const origenes = barajar(conVecinas, rng);
  for (const origen of origenes) {
    const dist = distanciasDesde(grafo, origen);
    const objetivos = [...dist.keys()].filter((p) => dist.get(p) === pasos).sort();
    if (objetivos.length === 0) continue;
    const destino = objetivos[Math.floor(rng() * objetivos.length)];
    return {
      origen,
      destino,
      pasos,
      camino: caminoMinimo(grafo, origen, destino),
    };
  }
  return null;
}

/**
 * ¿Es legal pasar de `actual` a `siguiente`? Debe ser palabra del diccionario
 * y estar a distancia Hamming 1. `diccionario` puede ser Set o array.
 */
export function esPasoValido(diccionario, actual, siguiente) {
  const existe = diccionario instanceof Set
    ? diccionario.has(siguiente)
    : diccionario.includes(siguiente);
  return existe && sonVecinas(actual, siguiente);
}

/** Métricas del grafo (para docs/métricas): nodos, aristas, componentes. */
export function estadisticas(grafo) {
  const nodos = grafo.size;
  let gradoTotal = 0;
  for (const vecinas of grafo.values()) gradoTotal += vecinas.length;

  const visitadas = new Set();
  const componentes = [];
  for (const palabra of grafo.keys()) {
    if (visitadas.has(palabra)) continue;
    let tam = 0;
    const pila = [palabra];
    visitadas.add(palabra);
    while (pila.length > 0) {
      const p = pila.pop();
      tam += 1;
      for (const v of grafo.get(p)) {
        if (!visitadas.has(v)) {
          visitadas.add(v);
          pila.push(v);
        }
      }
    }
    componentes.push(tam);
  }
  componentes.sort((a, b) => b - a);
  return {
    nodos,
    aristas: gradoTotal / 2,
    componentes,
    aisladas: componentes.filter((t) => t === 1).length,
  };
}
