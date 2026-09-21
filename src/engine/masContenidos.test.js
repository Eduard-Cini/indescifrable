import { describe, it, expect } from 'vitest';
import indice from '../data/mas/indice.json';

// Integridad del catálogo de «Más contenidos»: cada tema del índice tiene su
// lección (con el resumen de lo que explica el libro) y sus ejercicios, cada
// capítulo tiene sus mazos de vocabulario y de verbos, y las fichas que
// enlaza una lección existen.
const ARCHIVOS = import.meta.glob('../data/mas/*.json', { eager: true, import: 'default' });
const archivo = (nombre) => ARCHIVOS[`../data/mas/${nombre}.json`];

describe('indice.json', () => {
  it('declara los capítulos 8, 9 y 10', () => {
    expect(indice.capitulos.map((c) => c.numero)).toEqual([8, 9, 10]);
  });

  for (const cap of indice.capitulos) {
    for (const tema of cap.temas) {
      it(`capítulo ${cap.numero}, tema «${tema}»: lección y ejercicios`, () => {
        expect(archivo(`ejercicios-${tema}`)?.tema).toBe(tema);
        const leccion = archivo(`leccion-${tema}`);
        expect(leccion?.id).toBe(tema);
        expect(leccion.secciones.length).toBeGreaterThan(0);
        expect(leccion.libro?.referencia).toBeTruthy();
        expect(leccion.libro.puntos.length).toBeGreaterThan(0);
        // Si la lección enlaza fichas, el mazo tiene que existir.
        if (leccion.mazo) expect(archivo(`mazo-${leccion.mazo}`)?.id).toBe(leccion.mazo);
      });
    }

    it(`capítulo ${cap.numero}: mazos de vocabulario y de verbos`, () => {
      expect(cap.mazos).toEqual([`k${cap.numero}-vocabulario`, `k${cap.numero}-verbos`]);
      for (const id of cap.mazos) expect(archivo(`mazo-${id}`)?.id).toBe(id);
    });

    it(`capítulo ${cap.numero}: el mazo de verbos solo tiene verbos`, () => {
      const verbos = archivo(`mazo-k${cap.numero}-verbos`);
      expect(verbos.tarjetas.every((t) => t.tipo === 'verbo')).toBe(true);
      expect(verbos.tarjetas.length).toBeGreaterThan(20);
    });
  }

  it('no hay ids repetidos entre capítulos (los ids son rutas)', () => {
    const ids = indice.capitulos.flatMap((c) => [...c.temas, ...c.mazos]);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
