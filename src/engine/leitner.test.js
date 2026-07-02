import { describe, it, expect } from 'vitest';
import {
  NUM_CAJAS,
  INTERVALOS_CAJA,
  estadoInicialLeitner,
  calificarLeitner,
  estaPendienteLeitner,
  matrizTransicion,
  distribucionEstacionaria,
  repasosHastaUltimaCaja,
  diasHastaUltimaCaja,
  tasaRepasosEstacionaria,
} from './leitner';

const T0 = '2026-01-01T00:00:00.000Z';
const DIA = 24 * 60 * 60 * 1000;

describe('calificarLeitner', () => {
  it('sube de caja al acertar, con techo en la 5', () => {
    let e = estadoInicialLeitner(T0);
    for (let i = 2; i <= NUM_CAJAS; i++) {
      e = calificarLeitner(e, true, T0);
      expect(e.caja).toBe(i);
      expect(Date.parse(e.vencimiento)).toBe(
        Date.parse(T0) + INTERVALOS_CAJA[i - 1] * DIA
      );
    }
    e = calificarLeitner(e, true, T0);
    expect(e.caja).toBe(NUM_CAJAS); // techo
    expect(e.repasos).toBe(5);
  });

  it('al fallar vuelve a la caja 1 y cuenta el fallo', () => {
    let e = estadoInicialLeitner(T0);
    e = calificarLeitner(e, true, T0);
    e = calificarLeitner(e, true, T0);
    e = calificarLeitner(e, false, T0);
    expect(e.caja).toBe(1);
    expect(e.fallos).toBe(1);
    expect(Date.parse(e.vencimiento)).toBe(Date.parse(T0) + 1 * DIA);
  });

  it('estaPendienteLeitner respeta el vencimiento', () => {
    const e = calificarLeitner(undefined, true, T0); // caja 2, vence en 2 días
    expect(estaPendienteLeitner(e, T0)).toBe(false);
    expect(estaPendienteLeitner(e, '2026-01-03T00:00:00.000Z')).toBe(true);
  });
});

describe('cadena de Markov', () => {
  it('las filas de la matriz de transición suman 1', () => {
    for (const p of [0.5, 0.8, 0.95]) {
      for (const fila of matrizTransicion(p)) {
        expect(fila.reduce((s, x) => s + x, 0)).toBeCloseTo(1);
      }
    }
  });

  it('la distribución estacionaria suma 1 y satisface π = πP', () => {
    const P = matrizTransicion(0.9);
    const pi = distribucionEstacionaria(P);
    expect(pi.reduce((s, x) => s + x, 0)).toBeCloseTo(1);
    for (let j = 0; j < NUM_CAJAS; j++) {
      const pj = pi.reduce((s, x, i) => s + x * P[i][j], 0);
      expect(pj).toBeCloseTo(pi[j], 10);
    }
  });

  it('con p=1 todo converge a la caja 5 y se repasa cada 16 días', () => {
    const pi = distribucionEstacionaria(matrizTransicion(1));
    expect(pi[NUM_CAJAS - 1]).toBeCloseTo(1);
    expect(tasaRepasosEstacionaria(1)).toBeCloseTo(1 / 16);
  });

  it('repasos hasta la caja 5: 4 con p=1 y Σ p^(−j) en general', () => {
    expect(repasosHastaUltimaCaja(1)).toBeCloseTo(4);
    const p = 0.9;
    const esperado = 1 / p + 1 / p ** 2 + 1 / p ** 3 + 1 / p ** 4;
    expect(repasosHastaUltimaCaja(p)).toBeCloseTo(esperado);
  });

  it('días hasta la caja 5: 1+2+4+8 = 15 con p=1, y crece al bajar p', () => {
    expect(diasHastaUltimaCaja(1)).toBeCloseTo(15);
    expect(diasHastaUltimaCaja(0.8)).toBeGreaterThan(diasHastaUltimaCaja(0.95));
  });

  it('la tasa de repasos estacionaria crece al bajar p (más fallos, más trabajo)', () => {
    expect(tasaRepasosEstacionaria(0.7)).toBeGreaterThan(tasaRepasosEstacionaria(0.95));
  });
});
