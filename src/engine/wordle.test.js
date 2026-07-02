import { describe, it, expect } from 'vitest';
import {
  evaluar,
  esVictoria,
  patron,
  elegirSecreto,
  filtrarConsistentes,
  entropiaDe,
  mejorIntento,
} from './wordle';

describe('evaluar', () => {
  it('marca verdes, amarillos y grises', () => {
    // secreto hand / intento dank: d existe fuera de sitio, a y n en su sitio,
    // k no está.
    expect(patron(evaluar('hand', 'dank'))).toBe('CBB-');
  });

  it('todo verde cuando acierta', () => {
    expect(patron(evaluar('haus', 'haus'))).toBe('BBBB');
    expect(esVictoria(evaluar('haus', 'haus'))).toBe(true);
  });

  it('letras repetidas: cada letra del secreto justifica UNA sola marca', () => {
    // secreto nase (una n) / intento anna: la primera n va de amarillo,
    // la segunda ya no tiene n del secreto que la justifique.
    expect(patron(evaluar('nase', 'anna'))).toBe('CC--');
  });

  it('los verdes consumen antes que los amarillos', () => {
    // secreto anna / intento nana: posiciones 2-3 ¿? n en pos1 del secreto…
    // a-n-n-a vs n-a-n-a: pos2 n=n verde, pos3 a=a… no: anna[3]='a', nana[3]='a' verde.
    expect(patron(evaluar('anna', 'nana'))).toBe('CCBB');
  });

  it('sin falsos amarillos cuando la letra ya se consumió en verde', () => {
    // secreto esel / intento else: la e de pos0 no es verde… e-l-s-e vs e-s-e-l:
    // pos0 e=e verde; quedan s,e,l del secreto para l,s,e → todos amarillos.
    expect(patron(evaluar('esel', 'else'))).toBe('BCCC');
  });
});

describe('elegirSecreto', () => {
  const PALABRAS = ['haus', 'maus', 'hals', 'nase', 'esel'];

  it('es determinista por semilla y pertenece al diccionario', () => {
    const a = elegirSecreto(PALABRAS, 'X');
    expect(a).toBe(elegirSecreto(PALABRAS, 'X'));
    expect(PALABRAS).toContain(a);
  });

  it('no depende del orden de entrada del diccionario', () => {
    expect(elegirSecreto([...PALABRAS].reverse(), 'X')).toBe(elegirSecreto(PALABRAS, 'X'));
  });

  it('varía con la semilla', () => {
    const secretos = new Set(['a', 'b', 'c', 'd', 'e', 'f'].map((s) => elegirSecreto(PALABRAS, s)));
    expect(secretos.size).toBeGreaterThan(1);
  });

  it('diccionario vacío → null', () => {
    expect(elegirSecreto([], 'X')).toBeNull();
  });
});

describe('filtrarConsistentes', () => {
  const PALABRAS = ['haus', 'maus', 'laus', 'hals', 'nase'];

  it('conserva exactamente las palabras que habrían dado el mismo feedback', () => {
    // Jugamos «haus» contra secreto desconocido y sale '-BBB' (h gris, aus bien):
    // consistentes = las *aus sin h — maus y laus.
    const intentos = [{ intento: 'haus', resultado: evaluar('maus', 'haus') }];
    expect(filtrarConsistentes(PALABRAS, intentos)).toEqual(['maus', 'laus']);
  });

  it('el propio secreto siempre es consistente', () => {
    const intentos = [
      { intento: 'haus', resultado: evaluar('nase', 'haus') },
      { intento: 'hals', resultado: evaluar('nase', 'hals') },
    ];
    expect(filtrarConsistentes(PALABRAS, intentos)).toContain('nase');
  });

  it('sin intentos, todas son consistentes', () => {
    expect(filtrarConsistentes(PALABRAS, [])).toEqual(PALABRAS);
  });
});

describe('entropía', () => {
  it('partición uniforme en k clases → log2(k) bits', () => {
    // Con candidatas {aa, ab, ba, bb} el intento «ab» separa las 4 en 4
    // patrones distintos → 2 bits exactos.
    const candidatas = ['aa', 'ab', 'ba', 'bb'];
    expect(entropiaDe('ab', candidatas)).toBeCloseTo(2, 10);
  });

  it('un intento que no separa nada aporta 0 bits', () => {
    // «zz» da el mismo patrón '--' para todas las candidatas sin z.
    expect(entropiaDe('zz', ['aa', 'ab', 'ba'])).toBeCloseTo(0, 10);
  });

  it('mejorIntento maximiza la entropía y es determinista', () => {
    const palabras = ['aa', 'ab', 'ba', 'bb', 'zz'];
    const { intento, entropia } = mejorIntento(palabras);
    for (const p of palabras) {
      expect(entropia).toBeGreaterThanOrEqual(entropiaDe(p, palabras) - 1e-12);
    }
    expect(intento).not.toBe('zz');
  });
});
