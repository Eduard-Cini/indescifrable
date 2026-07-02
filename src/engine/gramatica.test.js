import { describe, it, expect } from 'vitest';
import {
  opcionesDe,
  esCorrecta,
  seleccionarSesion,
  resumenSesion,
} from './gramatica';

const ej = {
  id: 'demo#1',
  tema: 'declinacion',
  antes: 'El pan está caliente: ',
  respuesta: 'das',
  despues: ' Brot ist gut.',
  distractores: ['der', 'die', 'dem'],
  pista: 'nominativo · neutro singular',
};

describe('opcionesDe', () => {
  it('incluye la respuesta y todos los distractores', () => {
    const ops = opcionesDe(ej);
    expect(ops).toContain('das');
    expect(ops).toHaveLength(4);
    for (const d of ej.distractores) expect(ops).toContain(d);
  });

  it('es determinista para una misma semilla', () => {
    expect(opcionesDe(ej, 'x')).toEqual(opcionesDe(ej, 'x'));
  });

  it('varía el orden según la semilla', () => {
    // Con suficientes semillas distintas, al menos dos órdenes no coinciden.
    const ordenes = ['a', 'b', 'c', 'd', 'e'].map((s) => opcionesDe(ej, s).join(','));
    expect(new Set(ordenes).size).toBeGreaterThan(1);
  });

  it('deduplica si un distractor coincide con la respuesta', () => {
    const ops = opcionesDe({ ...ej, distractores: ['das', 'der'] });
    expect(ops.filter((o) => o === 'das')).toHaveLength(1);
    expect(ops).toHaveLength(2);
  });

  it('no falla si no hay distractores', () => {
    expect(opcionesDe({ id: 'z', respuesta: 'x' })).toEqual(['x']);
  });
});

describe('esCorrecta', () => {
  it('distingue respuesta de distractor', () => {
    expect(esCorrecta(ej, 'das')).toBe(true);
    expect(esCorrecta(ej, 'der')).toBe(false);
  });
});

describe('seleccionarSesion', () => {
  const banco = Array.from({ length: 25 }, (_, i) => ({ id: `e${i}`, respuesta: 'x' }));

  it('limita al tope n', () => {
    expect(seleccionarSesion(banco, { n: 10 })).toHaveLength(10);
  });

  it('no repite ejercicios', () => {
    const ids = seleccionarSesion(banco, { n: 10 }).map((e) => e.id);
    expect(new Set(ids).size).toBe(10);
  });

  it('es determinista por semilla y varía entre semillas', () => {
    const a = seleccionarSesion(banco, { n: 5, semilla: 's1' }).map((e) => e.id);
    const b = seleccionarSesion(banco, { n: 5, semilla: 's1' }).map((e) => e.id);
    const c = seleccionarSesion(banco, { n: 5, semilla: 's2' }).map((e) => e.id);
    expect(a).toEqual(b);
    expect(a).not.toEqual(c);
  });

  it('devuelve todo si n excede el banco, y [] si está vacío', () => {
    expect(seleccionarSesion(banco, { n: 999 })).toHaveLength(25);
    expect(seleccionarSesion([], { n: 5 })).toEqual([]);
  });
});

describe('resumenSesion', () => {
  it('cuenta aciertos, fallos y porcentaje', () => {
    expect(resumenSesion([true, true, false, true])).toEqual({
      total: 4,
      aciertos: 3,
      fallos: 1,
      porcentaje: 75,
    });
  });

  it('sesión vacía → 0% sin dividir por cero', () => {
    expect(resumenSesion([])).toEqual({ total: 0, aciertos: 0, fallos: 0, porcentaje: 0 });
  });
});
