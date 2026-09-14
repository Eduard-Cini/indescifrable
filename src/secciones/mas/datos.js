// Material de «Más contenidos» (Netzwerk neu B1), cargado con dynamic import:
// cada JSON de src/data/mas viaja en su propio chunk. El catálogo (indice.json)
// dice qué capítulos, temas y mazos hay; los archivos siguen una convención
// de nombres (mazo-<id>, leccion-<id>, ejercicios-<id>).
import { combinarMazos } from '../../engine/mazos';

const ARCHIVOS = import.meta.glob('../../data/mas/*.json');

// Nombre desconocido → null (la vista muestra «no encontrado» en vez de romperse).
function cargarArchivo(nombre) {
  const importar = ARCHIVOS[`../../data/mas/${nombre}.json`];
  return importar ? importar().then((m) => m.default) : Promise.resolve(null);
}

export const cargarIndice = () => cargarArchivo('indice');
export const cargarLeccion = (id) => cargarArchivo(`leccion-${id}`);
export const cargarEjercicios = (id) => cargarArchivo(`ejercicios-${id}`);

/** Mazo con sus fichas y las de los mazos que declara en `incluye`. */
export async function cargarMazo(id) {
  const mazo = await cargarArchivo(`mazo-${id}`);
  if (!mazo?.incluye?.length) return mazo;
  const incluidos = await Promise.all(mazo.incluye.map((i) => cargarArchivo(`mazo-${i}`)));
  return combinarMazos(mazo, incluidos.filter(Boolean));
}
