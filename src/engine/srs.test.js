import { describe, it, expect } from 'vitest';
import {
  CALIFICACIONES,
  estadoInicial,
  calificar,
  estaPendiente,
  esRepasable,
  seleccionarSesion,
  aplicarCalificacion,
  resumen,
} from './srs';
import { crearEntrada } from './bolsa';

const T0 = '2026-01-01T00:00:00.000Z';

function entrada(surface, extra = {}) {
  return {
    ...crearEntrada({
      lang: 'de',
      surface,
      traducciones: { es: 'x' },
      addedAt: T0,
    }),
    ...extra,
  };
}

function diasEntre(isoA, isoB) {
  return (Date.parse(isoB) - Date.parse(isoA)) / (24 * 60 * 60 * 1000);
}

describe('calificar (recurrencia SM-2)', () => {
  it('sigue la serie de intervalos 1, 6, round(6·EF) con "bien"', () => {
    let s = calificar(undefined, CALIFICACIONES.bien, T0);
    expect(s.intervalo).toBe(1);
    expect(diasEntre(T0, s.vencimiento)).toBe(1);

    s = calificar(s, CALIFICACIONES.bien, T0);
    expect(s.intervalo).toBe(6);

    const efAntes = s.ef;
    s = calificar(s, CALIFICACIONES.bien, T0);
    // q=4 deja EF sin cambio: EF' = EF + 0.1 − 1·(0.08+0.02) = EF
    expect(s.ef).toBeCloseTo(efAntes);
    expect(s.intervalo).toBe(Math.round(6 * efAntes));
  });

  it('un fallo reinicia reps e intervalo y cuenta el lapso', () => {
    let s = calificar(undefined, CALIFICACIONES.bien, T0);
    s = calificar(s, CALIFICACIONES.bien, T0);
    s = calificar(s, CALIFICACIONES.otraVez, T0);
    expect(s.reps).toBe(0);
    expect(s.intervalo).toBe(0);
    expect(s.vencimiento).toBe(T0); // vuelve a la cola de la sesión
    expect(s.fallos).toBe(1);
    expect(s.repasos).toBe(3);
  });

  it('EF baja con "difícil", sube con "fácil" y tiene suelo 1.3', () => {
    const base = estadoInicial(T0);
    expect(calificar(base, CALIFICACIONES.dificil, T0).ef).toBeLessThan(base.ef);
    expect(calificar(base, CALIFICACIONES.facil, T0).ef).toBeGreaterThan(base.ef);

    let s = base;
    for (let i = 0; i < 20; i++) s = calificar(s, CALIFICACIONES.otraVez, T0);
    expect(s.ef).toBeCloseTo(1.3);
  });

  it('"difícil" también avanza el intervalo (q≥3 no es fallo)', () => {
    const s = calificar(undefined, CALIFICACIONES.dificil, T0);
    expect(s.reps).toBe(1);
    expect(s.intervalo).toBe(1);
    expect(s.fallos).toBe(0);
  });
});

describe('estaPendiente / esRepasable', () => {
  it('una palabra sin srs es nueva y está pendiente', () => {
    expect(estaPendiente(entrada('Frau'), T0)).toBe(true);
  });

  it('respeta el vencimiento', () => {
    const p = entrada('Frau', { srs: calificar(undefined, 4, T0) });
    expect(estaPendiente(p, T0)).toBe(false);
    expect(estaPendiente(p, '2026-01-02T00:00:00.000Z')).toBe(true);
  });

  it('sin traducción al español no es repasable', () => {
    const sin = { ...entrada('Und'), traducciones: {} };
    expect(esRepasable(sin)).toBe(false);
    expect(esRepasable(entrada('Frau'))).toBe(true);
  });
});

describe('seleccionarSesion', () => {
  it('ordena vencidas (más atrasada primero) y luego nuevas, sin futuras', () => {
    const vencidaVieja = entrada('alt', {
      srs: { ...estadoInicial(T0), vencimiento: '2025-12-20T00:00:00.000Z' },
    });
    const vencidaReciente = entrada('neu', {
      srs: { ...estadoInicial(T0), vencimiento: '2025-12-30T00:00:00.000Z' },
    });
    const futura = entrada('morgen', {
      srs: { ...estadoInicial(T0), vencimiento: '2026-02-01T00:00:00.000Z' },
    });
    const nueva = entrada('frisch');
    const sinTrad = { ...entrada('und'), traducciones: {} };

    const cola = seleccionarSesion(
      [nueva, futura, vencidaReciente, sinTrad, vencidaVieja],
      T0
    );
    expect(cola.map((p) => p.surface)).toEqual(['alt', 'neu', 'frisch']);
  });

  it('limita las nuevas con maxNuevas', () => {
    const bolsa = ['a', 'b', 'c'].map((s) => entrada(s));
    expect(seleccionarSesion(bolsa, T0, { maxNuevas: 2 })).toHaveLength(2);
  });
});

describe('aplicarCalificacion', () => {
  it('actualiza solo la entrada calificada y no muta la bolsa original', () => {
    const bolsa = [entrada('Frau'), entrada('Mann')];
    const nueva = aplicarCalificacion(bolsa, 'de:frau', CALIFICACIONES.bien, T0);
    expect(bolsa[0].srs).toBeUndefined();
    expect(nueva[0].srs.reps).toBe(1);
    expect(nueva[0].traducciones).toEqual({ es: 'x' });
    expect(nueva[1]).toBe(bolsa[1]);
  });
});

describe('resumen', () => {
  it('cuenta nuevas, vencidas, programadas y sin traducción', () => {
    const bolsa = [
      entrada('nueva'),
      entrada('vencida', {
        srs: { ...estadoInicial(T0), vencimiento: '2025-12-01T00:00:00.000Z' },
      }),
      entrada('futura', {
        srs: { ...estadoInicial(T0), vencimiento: '2026-03-01T00:00:00.000Z' },
      }),
      { ...entrada('sin'), traducciones: {} },
    ];
    expect(resumen(bolsa, T0)).toEqual({
      nuevas: 1,
      vencidas: 1,
      programadas: 1,
      sinTraduccion: 1,
    });
  });
});
