// engine/leitner.js
// Sistema de Leitner (5 cajas) y su modelo como cadena de Markov.
//
// Dinámica: una palabra en la caja i se repasa cada I_i días
// (I = [1, 2, 4, 8, 16]); si acierta sube a la caja i+1 (la 5 es techo),
// si falla vuelve a la caja 1. Con probabilidad de acierto p constante,
// la sucesión de cajas es una cadena de Markov con matriz de transición
//   P[i][i+1] = p,  P[i][1] = 1−p   (y P[5][5] = p en el techo).
//
// De la cadena salen los resultados analíticos de la tesis (validados por
// la simulación de simulacion/comparar.mjs):
//  - distribución estacionaria π (dónde pasa sus repasos una palabra),
//  - repasos esperados hasta la caja 5: h_1 = Σ_{j=1..4} p^(−j)
//    (esperanza de la primera racha de 4 aciertos seguidos),
//  - días esperados hasta la caja 5 (misma recurrencia, ponderada por I_i),
//  - tasa de repasos en régimen: 1 / Σ_i π_i·I_i (repasos/día/palabra).
//
// Módulo puro con tiempo inyectado, igual que srs.js. En producción la UI
// usa SM-2; Leitner existe para la comparación matemática y la simulación.

const MS_POR_DIA = 24 * 60 * 60 * 1000;

export const NUM_CAJAS = 5;
export const INTERVALOS_CAJA = [1, 2, 4, 8, 16]; // días de espera por caja

function sumarDias(iso, dias) {
  return new Date(Date.parse(iso) + dias * MS_POR_DIA).toISOString();
}

/** Estado Leitner de una palabra recién incorporada (caja 1, vence ya). */
export function estadoInicialLeitner(ahora) {
  return { caja: 1, vencimiento: ahora, repasos: 0, fallos: 0 };
}

/** Aplica un repaso binario (correcto/incorrecto). Puro, no muta. */
export function calificarLeitner(estado, correcto, ahora) {
  const base = estado ?? estadoInicialLeitner(ahora);
  const caja = correcto ? Math.min(base.caja + 1, NUM_CAJAS) : 1;
  return {
    caja,
    vencimiento: sumarDias(ahora, INTERVALOS_CAJA[caja - 1]),
    repasos: base.repasos + 1,
    fallos: base.fallos + (correcto ? 0 : 1),
  };
}

export function estaPendienteLeitner(estado, ahora) {
  return Date.parse(estado.vencimiento) <= Date.parse(ahora);
}

// --- Cadena de Markov (p = probabilidad de acierto constante) --------------

/** Matriz de transición 5×5 (índices 0..4 = cajas 1..5). */
export function matrizTransicion(p) {
  const P = Array.from({ length: NUM_CAJAS }, () => Array(NUM_CAJAS).fill(0));
  for (let i = 0; i < NUM_CAJAS; i++) {
    const sube = Math.min(i + 1, NUM_CAJAS - 1);
    P[i][sube] += p;
    P[i][0] += 1 - p;
  }
  return P;
}

/** Distribución estacionaria π = πP por iteración de potencias. */
export function distribucionEstacionaria(P, iteraciones = 200) {
  let pi = Array(NUM_CAJAS).fill(1 / NUM_CAJAS);
  for (let k = 0; k < iteraciones; k++) {
    const sig = Array(NUM_CAJAS).fill(0);
    for (let i = 0; i < NUM_CAJAS; i++)
      for (let j = 0; j < NUM_CAJAS; j++) sig[j] += pi[i] * P[i][j];
    pi = sig;
  }
  return pi;
}

/**
 * Repasos esperados para llegar a la caja 5 desde la caja 1: la primera
 * racha de 4 aciertos seguidos, E = Σ_{j=1..4} p^(−j) (forma cerrada).
 */
export function repasosHastaUltimaCaja(p) {
  let e = 0;
  for (let j = 1; j < NUM_CAJAS; j++) e += p ** -j;
  return e;
}

/**
 * Días esperados para llegar a la caja 5 desde la caja 1. Recurrencia
 * d_i = I_i + p·d_{i+1} + (1−p)·d_1 con d_5 = 0: expresando cada d_i como
 * a_i + b_i·d_1 (sustitución hacia atrás) queda una ecuación en d_1.
 */
export function diasHastaUltimaCaja(p) {
  let a = 0; // d_{i+1} = a + b·d_1, empezando por d_5 = 0
  let b = 0;
  for (let i = NUM_CAJAS - 2; i >= 1; i--) {
    a = INTERVALOS_CAJA[i] + p * a;
    b = p * b + (1 - p);
  }
  // d_1 = I_1 + p·(a + b·d_1) + (1−p)·d_1
  return (INTERVALOS_CAJA[0] + p * a) / (1 - p * b - (1 - p));
}

/** Repasos/día/palabra en régimen estacionario: 1 / Σ π_i·I_i. */
export function tasaRepasosEstacionaria(p) {
  const pi = distribucionEstacionaria(matrizTransicion(p));
  const diasPorRepaso = pi.reduce((s, x, i) => s + x * INTERVALOS_CAJA[i], 0);
  return 1 / diasPorRepaso;
}
