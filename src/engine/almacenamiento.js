// engine/almacenamiento.js
// Adaptador delgado (impuro) sobre localStorage para persistir la bolsa.
// Aislado del núcleo puro (bolsa.js) para mantener ese módulo testeable.

const CLAVE = 'bolsa.v1';

export function cargarBolsa() {
  if (typeof localStorage === 'undefined') return [];
  try {
    const crudo = localStorage.getItem(CLAVE);
    const datos = crudo ? JSON.parse(crudo) : [];
    return Array.isArray(datos) ? datos : [];
  } catch {
    return [];
  }
}

export function guardarBolsa(bolsa) {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.setItem(CLAVE, JSON.stringify(bolsa));
  } catch {
    // almacenamiento lleno o no disponible: degradamos en silencio
  }
}
