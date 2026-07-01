// engine/almacenamiento.js
// Adaptador delgado (impuro) sobre localStorage para persistir la bolsa.
// Aislado del núcleo puro (bolsa.js) para mantener ese módulo testeable.

const CLAVE_BOLSA = 'bolsa.v1';
const CLAVE_PROGRESO = 'lecturas.completadas.v1';

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

function guardarArray(clave, valor) {
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
  guardarArray(CLAVE_BOLSA, bolsa);
}

export function cargarProgreso() {
  return cargarArray(CLAVE_PROGRESO);
}

export function guardarProgreso(completadas) {
  guardarArray(CLAVE_PROGRESO, completadas);
}
