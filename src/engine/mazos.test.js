import { describe, it, expect } from 'vitest';
import {
  claveTarjeta,
  combinarMazos,
  entradasDeMazo,
  sesionDeMazo,
  calificarTarjeta,
  resumenDeMazo,
  estadoTarjeta,
  formasPasiva,
  textoPlural,
  textoPerfecto,
  rasgosGramaticales,
  problemasDeTarjeta,
} from './mazos';
import { CALIFICACIONES } from './srs';

// Todos los mazos reales de «Más contenidos», por id (mazo-<id>.json).
const MAZOS = Object.fromEntries(
  Object.entries(
    import.meta.glob('../data/mas/mazo-*.json', { eager: true, import: 'default' })
  ).map(([ruta, m]) => [ruta.match(/mazo-(.+)\.json$/)[1], m])
);

const T0 = '2026-01-01T00:00:00.000Z';
const T1 = '2026-01-02T00:00:00.000Z';

const mazo = {
  id: 'prueba',
  tarjetas: [
    { id: 'a', tipo: 'verbo', infinitivo: 'bauen', presente: 'baut', preterito: 'baute', participio: 'gebaut', auxiliar: 'hat', es: 'construir' },
    { id: 'b', tipo: 'sustantivo', articulo: 'der', palabra: 'Wert', plural: 'die Werte', es: 'valor' },
    { id: 'c', tipo: 'sustantivo', articulo: 'die', palabra: 'Toleranz', plural: null, es: 'tolerancia' },
  ],
};

const ids = (cola) => cola.map((x) => x.id);

describe('claveTarjeta / combinarMazos', () => {
  it('la clave es de la palabra (tipo:id), no del mazo', () => {
    expect(claveTarjeta(mazo.tarjetas[0])).toBe('verbo:a');
    expect(claveTarjeta({ id: 'a', tipo: 'sustantivo' })).toBe('sustantivo:a');
  });

  it('combina mazos sin repetir palabras y con las propias primero', () => {
    const otro = {
      tarjetas: [
        { ...mazo.tarjetas[1], es: 'otra glosa' },
        { id: 'd', tipo: 'otro', palabra: 'blind', es: 'ciego' },
      ],
    };
    const combinado = combinarMazos(mazo, [otro]);
    expect(combinado.tarjetas.map(claveTarjeta)).toEqual([
      'verbo:a',
      'sustantivo:b',
      'sustantivo:c',
      'otro:d',
    ]);
    expect(combinado.tarjetas[1].es).toBe('valor');
  });
});

describe('entradasDeMazo / sesionDeMazo (SM-2 de srs.js)', () => {
  it('convierte las fichas en entradas repasables con clave tipo:id', () => {
    const e = entradasDeMazo(mazo);
    expect(ids(e)).toEqual(['verbo:a', 'sustantivo:b', 'sustantivo:c']);
    expect(e[0].traducciones).toEqual({ es: 'construir' });
    expect(e[0].srs).toBeUndefined();
  });

  it('sin estados, la sesión presenta las fichas nuevas en el orden del mazo', () => {
    expect(ids(sesionDeMazo(mazo, {}, T0))).toEqual(['verbo:a', 'sustantivo:b', 'sustantivo:c']);
  });

  it('respeta el tope de nuevas por sesión', () => {
    expect(sesionDeMazo(mazo, {}, T0, { maxNuevas: 2 })).toHaveLength(2);
  });

  it('una ficha calificada «bien» sale de la cola hasta que vence y entonces va primero', () => {
    const estados = calificarTarjeta({}, 'verbo:a', CALIFICACIONES.bien, T0);
    expect(ids(sesionDeMazo(mazo, estados, T0))).toEqual(['sustantivo:b', 'sustantivo:c']);
    expect(ids(sesionDeMazo(mazo, estados, T1))[0]).toBe('verbo:a');
  });

  it('una ficha fallada sigue pendiente en la misma sesión', () => {
    const estados = calificarTarjeta({}, 'sustantivo:b', CALIFICACIONES.otraVez, T0);
    expect(ids(sesionDeMazo(mazo, estados, T0))).toContain('sustantivo:b');
  });

  it('el progreso de una palabra vale en cualquier mazo que la contenga', () => {
    const estados = calificarTarjeta({}, 'sustantivo:b', CALIFICACIONES.bien, T0);
    const otroMazo = { id: 'otro', tarjetas: [mazo.tarjetas[1]] };
    expect(sesionDeMazo(otroMazo, estados, T0)).toEqual([]);
  });
});

