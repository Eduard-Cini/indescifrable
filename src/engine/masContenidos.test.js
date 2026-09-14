import { describe, it, expect } from 'vitest';
import indice from '../data/mas/indice.json';

// Integridad del catálogo de «Más contenidos»: cada tema del índice tiene sus
// tres archivos (mazo, lección, ejercicios) y cada lección trae el resumen de
// lo que explica el libro (lo pidió el usuario).
const ARCHIVOS = import.meta.glob('../data/mas/*.json', { eager: true, import: 'default' });
const archivo = (nombre) => ARCHIVOS[`../data/mas/${nombre}.json`];

describe('indice.json', () => {
  it('declara los capítulos 9 y 10', () => {
    expect(indice.capitulos.map((c) => c.numero)).toEqual([9, 10]);
  });

  for (const cap of indice.capitulos) {
    for (const tema of cap.temas) {
      it(`capítulo ${cap.numero}, tema «${tema}»: mazo, lección y ejercicios`, () => {
        expect(archivo(`mazo-${tema}`)).toBeDefined();
        expect(archivo(`ejercicios-${tema}`)?.tema).toBe(tema);
        const leccion = archivo(`leccion-${tema}`);
        expect(leccion?.id).toBe(tema);
        expect(leccion.secciones.length).toBeGreaterThan(0);
        expect(leccion.libro?.referencia).toBeTruthy();
        expect(leccion.libro.puntos.length).toBeGreaterThan(0);
      });
    }

    it(`capítulo ${cap.numero}: mazos de vocabulario y de verbos`, () => {
      for (const id of cap.mazos) expect(archivo(`mazo-${id}`)?.id).toBe(id);
    });
  }

  it('no hay temas repetidos entre capítulos (los ids son rutas)', () => {
    const temas = indice.capitulos.flatMap((c) => [...c.temas, ...c.mazos]);
    expect(new Set(temas).size).toBe(temas.length);
  });
});
