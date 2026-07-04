import { describe, it, expect } from 'vitest';
import {
  sonVecinas,
  construirGrafo,
  distanciasDesde,
  caminoMinimo,
  generarReto,
  esPasoValido,
  estadisticas,
} from './escalera';
import juegosPorIdioma from '../data/juegos.json';
const juegos = juegosPorIdioma.de;

// Cadena aaa—aab—abb—bbb más una rama (aba) y una isla (zzz).
const DICCIONARIO = ['aaa', 'aab', 'abb', 'bbb', 'aba', 'zzz'];

describe('sonVecinas', () => {
  it('detecta exactamente una letra de diferencia', () => {
    expect(sonVecinas('haus', 'maus')).toBe(true);
    expect(sonVecinas('haus', 'maut')).toBe(false); // dos posiciones
    expect(sonVecinas('haus', 'haus')).toBe(false); // idénticas
    expect(sonVecinas('haus', 'hause')).toBe(false); // longitud distinta
  });
});

describe('construirGrafo', () => {
  const grafo = construirGrafo(DICCIONARIO);

  it('une solo palabras a distancia Hamming 1', () => {
    expect(grafo.get('aaa')).toEqual(['aab', 'aba']);
    expect(grafo.get('abb')).toEqual(['aab', 'aba', 'bbb']);
    expect(grafo.get('zzz')).toEqual([]);
  });

  it('es simétrico', () => {
    for (const [palabra, vecinas] of grafo) {
      for (const v of vecinas) expect(grafo.get(v)).toContain(palabra);
    }
  });

  it('deduplica el diccionario de entrada', () => {
    expect(construirGrafo(['aaa', 'aaa', 'aab']).size).toBe(2);
  });
});

describe('caminoMinimo y distanciasDesde', () => {
  const grafo = construirGrafo(DICCIONARIO);

  it('encuentra el camino más corto', () => {
    expect(caminoMinimo(grafo, 'aaa', 'bbb')).toEqual(['aaa', 'aab', 'abb', 'bbb']);
  });

  it('devuelve null si no hay camino', () => {
    expect(caminoMinimo(grafo, 'aaa', 'zzz')).toBeNull();
  });

  it('origen igual a destino → camino de un solo nodo', () => {
    expect(caminoMinimo(grafo, 'aaa', 'aaa')).toEqual(['aaa']);
  });

  it('las distancias BFS coinciden con la longitud del camino', () => {
    const dist = distanciasDesde(grafo, 'aaa');
    expect(dist.get('bbb')).toBe(3);
    expect(dist.get('aba')).toBe(1);
    expect(dist.has('zzz')).toBe(false);
  });
});

describe('generarReto', () => {
  it('el par generado está a la distancia exacta pedida', () => {
    const reto = generarReto(DICCIONARIO, { pasos: 3, semilla: 'S1' });
    expect(reto).not.toBeNull();
    expect(reto.camino).toHaveLength(reto.pasos + 1);
    expect(reto.camino[0]).toBe(reto.origen);
    expect(reto.camino.at(-1)).toBe(reto.destino);
  });

  it('es determinista para una misma semilla', () => {
    const a = generarReto(DICCIONARIO, { pasos: 2, semilla: 'X' });
    const b = generarReto(DICCIONARIO, { pasos: 2, semilla: 'X' });
    expect(a).toEqual(b);
  });

  it('varía con la semilla', () => {
    const retos = ['a', 'b', 'c', 'd', 'e', 'f'].map((s) =>
      JSON.stringify(generarReto(DICCIONARIO, { pasos: 2, semilla: s }))
    );
    expect(new Set(retos).size).toBeGreaterThan(1);
  });

  it('devuelve null si nadie está a esa distancia', () => {
    expect(generarReto(DICCIONARIO, { pasos: 9, semilla: 'S' })).toBeNull();
  });

  it('funciona sobre el diccionario real de cada longitud', () => {
    for (const L of ['3', '4', '5']) {
      const palabras = Object.keys(juegos.escalera[L]);
      const reto = generarReto(palabras, { pasos: 4, semilla: 'DEMO' });
      expect(reto, `longitud ${L}`).not.toBeNull();
      expect(reto.camino).toHaveLength(5);
    }
  });
});

describe('esPasoValido', () => {
  const dic = new Set(DICCIONARIO);

  it('exige palabra del diccionario a distancia 1', () => {
    expect(esPasoValido(dic, 'aaa', 'aab')).toBe(true);
    expect(esPasoValido(dic, 'aaa', 'abb')).toBe(false); // distancia 2
    expect(esPasoValido(dic, 'aaa', 'aac')).toBe(false); // no está en el diccionario
  });

  it('acepta también un array como diccionario', () => {
    expect(esPasoValido(DICCIONARIO, 'aaa', 'aba')).toBe(true);
  });
});

describe('estadisticas', () => {
  it('cuenta nodos, aristas y componentes', () => {
    const { nodos, aristas, componentes, aisladas } = estadisticas(construirGrafo(DICCIONARIO));
    expect(nodos).toBe(6);
    // aristas: aaa–aab, aaa–aba, aab–abb, aba–abb, abb–bbb
    expect(aristas).toBe(5);
    expect(componentes).toEqual([5, 1]);
    expect(aisladas).toBe(1);
  });
});
