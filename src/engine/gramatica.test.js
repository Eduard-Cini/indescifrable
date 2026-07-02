import { describe, it, expect } from 'vitest';
import {
  opcionesDe,
  esCorrecta,
  seleccionarSesion,
  resumenSesion,
  slugDeLectura,
  agruparPorLectura,
  claveEjercicio,
  lecturaCompletada,
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

  it('presenta por dificultad ascendente y agrupado por lectura', () => {
    const mixto = [
      { id: 'a', nivel: 'avanzado', fuente: 'avanzado · Immensee' },
      { id: 'b', nivel: 'principiante', fuente: 'principiante · El mercado' },
      { id: 'c', nivel: 'intermedio', fuente: 'intermedio · Caperucita' },
      { id: 'd', nivel: 'principiante', fuente: 'principiante · Un día de Ana' },
      { id: 'e', nivel: 'intermedio', fuente: 'intermedio · Caperucita' },
      { id: 'f', nivel: 'principiante', fuente: 'principiante · El mercado' },
    ];
    const niveles = seleccionarSesion(mixto, { n: 6 }).map((e) => e.nivel);
    expect(niveles).toEqual([
      'principiante', 'principiante', 'principiante',
      'intermedio', 'intermedio', 'avanzado',
    ]);
    const fuentes = seleccionarSesion(mixto, { n: 6 }).map((e) => e.fuente);
    // Dentro de un nivel, los de la misma lectura quedan contiguos.
    expect(fuentes.slice(3, 5)).toEqual([
      'intermedio · Caperucita', 'intermedio · Caperucita',
    ]);
  });

  it('los ejercicios sin nivel van al final', () => {
    const mixto = [
      { id: 'x' },
      { id: 'y', nivel: 'avanzado', fuente: 'z' },
    ];
    expect(seleccionarSesion(mixto, { n: 2 }).map((e) => e.id)).toEqual(['y', 'x']);
  });
});

describe('slugDeLectura', () => {
  it('quita acentos y normaliza a kebab-case', () => {
    expect(slugDeLectura('Un día de Ana')).toBe('un-dia-de-ana');
    expect(slugDeLectura('La metamorfosis')).toBe('la-metamorfosis');
    expect(slugDeLectura('  ¡El león y el ratón!  ')).toBe('el-leon-y-el-raton');
  });
});

describe('agruparPorLectura', () => {
  const data = {
    temas: [
      { id: 'declinacion', nivel: 'principiante' },
      { id: 'preposicion_caso', nivel: 'intermedio' },
    ],
    ejercicios: {
      declinacion: [
        { id: 'd1', fuente: 'avanzado · Immensee', nivel: 'avanzado', antes: 'x', respuesta: 'die' },
        { id: 'd2', fuente: 'principiante · El mercado', nivel: 'principiante', antes: 'y', respuesta: 'das' },
      ],
      preposicion_caso: [
        { id: 'p1', fuente: 'principiante · El mercado', nivel: 'principiante', antes: 'z', respuesta: 'mit' },
      ],
    },
  };

  it('agrupa por lectura y ordena por nivel ascendente', () => {
    const grupos = agruparPorLectura(data);
    expect(grupos.map((g) => g.titulo)).toEqual(['El mercado', 'Immensee']);
    expect(grupos[0].nivel).toBe('principiante');
    expect(grupos[0].slug).toBe('el-mercado');
  });

  it('dentro de una lectura, los ejercicios van por tema en el orden de data.temas', () => {
    const mercado = agruparPorLectura(data)[0];
    expect(mercado.ejercicios.map((e) => e.tema)).toEqual(['declinacion', 'preposicion_caso']);
    expect(mercado.ejercicios.map((e) => e.id)).toEqual(['d2', 'p1']);
  });
});

describe('lecturaCompletada', () => {
  const data = {
    temas: [{ id: 't', nivel: 'principiante' }],
    ejercicios: {
      t: [
        { id: 'a', fuente: 'principiante · X', nivel: 'principiante', antes: '1', respuesta: 'r1' },
        { id: 'b', fuente: 'principiante · X', nivel: 'principiante', antes: '2', respuesta: 'r2' },
      ],
    },
  };
  const grupo = agruparPorLectura(data)[0];

  it('solo con todos los ejercicios respondidos bien', () => {
    const claves = grupo.ejercicios.map(claveEjercicio);
    expect(lecturaCompletada(grupo, [])).toBe(false);
    expect(lecturaCompletada(grupo, [claves[0]])).toBe(false);
    expect(lecturaCompletada(grupo, claves)).toBe(true);
  });

  it('la clave es estable aunque cambien los ids', () => {
    const otro = { ...grupo.ejercicios[0], id: 'renumerado-99' };
    expect(claveEjercicio(otro)).toBe(claveEjercicio(grupo.ejercicios[0]));
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
