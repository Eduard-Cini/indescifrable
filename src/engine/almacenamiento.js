// engine/almacenamiento.js
// Adaptador delgado (impuro) sobre localStorage para persistir la bolsa.
// Aislado del núcleo puro (bolsa.js) para mantener ese módulo testeable.

const CLAVE_BOLSA = 'bolsa.v1';
const CLAVE_PROGRESO = 'lecturas.completadas.v1';
const CLAVE_CONOCIDAS = 'conocidas.v1';
const CLAVE_REPASO_PREVIO = 'repasoPrevio.v1';
const CLAVE_GRAMATICA = 'gramatica.completados.v1';
const CLAVE_IDIOMA = 'idiomaEstudio.v1';

const IDIOMA_DEFECTO = 'de';

// Todo el estado persistente del usuario vive en estas claves. Un «perfil» es
// simplemente su serialización conjunta (exportarPerfil/importarPerfil), lo que
// permite copia de seguridad y portabilidad sin necesidad de un servidor.
const CLAVES_PERFIL = [
  CLAVE_BOLSA,
  CLAVE_PROGRESO,
  CLAVE_CONOCIDAS,
  CLAVE_REPASO_PREVIO,
  CLAVE_GRAMATICA,
  CLAVE_IDIOMA,
];

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

/** Claves estables (lectura|tema) de tandas de gramática TERMINADAS
 *  (ver claveGrupo en engine/gramatica.js; sobreviven a regenerar ids). */
export function cargarGramaticaCompletados() {
  return cargarArray(CLAVE_GRAMATICA);
}

export function guardarGramaticaCompletados(claves) {
  guardar(CLAVE_GRAMATICA, claves);
}

/** Idioma de estudio activo (gobierna Repaso, Bolsa y la Biblioteca). */
export function cargarIdiomaEstudio() {
  if (typeof localStorage === 'undefined') return IDIOMA_DEFECTO;
  try {
    const crudo = localStorage.getItem(CLAVE_IDIOMA);
    const v = crudo ? JSON.parse(crudo) : null;
    return typeof v === 'string' ? v : IDIOMA_DEFECTO;
  } catch {
    return IDIOMA_DEFECTO;
  }
}

export function guardarIdiomaEstudio(idioma) {
  guardar(CLAVE_IDIOMA, idioma);
}

// --- Perfil: exportar / importar todo el progreso (sin servidor) -------------
// El perfil viaja como un único objeto JSON con las claves crudas (ya
// serializadas), de modo que la ronda export→import es sin pérdidas.

export function exportarPerfil() {
  const datos = {};
  if (typeof localStorage !== 'undefined') {
    for (const clave of CLAVES_PERFIL) {
      const crudo = localStorage.getItem(clave);
      if (crudo != null) datos[clave] = crudo;
    }
  }
  return {
    app: 'indescifrable',
    tipo: 'perfil',
    version: 1,
    exportadoEn: new Date().toISOString(),
    datos,
  };
}

/**
 * Restaura un perfil exportado. Valida la envoltura y que cada valor sea JSON
 * válido antes de escribirlo; ignora claves desconocidas o corruptas. Devuelve
 * el número de claves restauradas.
 */
export function importarPerfil(objeto) {
  if (
    !objeto ||
    objeto.app !== 'indescifrable' ||
    objeto.tipo !== 'perfil' ||
    !objeto.datos ||
    typeof objeto.datos !== 'object'
  ) {
    throw new Error('El archivo no es un perfil de indescifrable válido.');
  }
  if (typeof localStorage === 'undefined') return 0;
  let restauradas = 0;
  for (const clave of CLAVES_PERFIL) {
    const crudo = objeto.datos[clave];
    if (typeof crudo !== 'string') continue;
    try {
      JSON.parse(crudo); // descarta valores corruptos sin tocar lo guardado
      localStorage.setItem(clave, crudo);
      restauradas += 1;
    } catch {
      // valor no parseable: se omite
    }
  }
  return restauradas;
}
