// simulacion/comparar.mjs
// Comparación Leitner vs SM-2 por simulación con alumno sintético.
//
//   node simulacion/comparar.mjs      (o `npm run simular`)
//   → escribe docs/datos-simulacion.json (lo consume generar_metricas_repaso.py)
//
// Diseño:
//  - Alumno sintético con curva de olvido exponencial: P(recordar tras Δ días)
//    = e^(−Δ/S). Cada palabra tiene dificultad d y estabilidad inicial S0; al
//    acertar un repaso la estabilidad crece S ← S·g (g depende de d), al
//    fallar se contrae S ← max(S0, 0.3·S). Es el mismo modelo de olvido que
//    usa producción (engine/conocimiento.js) — la simulación y la app hablan
//    el mismo idioma matemático.
//  - Los DOS planificadores operan sobre los motores REALES del repo:
//    engine/srs.js (SM-2, el de producción) y engine/leitner.js (5 cajas).
//    El mismo alumno (mismos d, S0, g por palabra) se simula bajo cada uno.
//  - Contabilidad fiel a cada método: un fallo en SM-2 cuesta 2 presentaciones
//    (falla + reciclada en la sesión, como hace la UI); en Leitner cuesta 1
//    (baja a la caja 1 y espera). En ambos, tras el fallo el alumno ve la
//    respuesta: lastReview se actualiza sin bonus de estabilidad.
//  - Métrica diaria de retención: media sobre las palabras introducidas de
//    e^(−(hoy − últimoRepaso)/S) — probabilidad de recordarlas si se
//    preguntaran hoy ("probe", no gasta repasos).
//
// Además emite la solución analítica de Leitner como cadena de Markov
// (distribución estacionaria, repasos/días hasta la caja 5, tasa de repasos
// en régimen) para p de acierto constante, desde engine/leitner.js.

import { writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { calificar, CALIFICACIONES } from '../src/engine/srs.js';
import {
  calificarLeitner,
  estaPendienteLeitner,
  matrizTransicion,
  distribucionEstacionaria,
  repasosHastaUltimaCaja,
  diasHastaUltimaCaja,
  tasaRepasosEstacionaria,
  NUM_CAJAS,
} from '../src/engine/leitner.js';

const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));
const SALIDA = join(RAIZ, 'docs', 'datos-simulacion.json');

// --- Parámetros -------------------------------------------------------------
const SEED = 42;
const HORIZONTE = 150; // días simulados
const NUEVAS_POR_DIA = 8;
const DIAS_ALTA = 60; // se introducen palabras los primeros 60 días
const N = NUEVAS_POR_DIA * DIAS_ALTA; // 480 palabras
const T0 = Date.parse('2026-01-01T00:00:00.000Z');
const MS_POR_DIA = 24 * 60 * 60 * 1000;
const iso = (dia) => new Date(T0 + dia * MS_POR_DIA).toISOString();

