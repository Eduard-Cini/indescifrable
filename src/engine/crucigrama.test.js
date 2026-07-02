import { describe, it, expect } from 'vitest';
import {
  puedeColocar,
  colocacionesValidas,
  generarCrucigrama,
  cuadricula,
  metricas,
} from './crucigrama';
import juegos from '../data/juegos.json';

// Tablero de partida: «anna» en horizontal en la fila 0.
function tableroAnna() {
  const celdas = new Map();
  ['a', 'n', 'n', 'a'].forEach((letra, i) => celdas.set(`0,${i}`, letra));
  return celdas;
}

describe('puedeColocar', () => {
  it('acepta un cruce legal y cuenta sus cruces', () => {
    // «nein» vertical cruzando la primera n de «anna».
    expect(puedeColocar(tableroAnna(), 'nein', 0, 1, 'V')).toBe(1);
  });

  it('rechaza si la letra del cruce no coincide', () => {
    expect(puedeColocar(tableroAnna(), 'oder', 0, 1, 'V')).toBe(-1);
  });

  it('rechaza el contacto lateral fuera de un cruce', () => {
    // «nein» vertical pegada en paralelo justo debajo: n en (1,0) toca la a de (0,0)…
    // su primera letra queda adyacente a la fila de «anna» sin cruzarla.
    expect(puedeColocar(tableroAnna(), 'nein', 1, 0, 'V')).toBe(-1);
  });

  it('rechaza si el extremo anterior o posterior está ocupado', () => {
    // «nna» horizontal a partir de (0,1): la casilla anterior (0,0) tiene la a.
    expect(puedeColocar(tableroAnna(), 'nna', 0, 1, 'H')).toBe(-1);
  });

  it('acepta en tablero vacío (0 cruces)', () => {
    expect(puedeColocar(new Map(), 'anna', 0, 0, 'H')).toBe(0);
  });
});

describe('colocacionesValidas', () => {
  it('solo devuelve colocaciones ancladas en un cruce', () => {
    const opciones = colocacionesValidas(tableroAnna(), 'nein');
    expect(opciones.length).toBeGreaterThan(0);
    for (const o of opciones) {
      expect(o.cruces).toBeGreaterThan(0);
      expect(puedeColocar(tableroAnna(), 'nein', o.fila, o.col, o.dir)).toBe(o.cruces);
    }
  });

  it('ordena de más a menos cruces', () => {
    const opciones = colocacionesValidas(tableroAnna(), 'nein');
    for (let i = 1; i < opciones.length; i++) {
      expect(opciones[i - 1].cruces).toBeGreaterThanOrEqual(opciones[i].cruces);
    }
  });
});

describe('generarCrucigrama', () => {
  const entradas = [
    { palabra: 'anna', pista: 'nombre' },
    { palabra: 'nein', pista: 'no' },
    { palabra: 'insel', pista: 'isla' },
    { palabra: 'esel', pista: 'burro' },
    { palabra: 'nase', pista: 'nariz' },
  ];

  it('coloca las n palabras pedidas cuando caben', () => {
    const cruci = generarCrucigrama(entradas, { n: 5, semilla: 'T' });
    expect(cruci.palabras).toHaveLength(5);
  });

  it('es determinista para una misma semilla', () => {
    expect(generarCrucigrama(entradas, { n: 4, semilla: 'X' })).toEqual(
      generarCrucigrama(entradas, { n: 4, semilla: 'X' })
    );
  });

  it('cada palabra tras la primera cruza el tablero: cruces ≥ palabras − 1', () => {
    const cruci = generarCrucigrama(entradas, { n: 5, semilla: 'T' });
    expect(metricas(cruci).cruces).toBeGreaterThanOrEqual(cruci.palabras.length - 1);
  });

  it('dos palabras nunca ponen letras distintas en la misma casilla', () => {
    const cruci = generarCrucigrama(entradas, { n: 5, semilla: 'T' });
    const letras = new Map();
    for (const p of cruci.palabras) {
      for (let i = 0; i < p.palabra.length; i++) {
        const pos = `${p.fila + (p.dir === 'V' ? i : 0)},${p.col + (p.dir === 'H' ? i : 0)}`;
        if (letras.has(pos)) expect(letras.get(pos)).toBe(p.palabra[i]);
        letras.set(pos, p.palabra[i]);
      }
    }
  });

  it('la numeración empieza en 1 y va en orden de lectura', () => {
    const cruci = generarCrucigrama(entradas, { n: 4, semilla: 'T' });
    const numeros = cruci.palabras.map((p) => p.numero);
    expect(Math.min(...numeros)).toBe(1);
    const porNumero = [...cruci.palabras].sort((a, b) => a.numero - b.numero);
    for (let i = 1; i < porNumero.length; i++) {
      const antes = porNumero[i - 1];
      const ahora = porNumero[i];
      if (antes.numero === ahora.numero) continue; // misma casilla inicial (H y V)
      expect(
        antes.fila < ahora.fila || (antes.fila === ahora.fila && antes.col <= ahora.col)
      ).toBe(true);
    }
  });

  it('las dimensiones abarcan exactamente las palabras', () => {
    const cruci = generarCrucigrama(entradas, { n: 5, semilla: 'T' });
    const grid = cuadricula(cruci);
    expect(grid).toHaveLength(cruci.filas);
    expect(grid[0]).toHaveLength(cruci.columnas);
    // ninguna fila/columna del borde vacía (recorte al mínimo)
    expect(grid[0].some(Boolean)).toBe(true);
    expect(grid.at(-1).some(Boolean)).toBe(true);
    expect(grid.some((f) => f[0])).toBe(true);
    expect(grid.some((f) => f.at(-1))).toBe(true);
  });

  it('sin entradas devuelve null', () => {
    expect(generarCrucigrama([], { n: 3 })).toBeNull();
  });

  it('funciona con el pool real del corpus', () => {
    const cruci = generarCrucigrama(juegos.crucigrama, { n: 8, semilla: 'DEMO' });
    expect(cruci.palabras).toHaveLength(8);
    const m = metricas(cruci);
    expect(m.cruces).toBeGreaterThanOrEqual(7);
    expect(m.densidad).toBeGreaterThan(0);
  });
});

describe('cuadricula y metricas', () => {
  it('coinciden en el caso mínimo de dos palabras cruzadas', () => {
    const cruci = generarCrucigrama(
      [
        { palabra: 'anna', pista: 'nombre' },
        { palabra: 'nein', pista: 'no' },
      ],
      { n: 2, semilla: 'M' }
    );
    const m = metricas(cruci);
    expect(m.palabras).toBe(2);
    expect(m.casillas).toBe(7); // 4 + 4 − 1 cruce
    expect(m.cruces).toBe(1);
  });
});
