// engine/almacenamiento.js
// Adaptador delgado (impuro) sobre localStorage para persistir la bolsa.
// Aislado del núcleo puro (bolsa.js) para mantener ese módulo testeable.

const CLAVE_BOLSA = 'bolsa.v1';
const CLAVE_PROGRESO = 'lecturas.completadas.v1';
const CLAVE_CONOCIDAS = 'conocidas.v1';
const CLAVE_REPASO_PREVIO = 'repasoPrevio.v1';

function cargarArray(clave) {
  if (typeof localStorage === 'undefined') return [];
  try {
    const crudo = localStorage.getItem(clave);
    const datos = crudo ? JSON.parse(crudo) : [];
    return Array.isArray(datos) ? datos : [];
  } catch {
    return [];
  }
}

function guardar(clave, valor) {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch {
    // almacenamiento lleno o no disponible: degradamos en silencio
  }
}

export function cargarBolsa() {
  return cargarArray(CLAVE_BOLSA);
}

export function guardarBolsa(bolsa) {
  guardar(CLAVE_BOLSA, bolsa);
}

export function cargarProgreso() {
  return cargarArray(CLAVE_PROGRESO);
}

export function guardarProgreso(completadas) {
  guardar(CLAVE_PROGRESO, completadas);
}

function cargarObjeto(clave) {
  if (typeof localStorage === 'undefined') return {};
  try {
    const crudo = localStorage.getItem(clave);
    const datos = crudo ? JSON.parse(crudo) : {};
    return datos && typeof datos === 'object' && !Array.isArray(datos) ? datos : {};
  } catch {
    return {};
  }
}

/** Ids de palabras que el usuario marcó como «ya la conocía» (repaso previo). */
export function cargarConocidas() {
  return cargarArray(CLAVE_CONOCIDAS);
}

export function guardarConocidas(ids) {
  guardar(CLAVE_CONOCIDAS, ids);
}

/** Mapa lecturaId → fecha ISO del último repaso previo mostrado. */
export function cargarRepasoPrevio() {
  return cargarObjeto(CLAVE_REPASO_PREVIO);
}

export function guardarRepasoPrevio(mapa) {
  guardar(CLAVE_REPASO_PREVIO, mapa);
}
