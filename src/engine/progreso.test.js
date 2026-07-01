import { describe, it, expect } from 'vitest';
import {
  marcarCompletada,
  desmarcarCompletada,
  estaCompletada,
  contarCompletadas,
} from './progreso';

describe('progreso', () => {
  it('marca una lectura como completada sin duplicar', () => {
    let p = marcarCompletada([], 'mercado-01');
    p = marcarCompletada(p, 'mercado-01');
    expect(p).toEqual(['mercado-01']);
    expect(estaCompletada(p, 'mercado-01')).toBe(true);
  });

  it('desmarca una lectura', () => {
    const p = desmarcarCompletada(['a', 'b'], 'a');
    expect(p).toEqual(['b']);
  });

  it('cuenta cuántas de una lista están completadas', () => {
    expect(contarCompletadas(['a', 'c'], ['a', 'b', 'c'])).toBe(2);
  });

  it('no muta el arreglo original', () => {
    const orig = [];
    marcarCompletada(orig, 'x');
    expect(orig).toHaveLength(0);
  });
});
