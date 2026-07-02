import { describe, it, expect } from 'vitest';
import {
  retrievability,
  priorPorFrecuencia,
  probConocer,
  candidatasRepasoPrevio,
  TOPE_POR_NIVEL,
} from './conocimiento';
import { crearEntrada } from './bolsa';

const T0 = '2026-01-01T00:00:00.000Z';
const DIA = 24 * 60 * 60 * 1000;

function enDias(n) {
  return new Date(Date.parse(T0) + n * DIA).toISOString();
}

// srs con último repaso en T0 e intervalo `intervalo` (vencimiento = T0 + intervalo).
function srsRepasadaEn(intervalo) {
  return {
    reps: 1,
    ef: 2.5,
    intervalo,
    vencimiento: enDias(intervalo),
    repasos: 1,
    fallos: 0,
  };
}

describe('retrievability', () => {
  it('vale 1 justo después de repasar y e^-1 cuando t = S', () => {
    const srs = srsRepasadaEn(6);
    expect(retrievability(srs, T0)).toBeCloseTo(1);
    expect(retrievability(srs, enDias(6))).toBeCloseTo(Math.exp(-1));
  });

  it('decae con el tiempo y más despacio con intervalos largos', () => {
    const corta = srsRepasadaEn(1);
    const larga = srsRepasadaEn(30);
    expect(retrievability(corta, enDias(3))).toBeLessThan(
      retrievability(larga, enDias(3))
    );
  });
});

describe('priorPorFrecuencia', () => {
  it('es monótono en la frecuencia', () => {
    const total = 30000;
    const p1 = priorPorFrecuencia(1, total);
    const p30 = priorPorFrecuencia(30, total);
    const p1000 = priorPorFrecuencia(1000, total);
    expect(p1).toBeLessThan(p30);
    expect(p30).toBeLessThan(p1000);
  });

  it('palabra muy común → P alta; hapax → P baja; sin datos → 0.1', () => {
    expect(priorPorFrecuencia(993, 30294)).toBeGreaterThan(0.85); // "und"
    expect(priorPorFrecuencia(1, 30294)).toBeLessThan(0.15);
    expect(priorPorFrecuencia(undefined, 30294)).toBe(0.1);
  });
});

describe('probConocer (los 4 casos)', () => {
  const entrada = crearEntrada({
    lang: 'de',
    surface: 'Frau',
    traducciones: { es: 'mujer' },
    addedAt: T0,
  });

  it('conocida marcada → 0.95', () => {
    expect(probConocer(null, { conocida: true }, T0)).toBe(0.95);
  });

  it('en bolsa con srs → retrievability', () => {
    const conSrs = { ...entrada, srs: srsRepasadaEn(6) };
    expect(probConocer(conSrs, {}, enDias(6))).toBeCloseTo(Math.exp(-1));
  });

  it('en bolsa sin srs → 0.2', () => {
    expect(probConocer(entrada, {}, T0)).toBe(0.2);
  });

  it('nunca vista → prior por frecuencia', () => {
    expect(probConocer(null, { conteo: 993, total: 30294 }, T0)).toBeGreaterThan(0.85);
  });
});

describe('candidatasRepasoPrevio', () => {
  const lexico = {
    'de:katze': { lemma: 'Katze', es: 'gato' },
    'de:hund': { lemma: 'Hund', es: 'perro' },
    'de:und': { lemma: 'und', es: 'y' },
    'de:nahm': { lemma: 'nehmen', es: 'tomar' },
    'de:gregor': { lemma: 'Gregor' }, // sin traducción (nombre propio)
  };
  const frecuencias = {
    totales: { de: 30000 },
    lemas: { 'de:und': 1000, 'de:katze': 2, 'de:hund': 5, 'de:annehmen': 3 },
  };
  const lectura = {
    nivel: 'principiante',
    cuerpo: { de: ['Die Katze und der Hund.', 'Gregor nahm die Katze.'] },
  };

  it('excluye comunes y sin traducción, ordena por improbabilidad y deduplica', () => {
    const c = candidatasRepasoPrevio(lectura, 'de', { lexico, frecuencias, ahora: T0 });
    const ids = c.map((x) => x.id);
    expect(ids).not.toContain('de:und'); // P alta, fuera
    expect(ids).not.toContain('de:gregor'); // sin es, fuera
    expect(ids.filter((i) => i === 'de:katze')).toHaveLength(1); // aparece 2 veces, 1 ficha
    // Katze (2 apariciones) es menos probable de conocer que Hund (5).
    expect(ids.indexOf('de:katze')).toBeLessThan(ids.indexOf('de:hund'));
  });

  it('el override de la lectura desambigua el lema', () => {
    const conOverride = {
      ...lectura,
      lexico: { 'de:nahm': { lemma: 'annehmen', es: 'suponer' } },
    };
    const c = candidatasRepasoPrevio(conOverride, 'de', { lexico, frecuencias, ahora: T0 });
    expect(c.map((x) => x.id)).toContain('de:annehmen');
  });

  it('respeta el tope por nivel y excluye conocidas y bien retenidas', () => {
    const letras = 'abcdefghijklmnopqrstuvwxyz';
    const muchas = {};
    const cuerpo = [];
    for (let i = 0; i < 30; i++) {
      const w = `wort${letras[Math.floor(i / 26)]}${letras[i % 26]}`;
      muchas[`de:${w}`] = { lemma: w, es: `palabra ${i}` };
      cuerpo.push(w);
    }
    const l = { nivel: 'principiante', cuerpo: { de: [cuerpo.join(' ')] } };
    const c = candidatasRepasoPrevio(l, 'de', {
      lexico: muchas,
      frecuencias,
      conocidas: ['de:wortaa'],
      bolsa: [
        {
          ...crearEntrada({ lang: 'de', surface: 'wortab', lemma: 'wortab', traducciones: { es: 'p' }, addedAt: T0 }),
          srs: srsRepasadaEn(30), // recién repasada con intervalo largo → retenida
        },
      ],
      ahora: T0,
    });
    expect(c).toHaveLength(TOPE_POR_NIVEL.principiante);
    const ids = c.map((x) => x.id);
    expect(ids).not.toContain('de:wortaa');
    expect(ids).not.toContain('de:wortab');
  });

  it('una palabra de la bolsa vencida hace ficha con enBolsa=true', () => {
    const vencida = {
      ...crearEntrada({ lang: 'de', surface: 'Katze', lemma: 'Katze', traducciones: { es: 'gato' }, addedAt: T0 }),
      srs: srsRepasadaEn(1),
    };
    const c = candidatasRepasoPrevio(lectura, 'de', {
      lexico,
      frecuencias,
      bolsa: [vencida],
      ahora: enDias(10), // R = e^-10 ≈ 0
    });
    const katze = c.find((x) => x.id === 'de:katze');
    expect(katze.enBolsa).toBe(true);
    expect(katze.prob).toBeLessThan(0.01);
  });
});
