import { describe, it, expect } from 'vitest';
import {
  poolDe,
  pasosDisponibles,
  longitudesEscalera,
  longitudesWordle,
  tamanosTablero,
  juegosDisponibles,
  lecturasOrdenadas,
  MIN_WORDLE,
  MIN_TABLERO,
  SLUG_CORPUS,
} from './juegos';
import juegos from '../data/juegos.json';

// Cadena aaa—aab—abb—bbb—bbc (distancias 1..4) más una palabra aislada.
const CADENA = { aaa: 'x', aab: 'x', abb: 'x', bbb: 'x', bbc: 'x', zzz: 'x' };
// Palabras sin vecinas: grafo sin aristas.
const SUELTAS = { abc: 'x', xyz: 'x', qqq: 'x' };

const glosas = (n) =>
  Object.fromEntries(Array.from({ length: n }, (_, i) => [`p${i}`, 'x']));

describe('poolDe', () => {
  it('corpus devuelve los pools globales', () => {
    const pool = poolDe(juegos, SLUG_CORPUS);
    expect(pool.titulo).toBe('Todo el corpus');
    expect(pool.escalera).toBe(juegos.escalera);
    expect(pool.crucigrama).toBe(juegos.crucigrama);
  });

  it('encuentra una lectura por slug y devuelve null si no existe', () => {
    const lectura = poolDe(juegos, juegos.lecturas[0].slug);
    expect(lectura).toBe(juegos.lecturas[0]);
    expect(poolDe(juegos, 'no-existe')).toBeNull();
  });
});

describe('pasosDisponibles', () => {
  it('devuelve solo las distancias que algún par alcanza', () => {
    // La cadena llega a distancia 4 (aaa→bbc): 3 y 4 sí; 5 y 6 no.
    expect(pasosDisponibles(Object.keys(CADENA))).toEqual([3, 4]);
  });

  it('grafo sin aristas → sin retos', () => {
    expect(pasosDisponibles(Object.keys(SUELTAS))).toEqual([]);
  });
});

describe('longitudes disponibles', () => {
  it('escalera exige un par a distancia >= 3 en la longitud', () => {
    expect(longitudesEscalera({ 3: CADENA, 4: SUELTAS })).toEqual(['3']);
  });

  it('wordle exige un mínimo de palabras', () => {
    const pocas = glosas(MIN_WORDLE - 1);
    const justas = glosas(MIN_WORDLE);
    expect(longitudesWordle({ 3: pocas, 4: justas })).toEqual(['4']);
  });
});

describe('tamanosTablero', () => {
  it('solo ofrece tamaños que el pool cubre', () => {
    expect(tamanosTablero(Array(7).fill({}))).toEqual([6]);
    expect(tamanosTablero(Array(30).fill({}))).toEqual([6, 8, 10]);
    expect(tamanosTablero([])).toEqual([]);
  });
});

describe('juegosDisponibles', () => {
  it('pool rico → los cuatro juegos', () => {
    const pool = poolDe(juegos, SLUG_CORPUS);
    expect(juegosDisponibles(pool)).toEqual(['escalera', 'crucigrama', 'wordle', 'sopa']);
  });

  it('pool pobre en grafo pero con pistas → tablero sí, escalera no', () => {
    const pool = {
      escalera: { 3: SUELTAS },
      crucigrama: Array(MIN_TABLERO).fill({ palabra: 'haus', pista: 'casa' }),
    };
    expect(juegosDisponibles(pool)).toEqual(['crucigrama', 'sopa']);
  });

  it('pool null o vacío → nada', () => {
    expect(juegosDisponibles(null)).toEqual([]);
    expect(juegosDisponibles({ escalera: {}, crucigrama: [] })).toEqual([]);
  });

  it('toda lectura real ofrece al menos un juego', () => {
    for (const lectura of juegos.lecturas) {
      expect(
        juegosDisponibles(lectura).length,
        `lectura ${lectura.slug}`
      ).toBeGreaterThan(0);
    }
  });

  it('los libros (avanzado) ofrecen los cuatro juegos', () => {
    for (const lectura of juegos.lecturas.filter((l) => l.nivel === 'avanzado')) {
      expect(juegosDisponibles(lectura)).toEqual(['escalera', 'crucigrama', 'wordle', 'sopa']);
    }
  });
});

describe('lecturasOrdenadas', () => {
  it('ordena por nivel ascendente y título', () => {
    const orden = lecturasOrdenadas(juegos).map((l) => l.nivel);
    const pesos = { principiante: 0, intermedio: 1, avanzado: 2 };
    for (let i = 1; i < orden.length; i++) {
      expect(pesos[orden[i - 1]]).toBeLessThanOrEqual(pesos[orden[i]]);
    }
  });
});
