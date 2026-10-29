import { describe, it, expect } from 'vitest';
import {
  TIPOS,
  normalizar,
  tiposDeTarjeta,
  pregunta,
  comprobar,
  sesionDeExamen,
} from './examenMazo';

const AUSGABE = {
  id: 'ausgabe', tipo: 'sustantivo', articulo: 'die', palabra: 'Ausgabe',
  plural: 'die Ausgaben', es: 'gasto; número (de una revista)',
};
const ANSCHAUEN = {
  id: 'anschauen', tipo: 'verbo', infinitivo: 'an|schauen', presente: 'schaut an',
  preterito: 'schaute an', participio: 'angeschaut', auxiliar: 'hat', es: 'mirar, contemplar',
};
const ABBIEGEN = {
  id: 'abbiegen', tipo: 'verbo', infinitivo: 'ab|biegen', presente: 'biegt ab',
  preterito: 'bog ab', participio: 'abgebogen', auxiliar: 'ist', es: 'girar, torcer',
};
const AMUESIEREN = {
  id: 'amuesieren', tipo: 'verbo', infinitivo: 'sich amüsieren', presente: 'amüsiert sich',
  preterito: 'amüsierte sich', participio: 'amüsiert', auxiliar: 'hat', es: 'divertirse',
};
const GEMUETLICH = { id: 'gemuetlich', tipo: 'otro', palabra: 'gemütlich', es: 'acogedor' };

const preg = (t, tipo) => pregunta(t, tipo);
const resp = (t, tipo, texto) => comprobar(preg(t, tipo), texto);

describe('normalizar', () => {
  it('ignora mayúsculas, puntuación y espacios de sobra', () => {
    expect(normalizar('  Die   Ausgabe. ')).toBe('die ausgabe');
  });

  it('acepta los umlauts tecleados como ae/oe/ue y la ß como ss', () => {
    expect(normalizar('gemütlich')).toBe(normalizar('gemuetlich'));
    expect(normalizar('Fußgänger')).toBe(normalizar('fussgaenger'));
  });

  it('pero no acepta la vocal pelada: «schon» no es «schön»', () => {
    expect(normalizar('schon')).not.toBe(normalizar('schön'));
  });

  it('quita la barra del verbo separable', () => {
    expect(normalizar('ab|biegen')).toBe('abbiegen');
  });
});

describe('tiposDeTarjeta', () => {
  it('sustantivo: artículo y palabra; verbo: Partizip II e infinitivo', () => {
    expect(tiposDeTarjeta(AUSGABE)).toEqual([TIPOS.articulo, TIPOS.palabra]);
    expect(tiposDeTarjeta(ANSCHAUEN)).toEqual([TIPOS.participio, TIPOS.infinitivo]);
    expect(tiposDeTarjeta(GEMUETLICH)).toEqual([TIPOS.palabra]);
  });
});

describe('pregunta', () => {
  it('el género se pregunta enseñando la palabra SIN artículo', () => {
    const p = preg(AUSGABE, TIPOS.articulo);
    expect(p.muestra).toBe('Ausgabe');
    expect(p.esperado).toBe('die');
  });

  it('la palabra se pregunta enseñando el significado', () => {
    const p = preg(AUSGABE, TIPOS.palabra);
    expect(p.muestra).toBe(AUSGABE.es);
    expect(p.esperado).toBe('die Ausgabe');
  });

  it('el Partizip II se pregunta enseñando el infinitivo', () => {
    expect(preg(ANSCHAUEN, TIPOS.participio)).toMatchObject({
      muestra: 'an|schauen',
      esperado: 'angeschaut',
    });
  });
});

describe('comprobar: género', () => {
  it('acepta el artículo solo y también «artículo + palabra»', () => {
    expect(resp(AUSGABE, TIPOS.articulo, 'die').acierto).toBe(true);
    expect(resp(AUSGABE, TIPOS.articulo, 'Die Ausgabe').acierto).toBe(true);
  });

  it('el género equivocado falla y lo dice', () => {
    expect(resp(AUSGABE, TIPOS.articulo, 'der')).toMatchObject({ acierto: false, fallo: 'articulo' });
  });

  it('sin respuesta no se cuenta como acierto', () => {
    expect(resp(AUSGABE, TIPOS.articulo, '   ')).toMatchObject({ acierto: false, fallo: 'vacia' });
  });
});