describe('calificarTarjeta', () => {
  it('no muta el mapa anterior y aplica la recurrencia SM-2', () => {
    const antes = {};
    const despues = calificarTarjeta(antes, 'verbo:a', CALIFICACIONES.bien, T0);
    expect(antes).toEqual({});
    expect(despues['verbo:a'].reps).toBe(1);
    expect(despues['verbo:a'].intervalo).toBe(1);
  });
});

describe('resumenDeMazo / estadoTarjeta', () => {
  it('cuenta nuevas, vencidas y programadas', () => {
    const estados = calificarTarjeta({}, 'verbo:a', CALIFICACIONES.bien, T0);
    expect(resumenDeMazo(mazo, estados, T0)).toMatchObject({ nuevas: 2, vencidas: 0, programadas: 1 });
  });

  it('describe el estado de una ficha', () => {
    const s = calificarTarjeta({}, 'x', CALIFICACIONES.bien, T0).x;
    expect(estadoTarjeta(undefined, T0)).toEqual({ tipo: 'nueva' });
    expect(estadoTarjeta(s, T0)).toEqual({ tipo: 'programada', dias: 1 });
    expect(estadoTarjeta(s, T1)).toEqual({ tipo: 'pendiente' });
  });
});

describe('formasPasiva / textoPlural / textoPerfecto', () => {
  it('construye la pasiva a partir del Partizip II', () => {
    expect(formasPasiva(mazo.tarjetas[0])).toEqual({
      presente: 'wird gebaut',
      preterito: 'wurde gebaut',
      perfecto: 'ist gebaut worden',
      modal: 'muss gebaut werden',
    });
  });

  it('no hay pasiva para sustantivos ni para fichas con pasiva:false', () => {
    expect(formasPasiva(mazo.tarjetas[1])).toBeNull();
    expect(formasPasiva({ ...mazo.tarjetas[0], pasiva: false })).toBeNull();
  });

  it('tampoco para reflexivos ni para verbos con sein', () => {
    expect(formasPasiva({ ...mazo.tarjetas[0], infinitivo: 'sich anstrengen' })).toBeNull();
    expect(formasPasiva({ ...mazo.tarjetas[0], auxiliar: 'ist' })).toBeNull();
  });

  it('el plural null se muestra como «solo singular»', () => {
    expect(textoPlural(mazo.tarjetas[1])).toBe('die Werte');
    expect(textoPlural(mazo.tarjetas[2])).toBe('solo singular (Sg.)');
  });

  it('el Perfekt es auxiliar + participio salvo forma explícita (reflexivos)', () => {
    expect(textoPerfecto(mazo.tarjetas[0])).toBe('hat gebaut');
    expect(textoPerfecto({ ...mazo.tarjetas[0], perfecto: 'hat sich gebaut' })).toBe('hat sich gebaut');
  });
});

describe('problemasDeTarjeta (regla: género + plural; presente + pasado + Partizip II)', () => {
  it('acepta fichas completas, también con plural null explícito', () => {
    expect(problemasDeTarjeta(mazo.tarjetas[0])).toEqual([]);
    expect(problemasDeTarjeta(mazo.tarjetas[2])).toEqual([]);
    expect(problemasDeTarjeta({ id: 'x', tipo: 'otro', palabra: 'blind', es: 'ciego' })).toEqual([]);
  });

  it('detecta sustantivos sin plural o sin género y verbos sin pasado', () => {
    const { plural: _p, ...sinPlural } = mazo.tarjetas[1];
    expect(problemasDeTarjeta(sinPlural)).toContain('plural');
    expect(problemasDeTarjeta({ ...mazo.tarjetas[1], articulo: 'el' })).toContain('articulo');
    const { preterito: _t, ...sinPasado } = mazo.tarjetas[0];
    expect(problemasDeTarjeta(sinPasado)).toContain('preterito');
  });
});

