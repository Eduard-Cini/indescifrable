// engine/mazos.js
// Mazos de fichas de «Más contenidos» (vocabulario del capítulo 10 de Netzwerk
// neu B1) sobre el MISMO planificador SM-2 de la Sección 2 (srs.js). Cada ficha
// es un dato estático (JSON); su estado de repaso vive aparte, en un mapa
// clave → srs que persiste almacenamiento.js. Aquí se convierte el par
// (ficha, estado) en las entradas que srs.js ya sabe planificar: el modelo de
// memorización es uno solo para la bolsa y para estos mazos.
//
// Módulo puro: sin DOM, React ni localStorage; `ahora` siempre inyectado.
// Extensión explícita en el import: también lo usa node (simulacion/*.mjs).

import { calificar, seleccionarSesion, resumen } from './srs.js';

const MS_POR_DIA = 24 * 60 * 60 * 1000;
// Fecha base ficticia para `addedAt`: las fichas nuevas salen en el orden del
// mazo (seleccionarSesion ordena las nuevas por fecha de incorporación).
const BASE_ORDEN = Date.UTC(2026, 0, 1);

export const ARTICULOS = ['der', 'die', 'das'];

/**
 * Clave estable del progreso de una ficha: `tipo:id`. La clave es de la
 * PALABRA, no del mazo: si «gründen» está en dos mazos, comparte estado SM-2
 * (el modelo de memoria es por palabra, como el de la bolsa).
 */
export function claveTarjeta(tarjeta) {
  return `${tarjeta.tipo}:${tarjeta.id}`;
}

/** Mazo con sus fichas propias y las de los mazos incluidos, sin repetir palabras. */
export function combinarMazos(mazo, incluidos = []) {
  const vistas = new Set();
  const tarjetas = [];
  for (const t of [...mazo.tarjetas, ...incluidos.flatMap((m) => m.tarjetas)]) {
    const clave = claveTarjeta(t);
    if (vistas.has(clave)) continue;
    vistas.add(clave);
    tarjetas.push(t);
  }
  return { ...mazo, tarjetas };
}

/** Fichas del mazo como entradas repasables por srs.js, con su estado si lo hay. */
export function entradasDeMazo(mazo, estados = {}) {
  return mazo.tarjetas.map((t, i) => {
    const id = claveTarjeta(t);
    return {
      ...t,
      id,
      traducciones: { es: t.es },
      addedAt: new Date(BASE_ORDEN + i * 1000).toISOString(),
      srs: estados[id],
    };
  });
}

/** Cola de una sesión: vencidas primero y luego nuevas en el orden del mazo. */
export function sesionDeMazo(mazo, estados, ahora, opciones) {
  return seleccionarSesion(entradasDeMazo(mazo, estados), ahora, opciones);
}

/** Aplica la calificación q a la ficha `clave`; devuelve un mapa nuevo. */
export function calificarTarjeta(estados, clave, q, ahora) {
  return { ...estados, [clave]: calificar(estados[clave], q, ahora) };
}

/** Conteos del mazo (nuevas, vencidas, programadas) para el índice. */
export function resumenDeMazo(mazo, estados, ahora) {
  return resumen(entradasDeMazo(mazo, estados), ahora);
}

/** Estado legible de una ficha: nueva, pendiente o programada a N días. */
export function estadoTarjeta(srs, ahora) {
  if (!srs) return { tipo: 'nueva' };
  const dias = Math.ceil((Date.parse(srs.vencimiento) - Date.parse(ahora)) / MS_POR_DIA);
  return dias <= 0 ? { tipo: 'pendiente' } : { tipo: 'programada', dias };
}

/**
 * Formas de la pasiva de un verbo a partir de su Partizip II
 * (null si la ficha no es un verbo o no admite pasiva, como werden).
 */
export function formasPasiva(tarjeta) {
  if (tarjeta.tipo !== 'verbo' || tarjeta.pasiva === false) return null;
  // Sin pasiva personal: los reflexivos (sich anstrengen) y los verbos que
  // forman el Perfekt con sein (intransitivos: gelangen, zurückkommen…).
  if (tarjeta.infinitivo.startsWith('sich ') || tarjeta.auxiliar === 'ist') return null;
  const p = tarjeta.participio;
  return {
    presente: `wird ${p}`,
    preterito: `wurde ${p}`,
    perfecto: `ist ${p} worden`,
    modal: `muss ${p} werden`,
  };
}

/** Plural para la UI: la forma plural o «solo singular (Sg.)». */
export function textoPlural(tarjeta) {
  return tarjeta.plural ?? 'solo singular (Sg.)';
}

/** Perfekt de un verbo: auxiliar + Partizip II, salvo forma explícita (reflexivos). */
export function textoPerfecto(tarjeta) {
  return tarjeta.perfecto ?? `${tarjeta.auxiliar} ${tarjeta.participio}`;
}

/**
 * Datos gramaticales de una ficha. Si la misma palabra (tipo:id) aparece en
 * varios mazos, estos datos tienen que coincidir (lo comprueba un test).
 */
export function rasgosGramaticales(t) {
  if (t.tipo === 'sustantivo') return [t.articulo, t.palabra, t.plural];
  if (t.tipo === 'verbo') {
    return [t.infinitivo, t.presente, t.preterito, t.participio, t.auxiliar, t.perfecto ?? null];
  }
  return [t.palabra];
}

/**
 * Regla de contenido: todo sustantivo trae género (artículo) y plural (o null
 * explícito = solo singular); todo verbo trae presente, Präteritum, Partizip II
 * y auxiliar. Devuelve los campos que faltan (vacío = ficha completa).
 */
export function problemasDeTarjeta(t) {
  const faltan = [];
  if (!t.id) faltan.push('id');
  if (!t.es) faltan.push('es');
  if (t.tipo === 'sustantivo') {
    if (!t.palabra) faltan.push('palabra');
    if (!ARTICULOS.includes(t.articulo)) faltan.push('articulo');
    if (!('plural' in t) || (t.plural !== null && !t.plural)) faltan.push('plural');
  } else if (t.tipo === 'verbo') {
    for (const campo of ['infinitivo', 'presente', 'preterito', 'participio']) {
      if (!t[campo]) faltan.push(campo);
    }
    if (!['hat', 'ist'].includes(t.auxiliar)) faltan.push('auxiliar');
  } else if (t.tipo === 'otro') {
    // adjetivos, adverbios y expresiones: palabra + significado
    if (!t.palabra) faltan.push('palabra');
  } else {
    faltan.push('tipo');
  }
  return faltan;
}
