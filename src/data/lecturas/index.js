// Catálogo de lecturas. Cada archivo JSON de esta carpeta es una lectura
// (es/en/de o un subconjunto) con el mismo formato que emite el pipeline
// offline de Python. Se cargan automáticamente con import.meta.glob, así que
// añadir lecturas (a mano o desde el pipeline) no requiere tocar este archivo.
// Fábulas y cuentos son intermedio; el avanzado son libros procesados con spaCy.

const modulos = import.meta.glob('./*.json', { eager: true, import: 'default' });

export const NIVELES = ['principiante', 'intermedio', 'avanzado'];
export const IDIOMAS = ['es', 'en', 'de'];

export const NOMBRE_IDIOMA = { es: 'Español', en: 'English', de: 'Deutsch' };
export const NOMBRE_NIVEL = {
  principiante: 'Principiante',
  intermedio: 'Intermedio',
  avanzado: 'Avanzado',
};

// Orden estable por nombre de archivo (principiante-01, intermedio-01, …).
export const lecturas = Object.keys(modulos)
  .sort()
  .map((ruta) => modulos[ruta]);

// Idiomas de ESTUDIO de una lectura. El de/en están disponibles si hay cuerpo.
// El español es lengua de estudio SOLO cuando es el original (no hay de/en): en
// las lecturas de/en el español es la traducción-pivote, no un texto a estudiar.
export function idiomasDisponibles(lectura) {
  const cuerpo = lectura.cuerpo ?? {};
  const tiene = (i) => Array.isArray(cuerpo[i]) && cuerpo[i].length > 0;
  const estudio = ['de', 'en'].filter(tiene);
  if (estudio.length === 0 && tiene('es')) estudio.push('es');
  return estudio;
}

export function lecturasPorNivel(nivel) {
  return lecturas.filter((l) => l.nivel === nivel);
}

// Lecturas de un nivel disponibles en el idioma de estudio elegido.
export function lecturasDisponibles(nivel, idioma) {
  return lecturas.filter(
    (l) => l.nivel === nivel && idiomasDisponibles(l).includes(idioma)
  );
}

export function obtenerLectura(id) {
  return lecturas.find((l) => l.id === id);
}

// Partes de un libro, ordenadas por número de parte.
export function partesDeLibro(libroId) {
  return lecturas
    .filter((l) => l.libro === libroId)
    .sort((a, b) => a.parte - b.parte);
}

// Agrupa una lista de lecturas: las partes de un mismo libro colapsan en una
// sola entrada { tipo: 'libro', ... }; el resto quedan como { tipo: 'lectura' }.
export function agruparPorLibro(lista) {
  const salida = [];
  const indice = new Map();
  for (const l of lista) {
    if (l.libro) {
      if (!indice.has(l.libro)) {
        indice.set(l.libro, salida.length);
        salida.push({
          tipo: 'libro',
          id: l.libro,
          titulo: l.titulo,
          autor: l.autor,
          nivel: l.nivel,
          partes: [],
        });
      }
      salida[indice.get(l.libro)].partes.push(l);
    } else {
      salida.push({ tipo: 'lectura', lectura: l });
    }
  }
  for (const e of salida) {
    if (e.tipo === 'libro') e.partes.sort((a, b) => a.parte - b.parte);
  }
  return salida;
}
