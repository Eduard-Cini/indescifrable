import { describe, it, expect } from 'vitest';
import {
  normalizar,
  clavePalabra,
  crearEntrada,
  agregarPalabra,
  quitarPalabra,
  tienePalabra,
  obtenerPalabra,
  contar,
} from './bolsa';

describe('normalizar', () => {
  it('pasa a minúsculas y recorta puntuación de los extremos', () => {
    expect(normalizar('  ¡Casa!  ')).toBe('casa');
    expect(normalizar('"Frau".')).toBe('frau');
  });
  it('conserva acentos y umlauts', () => {
    expect(normalizar('Äpfel')).toBe('äpfel');
    expect(normalizar('canción')).toBe('canción');
  });
});

describe('clavePalabra', () => {
  it('construye id idioma:forma', () => {
    expect(clavePalabra('de', 'Frau')).toBe('de:frau');
    expect(clavePalabra('es', 'Mujer')).toBe('es:mujer');
  });
});

describe('agregarPalabra', () => {
  const base = crearEntrada({
    lang: 'de',
    surface: 'Frau',
    traducciones: { es: 'mujer' },
    addedAt: '2026-01-01T00:00:00.000Z',
  });

  it('agrega una palabra nueva', () => {
    const bolsa = agregarPalabra([], base);
    expect(contar(bolsa)).toBe(1);
    expect(tienePalabra(bolsa, 'de:frau')).toBe(true);
  });

  it('conserva el estado de una palabra ya presente (no la reinicia)', () => {
    // entrada existente con estado SRS simulado
    const existente = { ...base, caja: 4, repasos: 10 };
    const duplicada = crearEntrada({
      lang: 'de',
      surface: 'Frau',
      traducciones: { es: 'mujer' },
      addedAt: '2026-09-09T00:00:00.000Z',
    });
    const bolsa = agregarPalabra([existente], duplicada);
    expect(contar(bolsa)).toBe(1);
    const guardada = obtenerPalabra(bolsa, 'de:frau');
    expect(guardada.caja).toBe(4); // estado intacto
    expect(guardada.addedAt).toBe('2026-01-01T00:00:00.000Z');
  });

  it('no muta la bolsa original', () => {
    const original = [];
    agregarPalabra(original, base);
    expect(original).toHaveLength(0);
  });
});

describe('quitarPalabra', () => {
  it('elimina por id', () => {
    const a = crearEntrada({ lang: 'de', surface: 'Frau', addedAt: 'x' });
    const b = crearEntrada({ lang: 'de', surface: 'Mann', addedAt: 'x' });
    const bolsa = quitarPalabra([a, b], 'de:frau');
    expect(contar(bolsa)).toBe(1);
    expect(tienePalabra(bolsa, 'de:frau')).toBe(false);
  });
});
