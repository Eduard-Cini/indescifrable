// engine/progreso.js
// Lógica pura del progreso de lectura: qué lecturas ha finalizado el usuario.
// Se identifica cada lectura por su id. Sin DOM ni localStorage (eso vive en
// almacenamiento.js).

export function marcarCompletada(completadas, id) {
  return completadas.includes(id) ? completadas : [...completadas, id];
}

export function desmarcarCompletada(completadas, id) {
  return completadas.filter((x) => x !== id);
}

export function estaCompletada(completadas, id) {
  return completadas.includes(id);
}

/** Cuántas de una lista de ids están completadas. */
export function contarCompletadas(completadas, ids) {
  return ids.reduce((n, id) => (completadas.includes(id) ? n + 1 : n), 0);
}