describe('comprobar: palabra a partir del significado', () => {
  it('el sustantivo hay que escribirlo con su artículo', () => {
    expect(resp(AUSGABE, TIPOS.palabra, 'die Ausgabe').acierto).toBe(true);
  });

  it('palabra correcta y género mal → fallo de artículo, no de palabra', () => {
    expect(resp(AUSGABE, TIPOS.palabra, 'der Ausgabe')).toMatchObject({
      acierto: false,
      fallo: 'articulo',
    });
  });

  it('dejarse el artículo también es fallo de artículo', () => {
    expect(resp(AUSGABE, TIPOS.palabra, 'Ausgabe')).toMatchObject({
      acierto: false,
      fallo: 'articulo',
    });
  });

  it('otra palabra es fallo de forma', () => {
    expect(resp(AUSGABE, TIPOS.palabra, 'die Einnahme')).toMatchObject({
      acierto: false,
      fallo: 'forma',
    });
  });

  it('un adjetivo va sin artículo', () => {
    expect(resp(GEMUETLICH, TIPOS.palabra, 'gemütlich').acierto).toBe(true);
    expect(resp(GEMUETLICH, TIPOS.palabra, 'gemuetlich').acierto).toBe(true);
  });
});

describe('comprobar: Partizip II', () => {
  it('vale el participio solo', () => {
    expect(resp(ANSCHAUEN, TIPOS.participio, 'angeschaut').acierto).toBe(true);
  });

  it('vale también con el auxiliar correcto delante', () => {
    expect(resp(ANSCHAUEN, TIPOS.participio, 'hat angeschaut').acierto).toBe(true);
    expect(resp(ABBIEGEN, TIPOS.participio, 'ist abgebogen').acierto).toBe(true);
  });

  it('participio bien y auxiliar mal → fallo de auxiliar, con la forma completa', () => {
    expect(resp(ABBIEGEN, TIPOS.participio, 'hat abgebogen')).toMatchObject({
      acierto: false,
      fallo: 'auxiliar',
      esperado: 'ist abgebogen',
    });
  });

  it('el «ge» de más en un separable es fallo de forma', () => {
    expect(resp(ANSCHAUEN, TIPOS.participio, 'angegeschaut')).toMatchObject({
      acierto: false,
      fallo: 'forma',
    });
  });

  it('en un reflexivo da igual poner el «sich»', () => {
    expect(resp(AMUESIEREN, TIPOS.participio, 'amüsiert').acierto).toBe(true);
    expect(resp(AMUESIEREN, TIPOS.participio, 'hat sich amüsiert').acierto).toBe(true);
  });
});

describe('comprobar: infinitivo', () => {
  it('el separable vale con barra y sin ella', () => {
    expect(resp(ANSCHAUEN, TIPOS.infinitivo, 'anschauen').acierto).toBe(true);
    expect(resp(ANSCHAUEN, TIPOS.infinitivo, 'an|schauen').acierto).toBe(true);
  });

  it('el reflexivo vale con «sich» y sin él', () => {
    expect(resp(AMUESIEREN, TIPOS.infinitivo, 'sich amüsieren').acierto).toBe(true);
    expect(resp(AMUESIEREN, TIPOS.infinitivo, 'amüsieren').acierto).toBe(true);
  });
});

describe('sesionDeExamen', () => {
  const mazo = { id: 'prueba', tarjetas: [AUSGABE, ANSCHAUEN, GEMUETLICH] };
  const T0 = '2026-01-01T00:00:00.000Z';

  it('una pregunta por ficha, en el orden de la sesión SM-2', () => {
    const s = sesionDeExamen(mazo, {}, T0);
    expect(s).toHaveLength(3);
    expect(s.map((p) => p.tarjeta.id)).toEqual(['ausgabe', 'anschauen', 'gemuetlich']);
  });

  it('la misma semilla da exactamente la misma sesión', () => {
    const a = sesionDeExamen(mazo, {}, T0, { semilla: 'x7' });
    const b = sesionDeExamen(mazo, {}, T0, { semilla: 'x7' });
    expect(a.map((p) => p.clave)).toEqual(b.map((p) => p.clave));
  });

  it('se puede limitar a un tipo: solo género', () => {
    const s = sesionDeExamen(mazo, {}, T0, { tipos: [TIPOS.articulo] });
    expect(s.map((p) => p.tarjeta.id)).toEqual(['ausgabe']); // las otras no lo admiten
    expect(s[0].tipo).toBe(TIPOS.articulo);
  });

  it('respeta el tope de fichas nuevas de srs.js', () => {
    expect(sesionDeExamen(mazo, {}, T0, { maxNuevas: 2 })).toHaveLength(2);
  });
});
