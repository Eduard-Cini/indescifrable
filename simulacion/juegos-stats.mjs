// simulacion/juegos-stats.mjs
// Estadísticas de la Sección 4 (Juegos) ejecutando los motores REALES:
//
//   node simulacion/juegos-stats.mjs      (o `npm run simular-juegos`)
//   → escribe docs/datos-juegos.json (lo consume generar_metricas_seccion4.py)
//
// Escalera: para cada longitud de palabra, propiedades del grafo de Hamming 1
// (nodos, aristas, componentes, diámetro de la componente gigante y
// distribución de distancias entre pares alcanzables) — determinan qué retos
// existen a cada número de pasos.
//
// Crucigrama: para cada tamaño n, un barrido de semillas mide la tasa de
// éxito del backtracking (¿colocó las n palabras?), la densidad y los cruces
// del tablero resultante y el tiempo medio de generación.
//
// Wordle: por longitud, el mejor primer intento (argmax de la entropía de
// Shannon de la partición que induce) y el rendimiento de un solver voraz
// por entropía jugando contra TODOS los secretos posibles (distribución de
// intentos, media, % resuelto en ≤ 6).
//
// Sopa: barrido de semillas midiendo cuántas de las n palabras pedidas
// se colocan (la colocación aleatorizada no garantiza n; el crucigrama sí).

import { writeFileSync } from 'node:fs';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { performance } from 'node:perf_hooks';
import {
  construirGrafo,
  distanciasDesde,
  estadisticas,
  generarReto,
} from '../src/engine/escalera.js';
import { generarCrucigrama, metricas } from '../src/engine/crucigrama.js';
import {
  evaluar,
  esVictoria,
  filtrarConsistentes,
  mejorIntento,
} from '../src/engine/wordle.js';
import { generarSopa } from '../src/engine/sopa.js';
import { juegosDisponibles, lecturasOrdenadas } from '../src/engine/juegos.js';

const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));
const SALIDA = join(RAIZ, 'docs', 'datos-juegos.json');
const juegos = JSON.parse(
  readFileSync(join(RAIZ, 'src', 'data', 'juegos.json'), 'utf-8')
);

const SEMILLAS_CRUCI = 200;
const TAMANOS_CRUCI = [6, 8, 10];
const PASOS_RETO = [3, 4, 5, 6];

// --- Escalera ---------------------------------------------------------------
const escalera = {};
for (const [longitud, glosas] of Object.entries(juegos.escalera)) {
  const palabras = Object.keys(glosas);
  const grafo = construirGrafo(palabras);
  const st = estadisticas(grafo);

  // Distribución de distancias y diámetro, restringidos a la componente
  // gigante (BFS desde cada nodo: |V|·O(V+E), sobra para ~500 nodos).
  const porDistancia = {};
  let diametro = 0;
  let sumaDist = 0;
  let paresAlcanzables = 0;
  for (const origen of grafo.keys()) {
    const dist = distanciasDesde(grafo, origen);
    for (const [destino, d] of dist) {
      if (destino <= origen || d === 0) continue; // cada par una vez
      porDistancia[d] = (porDistancia[d] ?? 0) + 1;
      diametro = Math.max(diametro, d);
      sumaDist += d;
      paresAlcanzables += 1;
    }
  }

  // ¿Existe reto a cada nº de pasos? (lo que ofrece el selector de la UI)
  const retos = {};
  for (const pasos of PASOS_RETO) {
    retos[pasos] = generarReto(palabras, { pasos, semilla: 'STATS' }) !== null;
  }

  escalera[longitud] = {
    nodos: st.nodos,
    aristas: st.aristas,
    aisladas: st.aisladas,
    numComponentes: st.componentes.length,
    mayoresComponentes: st.componentes.slice(0, 5),
    diametro,
    distanciaMedia: +(sumaDist / paresAlcanzables).toFixed(2),
    paresAlcanzables,
    paresPorDistancia: porDistancia,
    hayRetoConPasos: retos,
  };
}

// --- Crucigrama ---------------------------------------------------------------
const crucigrama = {};
for (const n of TAMANOS_CRUCI) {
  let colocadasTotal = 0;
  let exitos = 0;
  let densidadTotal = 0;
  let crucesTotal = 0;
  let casillasTotal = 0;
  const t0 = performance.now();
  for (let i = 0; i < SEMILLAS_CRUCI; i++) {
    const cruci = generarCrucigrama(juegos.crucigrama, { n, semilla: `S${i}` });
    const m = metricas(cruci);
    colocadasTotal += m.palabras;
    if (m.palabras === n) exitos += 1;
    densidadTotal += m.densidad;
    crucesTotal += m.cruces;
    casillasTotal += m.casillas;
  }
  const ms = performance.now() - t0;
  crucigrama[n] = {
    semillas: SEMILLAS_CRUCI,
    tasaExito: +(exitos / SEMILLAS_CRUCI).toFixed(4),
    palabrasMedias: +(colocadasTotal / SEMILLAS_CRUCI).toFixed(2),
    densidadMedia: +(densidadTotal / SEMILLAS_CRUCI).toFixed(3),
    crucesMedios: +(crucesTotal / SEMILLAS_CRUCI).toFixed(2),
    casillasMedias: +(casillasTotal / SEMILLAS_CRUCI).toFixed(1),
    msPorTablero: +(ms / SEMILLAS_CRUCI).toFixed(2),
  };
}