// --- RNG determinista (mulberry32) ------------------------------------------
function mulberry32(semilla) {
  let a = semilla >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// --- Alumno sintético: parámetros por palabra (compartidos entre sistemas) --
// Calibración: con e^(−Δ/S), recordar al 90% exige S ≈ 9.5·Δ. Se eligen S0 y g
// para que el primer repaso (Δ = 1 día) ronde el 85-94% de acierto y el
// crecimiento por acierto (~×2.7 de media) acompañe la escalada de intervalos
// de SM-2 (×EF = 2.5) — precisión resultante ~80-90%, como en los SRS reales.
const rngAlumno = mulberry32(SEED);
const palabras = Array.from({ length: N }, (_, i) => {
  const dificultad = 0.3 + 0.6 * rngAlumno();
  return {
    diaAlta: Math.floor(i / NUEVAS_POR_DIA),
    dificultad,
    s0: 6 + 10 * rngAlumno(), // estabilidad inicial (días)
    g: 2.2 + (1 - dificultad) * 1.4, // crecimiento de S al acertar
  };
});

// --- Simulación de un planificador ------------------------------------------
// planificador: {
//   alta(dia) -> estado del planificador para una palabra recién estudiada,
//   pendiente(estado, dia) -> ¿toca repasarla hoy?,
//   repasar(estado, correcto, dia) -> [nuevoEstado, presentaciones],
//   madura(estado) -> ¿intervalo largo? (SM-2 ≥16 días ≡ caja 5 de Leitner)
// }
function simular(planificador, semilla) {
  const rng = mulberry32(semilla);
  const mem = palabras.map(() => null); // { s, ultimo } por palabra
  const plan = palabras.map(() => null);
  const serie = [];
  let totalPresentaciones = 0;
  let aciertos = 0;
  let repasosEvaluados = 0;

  for (let dia = 0; dia <= HORIZONTE; dia++) {
    let hoy = 0;
    for (let i = 0; i < N; i++) {
      const w = palabras[i];
      if (dia === w.diaAlta) {
        // Alta: primer estudio (cuenta 1 presentación), estabilidad S0.
        mem[i] = { s: w.s0, ultimo: dia };
        plan[i] = planificador.alta(dia);
        hoy += 1;
        continue;
      }
      if (!mem[i] || !planificador.pendiente(plan[i], dia)) continue;

      const delta = dia - mem[i].ultimo;
      const r = Math.exp(-delta / mem[i].s);
      const correcto = rng() < r;
      repasosEvaluados += 1;
      if (correcto) {
        aciertos += 1;
        mem[i].s *= w.g;
      } else {
        mem[i].s = Math.max(w.s0, 0.5 * mem[i].s);
      }
      mem[i].ultimo = dia; // en ambos casos vio la respuesta
      const [nuevo, presentaciones] = planificador.repasar(plan[i], correcto, dia);
      plan[i] = nuevo;
      hoy += presentaciones;
    }
    totalPresentaciones += hoy;

    // Probe de retención sobre las palabras ya introducidas.
    let suma = 0;
    let n = 0;
    let maduras = 0;
    for (let i = 0; i < N; i++) {
      if (!mem[i]) continue;
      suma += Math.exp(-(dia - mem[i].ultimo) / mem[i].s);
      n += 1;
      if (planificador.madura(plan[i])) maduras += 1;
    }
    serie.push({
      dia,
      repasos: hoy,
      retencion: n ? suma / n : 0,
      maduras,
    });
  }

  return {
    serie,
    totalPresentaciones,
    precisión: repasosEvaluados ? aciertos / repasosEvaluados : 0,
    retencionFinal: serie[serie.length - 1].retencion,
    madurasFinal: serie[serie.length - 1].maduras,
    estados: plan,
  };
}

// --- Los dos planificadores sobre los motores reales -------------------------
const planSm2 = {
  alta: (dia) => calificar(undefined, CALIFICACIONES.bien, iso(dia)),
  pendiente: (srs, dia) => Date.parse(srs.vencimiento) <= T0 + dia * MS_POR_DIA,
  repasar: (srs, correcto, dia) => {
    if (correcto) return [calificar(srs, CALIFICACIONES.bien, iso(dia)), 1];
    // Fallo: «otra vez» + reciclada en la misma sesión (2 presentaciones).
    const caida = calificar(srs, CALIFICACIONES.otraVez, iso(dia));
    return [calificar(caida, CALIFICACIONES.bien, iso(dia)), 2];
  },
  madura: (srs) => srs.intervalo >= 16,
};

const planLeitner = {
  // Alta: entra en la caja 1 con el primer repaso mañana (I_1 = 1 día).
  alta: (dia) => ({ caja: 1, vencimiento: iso(dia + 1), repasos: 0, fallos: 0 }),
  pendiente: (e, dia) => estaPendienteLeitner(e, iso(dia)),
  repasar: (e, correcto, dia) => [calificarLeitner(e, correcto, iso(dia)), 1],
  madura: (e) => e.caja === NUM_CAJAS,
};

console.log(`Simulando ${N} palabras, ${HORIZONTE} días, semilla ${SEED}…`);
const sm2 = simular(planSm2, SEED + 1);
const leitner = simular(planLeitner, SEED + 2);

// Distribuciones finales: intervalos SM-2 y cajas Leitner.
const histCajas = Array(NUM_CAJAS).fill(0);
for (const e of leitner.estados) histCajas[e.caja - 1] += 1;
const cortes = [1, 2, 6, 15, 30, 60, Infinity];
const histIntervalos = Array(cortes.length).fill(0);
for (const s of sm2.estados) {
  histIntervalos[cortes.findIndex((c) => s.intervalo <= c)] += 1;
}

// --- Analítica de Markov (Leitner con p constante) ---------------------------
const markov = [0.7, 0.8, 0.9, 0.95].map((p) => ({
  p,
  estacionaria: distribucionEstacionaria(matrizTransicion(p)).map((x) => +x.toFixed(4)),
  repasosHastaCaja5: +repasosHastaUltimaCaja(p).toFixed(2),
  diasHastaCaja5: +diasHastaUltimaCaja(p).toFixed(1),
  repasosPorDiaPalabra: +tasaRepasosEstacionaria(p).toFixed(4),
}));

const limpiar = ({ estados, ...resto }) => resto; // eslint-disable-line no-unused-vars
const datos = {
  parametros: {
    seed: SEED,
    horizonteDias: HORIZONTE,
    nuevasPorDia: NUEVAS_POR_DIA,
    diasDeAlta: DIAS_ALTA,
    palabras: N,
    modeloOlvido: 'P(recordar tras Δ) = exp(−Δ/S); acierto: S·g; fallo: max(S0, 0.5·S)',
    dificultad: 'd ~ U(0.3, 0.9); S0 ~ U(6, 16) días; g = 2.2 + (1−d)·1.4',
  },
  sm2: limpiar(sm2),
  leitner: limpiar(leitner),
  histCajasLeitner: histCajas,
  histIntervalosSm2: { cortes: cortes.slice(0, -1).concat('más'), conteos: histIntervalos },
  markov,
};

mkdirSync(join(RAIZ, 'docs'), { recursive: true });
writeFileSync(SALIDA, JSON.stringify(datos, null, 1));

const f = (x) => (100 * x).toFixed(1) + '%';
console.log(`
                        SM-2      Leitner
retención final         ${f(sm2.retencionFinal)}     ${f(leitner.retencionFinal)}
presentaciones totales  ${sm2.totalPresentaciones}     ${leitner.totalPresentaciones}
precisión en repasos    ${f(sm2.precisión)}     ${f(leitner.precisión)}
maduras al final        ${sm2.madurasFinal}       ${leitner.madurasFinal}
-> ${SALIDA}`);
