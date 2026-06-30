// engine/bolsa.js
// Lógica pura de la "bolsa de palabras": estructura de datos única y persistente
// que comparten la sección de Lectura (1) y la de Repaso espaciado (2).
//
// Reglas de la tesis modeladas aquí:
//  - La bolsa es única; una palabra se identifica por `id` = `${lang}:${clave}`.
//  - Una palabra ya presente CONSERVA su estado (no se reinicia el progreso):
//    agregar una palabra existente deja la entrada intacta.
//
// Este módulo no toca el DOM, React ni localStorage: solo recibe datos y
// devuelve datos. La persistencia vive en `almacenamiento.js`.

/** Normaliza una forma superficial para construir claves estables. */
export function normalizar(superficie) {
  return String(superficie)
    .trim()
    .toLowerCase()
    // recorta puntuación de los extremos, conserva letras acentuadas y umlauts
    .replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, '');
}

/** Construye el id canónico de una palabra: `idioma:forma_normalizada`. */
export function clavePalabra(lang, superficie) {
  return `${lang}:${normalizar(superficie)}`;
}

/**
 * Crea una entrada de la bolsa. `addedAt` es inyectable para que las pruebas
 * sean deterministas; si se omite, usa la hora actual.
 */
export function crearEntrada({
  lang,
  surface,
  lemma,
  traducciones = {},
  origen = 'manual',
  addedAt,
}) {
  return {
    id: clavePalabra(lang, lemma ?? surface),
    lang,
    surface,
    lemma: lemma ?? surface,
    traducciones,
    origen, // 'manual' (clic en lectura) | 'auto' (volcado al elegir un texto)
    addedAt: addedAt ?? new Date().toISOString(),
    // El estado de repetición espaciada (caja de Leitner, factor SM-2, etc.)
    // lo añadirá el motor de la Sección 2 sobre esta misma entrada.
  };
}

export function tienePalabra(bolsa, id) {
  return bolsa.some((p) => p.id === id);
}

export function obtenerPalabra(bolsa, id) {
  return bolsa.find((p) => p.id === id);
}

/**
 * Agrega una entrada. Si su id ya existe, devuelve la bolsa SIN cambios para
 * conservar el estado acumulado de esa palabra.
 */
export function agregarPalabra(bolsa, entrada) {
  if (tienePalabra(bolsa, entrada.id)) return bolsa;
  return [...bolsa, entrada];
}

export function quitarPalabra(bolsa, id) {
  return bolsa.filter((p) => p.id !== id);
}

export function contar(bolsa) {
  return bolsa.length;
}