// --- Wordle -------------------------------------------------------------------
// Solver voraz: primer intento fijo (mejor entropía global) y después el
// intento de mayor entropía ENTRE las candidatas consistentes.
function resolver(secreto, primero, palabras) {
  let candidatas = palabras;
  let intento = primero;
  for (let turno = 1; turno <= 15; turno++) {
    const resultado = evaluar(secreto, intento);
    if (esVictoria(resultado)) return turno;
    candidatas = filtrarConsistentes(candidatas, [{ intento, resultado }]);
    intento = mejorIntento(candidatas, candidatas).intento;
  }
  return Infinity; // no ocurre: las candidatas se estrictamente reducen
}

const wordle = {};
for (const longitud of ['4', '5']) {
  const palabras = Object.keys(juegos.escalera[longitud]);
  const t0 = performance.now();
  const primero = mejorIntento(palabras);
  const distribucion = {};
  let suma = 0;
  for (const secreto of palabras) {
    const turnos = resolver(secreto, primero.intento, palabras);
    distribucion[turnos] = (distribucion[turnos] ?? 0) + 1;
    suma += turnos;
  }
  const ms = performance.now() - t0;
  const resueltosEn6 = Object.entries(distribucion)
    .filter(([t]) => Number(t) <= 6)
    .reduce((acc, [, cnt]) => acc + cnt, 0);
  wordle[longitud] = {
    palabras: palabras.length,
    mejorPrimerIntento: primero.intento,
    entropiaPrimerIntento: +primero.entropia.toFixed(3),
    entropiaMaxima: +Math.log2(palabras.length).toFixed(3),
    intentosMedios: +(suma / palabras.length).toFixed(3),
    resueltosEnSeis: +(resueltosEn6 / palabras.length).toFixed(4),
    distribucion,
    msTotal: +ms.toFixed(0),
  };
}

// --- Sopa -----------------------------------------------------------------------
const sopa = {};
for (const n of TAMANOS_CRUCI) {
  let colocadasTotal = 0;
  let completas = 0;
  for (let i = 0; i < SEMILLAS_CRUCI; i++) {
    const s = generarSopa(juegos.crucigrama, { n, filas: 12, columnas: 12, semilla: `S${i}` });
    colocadasTotal += s.palabras.length;
    if (s.palabras.length === n) completas += 1;
  }
  sopa[n] = {
    semillas: SEMILLAS_CRUCI,
    tasaCompleta: +(completas / SEMILLAS_CRUCI).toFixed(4),
    palabrasMedias: +(colocadasTotal / SEMILLAS_CRUCI).toFixed(2),
  };
}

// --- Disponibilidad por lectura (los criterios de engine/juegos.js) -----------
const lecturas = lecturasOrdenadas(juegos).map((lectura) => ({
  titulo: lectura.titulo,
  nivel: lectura.nivel,
  palabrasPorLongitud: Object.fromEntries(
    Object.entries(lectura.escalera).map(([L, d]) => [L, Object.keys(d).length])
  ),
  entradasCrucigrama: lectura.crucigrama.length,
  disponibles: juegosDisponibles(lectura),
}));

const salida = {
  generado: new Date().toISOString().slice(0, 10),
  entradasCrucigrama: juegos.crucigrama.length,
  escalera,
  crucigrama,
  wordle,
  sopa,
  lecturas,
};
writeFileSync(SALIDA, JSON.stringify(salida, null, 1) + '\n');

for (const [L, e] of Object.entries(escalera)) {
  console.log(
    `escalera L=${L}: ${e.nodos} nodos, ${e.aristas} aristas, ` +
      `gigante=${e.mayoresComponentes[0]}, diámetro=${e.diametro}, media=${e.distanciaMedia}`
  );
}
for (const [n, c] of Object.entries(crucigrama)) {
  console.log(
    `crucigrama n=${n}: éxito=${(c.tasaExito * 100).toFixed(1)}%, ` +
      `densidad=${c.densidadMedia}, cruces=${c.crucesMedios}, ${c.msPorTablero} ms/tablero`
  );
}
for (const [L, w] of Object.entries(wordle)) {
  console.log(
    `wordle L=${L}: mejor 1er intento «${w.mejorPrimerIntento}» ` +
      `(${w.entropiaPrimerIntento}/${w.entropiaMaxima} bits), ` +
      `media=${w.intentosMedios} intentos, ≤6: ${(w.resueltosEnSeis * 100).toFixed(1)}%`
  );
}
for (const [n, s] of Object.entries(sopa)) {
  console.log(`sopa n=${n}: completa=${(s.tasaCompleta * 100).toFixed(1)}%, medias=${s.palabrasMedias}`);
}
for (const l of lecturas) {
  console.log(`  ${l.nivel.padEnd(12)} ${l.titulo.padEnd(28)} → ${l.disponibles.join(', ')}`);
}
console.log(`-> ${SALIDA}`);
