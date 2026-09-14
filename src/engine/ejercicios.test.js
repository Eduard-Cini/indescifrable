import { describe, it, expect } from 'vitest';
import {
  trozos,
  numHuecos,
  segmentos,
  rellenar,
  problemasDeEjercicio,
  claveTanda,
} from './ejercicios';
import { opcionesDe, esCorrecta } from './gramatica';

// Todos los bancos de ejercicios reales de «Más contenidos».
const BANCOS = Object.values(
  import.meta.glob('../data/mas/ejercicios-*.json', { eager: true, import: 'default' })
);

const ej = {
  id: 'x1',
  partes: ['Am Montag ', ' der Raum ', '.'],
  respuesta: 'wird … aufgeräumt',
  distractores: ['werden … aufgeräumt', 'hat … aufgeräumt'],
};

describe('huecos', () => {
  it('parte una opción en sus trozos', () => {
    expect(trozos('wird … aufgeräumt')).toEqual(['wird', 'aufgeräumt']);
    expect(trozos('wurde')).toEqual(['wurde']);
  });

  it('cuenta los huecos (0 si la opción es una frase completa)', () => {
    expect(numHuecos(ej)).toBe(2);
    expect(numHuecos({ partes: null })).toBe(0);
  });

  it('rellena la frase con la opción elegida (verbo partido en dos huecos)', () => {
    expect(rellenar(ej, ej.respuesta)).toBe('Am Montag wird der Raum aufgeräumt.');
    expect(rellenar({ partes: null }, 'Frase completa.')).toBe('Frase completa.');
  });

  it('sin opción deja los huecos vacíos y omite los textos vacíos', () => {
    expect(segmentos({ partes: ['verteilen → ', ''] })).toEqual([
      { texto: 'verteilen → ' },
      { hueco: null },
    ]);
    expect(segmentos(ej, ej.respuesta).filter((s) => 'hueco' in s)).toEqual([
      { hueco: 'wird' },
      { hueco: 'aufgeräumt' },
    ]);
  });
});

describe('problemasDeEjercicio', () => {
  it('acepta un ejercicio coherente', () => {
    expect(problemasDeEjercicio(ej)).toEqual([]);
  });

  it('detecta la respuesta entre los distractores y opciones con otro número de huecos', () => {
    expect(problemasDeEjercicio({ ...ej, distractores: ['wird … aufgeräumt'] })).toContain(
      'la respuesta está entre los distractores'
    );
    expect(problemasDeEjercicio({ ...ej, distractores: ['wird'] }).join()).toMatch(/no rellena 2/);
  });

  it('un ejercicio de frase completa necesita pregunta', () => {
    expect(
      problemasDeEjercicio({ id: 'y', partes: null, respuesta: 'A.', distractores: ['B.'] })
    ).toContain('pregunta');
  });
});

describe('bancos reales de ejercicios', () => {
  it('hay bancos cargados', () => {
    expect(BANCOS.length).toBeGreaterThanOrEqual(6);
  });

  for (const banco of BANCOS) {
    it(`«${banco.tema}»: título, ejercicios coherentes e ids únicos`, () => {
      expect(banco.titulo).toBeTruthy();
      const todos = banco.tandas.flatMap((t) => t.ejercicios);
      const malos = todos
        .map((e) => [e.id, problemasDeEjercicio(e)])
        .filter(([, p]) => p.length > 0);
      expect(malos).toEqual([]);
      const idsEj = todos.map((e) => e.id);
      expect(new Set(idsEj).size).toBe(idsEj.length);
      const idsTanda = banco.tandas.map((t) => t.id);
      expect(new Set(idsTanda).size).toBe(idsTanda.length);
    });
  }

  it('las opciones se barajan de forma determinista y contienen la respuesta', () => {
    const e = BANCOS[0].tandas[0].ejercicios[0];
    const a = opcionesDe(e);
    expect(opcionesDe(e)).toEqual(a);
    expect(a).toContain(e.respuesta);
    expect(esCorrecta(e, e.respuesta)).toBe(true);
  });

  it('la clave de progreso de una tanda es estable', () => {
    expect(claveTanda('pasiva', 'modal')).toBe('pasiva|modal');
  });
});
