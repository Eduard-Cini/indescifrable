// engine/conocimiento.js
// Modelo de conocimiento léxico: estima P(conocer) para cada palabra de una
// lectura y selecciona las candidatas al "repaso previo" (las que el lector
// probablemente no conoce).
//
// Modelo de la tesis, por casos sobre el id `idioma:lemma`:
//  1. Marcada «ya la conocía»            → P = 0.95
//  2. En bolsa con estado SRS            → retrievability R = e^(−t/S)
//       t = días desde el último repaso (vencimiento − intervalo, recuperable
//       del estado SM-2 sin campos extra), S = max(intervalo, 0.5) días.
//  3. En bolsa sin SRS                   → P = 0.2 (la guardó porque no la sabía)
//  4. Nunca vista → prior logístico sobre la escala Zipf del corpus propio:
//       zipf = log10(conteo/total · 10⁶),  P = σ((zipf − Z0)/TAU)
//     Con el corpus actual (~30k tokens de): "und" (993) → zipf ≈ 4.5 → P ≈ 0.9;
//     un hapax → zipf ≈ 1.5 → P ≈ 0.1. Z0 = 3 equivale a ~30 apariciones.
//
// Módulo puro: tiempo (`ahora` ISO) y datos (bolsa, léxico, frecuencias,
// conocidas) siempre inyectados; determinista y simulable, como srs.js.

import { normalizar } from './bolsa';
import { tokenizar } from './tokenizar';

const MS_POR_DIA = 24 * 60 * 60 * 1000;

// Calibración del prior por frecuencia (documentada arriba).
const Z0 = 3.0;
const TAU = 0.7;
const P_CONOCIDA = 0.95; // marcada «ya la conocía»
const P_GUARDADA = 0.2; // en bolsa, nunca repasada
const P_SIN_DATOS = 0.1; // sin frecuencia en el corpus
const UMBRAL_CANDIDATA = 0.7; // solo P < umbral entra al repaso previo

/** Cuántas fichas presenta el repaso previo según el nivel de la lectura. */
export const TOPE_POR_NIVEL = {
  principiante: 5,
  intermedio: 12,
  avanzado: 20,
};

/** R = e^(−t/S): probabilidad de recordar una palabra con estado SM-2. */
export function retrievability(srs, ahora) {
  const ultimoRepaso = Date.parse(srs.vencimiento) - srs.intervalo * MS_POR_DIA;
  const t = Math.max(0, (Date.parse(ahora) - ultimoRepaso) / MS_POR_DIA);
  const s = Math.max(srs.intervalo, 0.5);
  return Math.exp(-t / s);
}

/** Prior logístico sobre la escala Zipf para palabras nunca vistas. */
export function priorPorFrecuencia(conteo, total) {
  if (!conteo || !total) return P_SIN_DATOS;
  const zipf = Math.log10((conteo / total) * 1e6);
  return 1 / (1 + Math.exp(-(zipf - Z0) / TAU));
}

/**
 * P(conocer) de una palabra: `entrada` es su entrada de la bolsa (o null),
 * `conocida` si el usuario la marcó como ya conocida, `conteo/total` su
 * frecuencia en el corpus del idioma.
 */
export function probConocer(entrada, { conocida = false, conteo, total }, ahora) {
  if (conocida) return P_CONOCIDA;
  if (entrada?.srs) return retrievability(entrada.srs, ahora);
  if (entrada) return P_GUARDADA;
  return priorPorFrecuencia(conteo, total);
}

/**
 * Candidatas al repaso previo de una lectura: tokens únicos del cuerpo,
 * resueltos a lema (override de la lectura > léxico global), solo con
 * traducción al español, ordenadas por P(conocer) ascendente y recortadas
 * al tope del nivel. Devuelve [{ id, surface, lemma, es, prob, enBolsa }].
 */
export function candidatasRepasoPrevio(
  lectura,
  idioma,
  { bolsa = [], lexico = {}, frecuencias = {}, conocidas = [], ahora }
) {
  const frases = lectura.cuerpo?.[idioma] ?? [];
  const total = frecuencias.totales?.[idioma];
  const lemas = frecuencias.lemas ?? {};
  const setConocidas = new Set(conocidas);
  const porId = new Map();

  for (const frase of frases) {
    for (const t of tokenizar(frase)) {
      if (t.tipo !== 'palabra') continue;
      const claveForma = `${idioma}:${normalizar(t.valor)}`;
      const entradaLex = lectura.lexico?.[claveForma] ?? lexico[claveForma];
      const lemma = entradaLex?.lemma ?? t.valor;
      const id = `${idioma}:${normalizar(lemma)}`;
      if (porId.has(id)) continue;

      const enBolsa = bolsa.find((p) => p.id === id) ?? null;
      const es = entradaLex?.es ?? enBolsa?.traducciones?.es;
      if (!es) continue; // sin traducción no hay ficha (excluye nombres propios)

      const prob = probConocer(
        enBolsa,
        { conocida: setConocidas.has(id), conteo: lemas[id], total },
        ahora
      );
      porId.set(id, {
        id,
        surface: t.valor,
        lemma,
        es,
        prob,
        enBolsa: Boolean(enBolsa),
      });
    }
  }

  const tope = TOPE_POR_NIVEL[lectura.nivel] ?? 10;
  return [...porId.values()]
    .filter((c) => c.prob < UMBRAL_CANDIDATA)
    .sort((a, b) => a.prob - b.prob)
    .slice(0, tope);
}