describe('mazos reales de «Más contenidos»', () => {
  const lista = Object.entries(MAZOS);

  it('hay mazos cargados', () => {
    expect(lista.length).toBeGreaterThanOrEqual(10);
  });

  for (const [id, m] of lista) {
    it(`«${id}»: fichas completas y sin palabras repetidas`, () => {
      const conProblemas = m.tarjetas
        .map((t) => [t.id, problemasDeTarjeta(t)])
        .filter(([, p]) => p.length > 0);
      expect(conProblemas).toEqual([]);
      const claves = m.tarjetas.map(claveTarjeta);
      expect(new Set(claves).size).toBe(claves.length);
      for (const incluido of m.incluye ?? []) expect(MAZOS[incluido]).toBeDefined();
    });
  }

  it('la misma palabra tiene los mismos datos gramaticales en todos los mazos', () => {
    const vistos = new Map();
    const choques = [];
    for (const [id, m] of lista) {
      for (const t of m.tarjetas) {
        const clave = claveTarjeta(t);
        const rasgos = JSON.stringify(rasgosGramaticales(t));
        const previo = vistos.get(clave);
        if (previo && previo.rasgos !== rasgos) choques.push(`${clave}: ${previo.id} ≠ ${id}`);
        else if (!previo) vistos.set(clave, { id, rasgos });
      }
    }
    expect(choques).toEqual([]);
  });

  it('el mazo de pasiva solo tiene verbos y el de valores solo sustantivos', () => {
    expect(MAZOS.pasiva.tarjetas.every((t) => t.tipo === 'verbo')).toBe(true);
    expect(MAZOS.valores.tarjetas.every((t) => t.tipo === 'sustantivo')).toBe(true);
  });

  const verbos = lista.flatMap(([, m]) => m.tarjetas.filter((t) => t.tipo === 'verbo'));
  const sinSich = (t) => t.infinitivo.replace(/^sich /, '');
  const INSEPARABLE = /^(be|emp|ent|er|miss|ver|zer)/;

  it('prefijo inseparable o -ieren → Partizip II sin ge-', () => {
    const sinGe = verbos.filter(
      (t) => (!sinSich(t).includes('|') && INSEPARABLE.test(sinSich(t))) || sinSich(t).endsWith('ieren')
    );
    expect(sinGe.length).toBeGreaterThan(20);
    expect(sinGe.filter((t) => t.participio.startsWith('ge')).map((t) => t.id)).toEqual([]);
  });

  it('verbo separable (con |) → prefijo + ge + participio', () => {
    const separables = verbos.filter((t) => sinSich(t).includes('|'));
    expect(separables.length).toBeGreaterThan(20);
    const mal = separables.filter((t) => {
      const [prefijo, resto] = sinSich(t).split('|');
      const sinGe = INSEPARABLE.test(resto) || resto.endsWith('ieren');
      return !t.participio.startsWith(sinGe ? prefijo : `${prefijo}ge`);
    });
    expect(mal.map((t) => t.id)).toEqual([]);
  });

  it('la preposición, cuando la hay, se escribe «preposición + caso»', () => {
    const conPreposicion = lista.flatMap(([, m]) => m.tarjetas).filter((t) => t.preposicion);
    expect(conPreposicion.length).toBeGreaterThan(10);
    const mal = conPreposicion.filter(
      (t) => !/^[a-zäöüß]+ \+ (acusativo|dativo|genitivo)$/.test(t.preposicion)
    );
    expect(mal.map((t) => `${t.id}: ${t.preposicion}`)).toEqual([]);
    expect(conPreposicion.every((t) => t.tipo === 'verbo' || t.tipo === 'otro')).toBe(true);
  });
});
