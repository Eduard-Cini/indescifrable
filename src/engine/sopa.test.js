import { describe, it, expect } from 'vitest';
import { generarSopa, extraerPalabra, buscarSeleccion, casillasDe } from './sopa';
import juegos from '../data/juegos.json';

const ENTRADAS = [
  { palabra: 'haus', pista: 'casa' },
  { palabra: 'geschenk', pista: 'regalo' },
  { palabra: 'nase', pista: 'nariz' },
  { palabra: 'esel', pista: 'burro' },
  { palabra: 'sonne', pista: 'sol' },
  { palabra: 'hand', pista: 'mano' },
];

describe('generarSopa', () => {
  const sopa = generarSopa(ENTRADAS, { n: 5, filas: 10, columnas: 10, semilla: 'T' });

  it('coloca las palabras pedidas en una cuadrícula completa', () => {
    expect(sopa.palabras).toHaveLength(5);
    expect(sopa.cuadricula).toHaveLength(10);
    for (const fila of sopa.cuadricula) {
      expect(fila).toHaveLength(10);
      for (const letra of fila) expect(letra).toMatch(/^[a-zäöüß]$/);
    }
  });

  it('cada palabra colocada se lee en la cuadrícula en su posición', () => {
    for (const p of sopa.palabras) {
      const leida = casillasDe(p)
        .map((pos) => {
          const [f, c] = pos.split(',').map(Number);
          return sopa.cuadricula[f][c];
        })
        .join('');
      expect(leida).toBe(p.palabra);
    }
  });

  it('es determinista por semilla', () => {
    expect(generarSopa(ENTRADAS, { n: 5, semilla: 'X' })).toEqual(
      generarSopa(ENTRADAS, { n: 5, semilla: 'X' })
    );
  });

  it('varía con la semilla', () => {
    const sopas = ['a', 'b', 'c', 'd'].map((s) =>
      JSON.stringify(generarSopa(ENTRADAS, { n: 5, semilla: s }).cuadricula)
    );
    expect(new Set(sopas).size).toBeGreaterThan(1);
  });

  it('omite palabras que no caben', () => {
    const chica = generarSopa(
      [{ palabra: 'einunddreissig', pista: 'x' }, { palabra: 'haus', pista: 'casa' }],
      { n: 2, filas: 6, columnas: 6, semilla: 'T' }
    );
    expect(chica.palabras.map((p) => p.palabra)).toEqual(['haus']);
  });

  it('sin entradas devuelve null', () => {
    expect(generarSopa([], { n: 3 })).toBeNull();
  });

  it('funciona con el pool real del corpus', () => {
    const real = generarSopa(juegos.crucigrama, { n: 8, filas: 12, columnas: 12, semilla: 'DEMO' });
    expect(real.palabras).toHaveLength(8);
  });
});

describe('extraerPalabra', () => {
  const cuadricula = [
    ['h', 'a', 'u', 's'],
    ['x', 'n', 'y', 'z'],
    ['x', 'y', 'n', 'z'],
    ['q', 'q', 'q', 'a'],
  ];

  it('lee horizontal, vertical y diagonal', () => {
    expect(extraerPalabra(cuadricula, { fila: 0, col: 0 }, { fila: 0, col: 3 })).toBe('haus');
    expect(extraerPalabra(cuadricula, { fila: 0, col: 0 }, { fila: 3, col: 0 })).toBe('hxxq');
    expect(extraerPalabra(cuadricula, { fila: 0, col: 0 }, { fila: 3, col: 3 })).toBe('hnna');
  });

  it('lee también en sentido inverso', () => {
    expect(extraerPalabra(cuadricula, { fila: 0, col: 3 }, { fila: 0, col: 0 })).toBe('suah');
  });

  it('rechaza selecciones que no son línea recta o de una sola casilla', () => {
    expect(extraerPalabra(cuadricula, { fila: 0, col: 0 }, { fila: 1, col: 2 })).toBeNull();
    expect(extraerPalabra(cuadricula, { fila: 2, col: 2 }, { fila: 2, col: 2 })).toBeNull();
  });
});

describe('buscarSeleccion', () => {
  const sopa = generarSopa(ENTRADAS, { n: 5, filas: 10, columnas: 10, semilla: 'T' });
  const p = sopa.palabras[0];
  const L = p.palabra.length;
  const fin = { fila: p.fila + p.dF * (L - 1), col: p.col + p.dC * (L - 1) };

  it('encuentra una palabra seleccionada de inicio a fin', () => {
    expect(buscarSeleccion(sopa, { fila: p.fila, col: p.col }, fin)).toBe(p);
  });

  it('también seleccionada al revés (de fin a inicio)', () => {
    expect(buscarSeleccion(sopa, fin, { fila: p.fila, col: p.col })).toBe(p);
  });

  it('rechaza selecciones más cortas que la palabra', () => {
    if (L > 2) {
      const casiFin = { fila: p.fila + p.dF * (L - 2), col: p.col + p.dC * (L - 2) };
      expect(buscarSeleccion(sopa, { fila: p.fila, col: p.col }, casiFin)).toBeNull();
    }
  });
});
