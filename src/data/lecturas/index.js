// Catálogo de lecturas. Cada archivo JSON es una lectura trilingüe (es/en/de)
// con el mismo formato que más adelante emitirá el pipeline offline de Python.
import mercado01 from './principiante-01.json';
import diaDeAna from './principiante-02.json';
import finDeSemana from './principiante-03.json';
import leonYRaton from './intermedio-01.json';
import liebreYTortuga from './intermedio-02.json';
import hormigaYCigarra from './intermedio-03.json';
import sterntaler from './avanzado-01.json';
import ollaMagica from './avanzado-02.json';
import vientoYSol from './avanzado-03.json';
import rotkaeppchen from './avanzado-04.json';

export const NIVELES = ['principiante', 'intermedio', 'avanzado'];
export const IDIOMAS = ['es', 'en', 'de'];

export const NOMBRE_IDIOMA = { es: 'Español', en: 'English', de: 'Deutsch' };
export const NOMBRE_NIVEL = {
  principiante: 'Principiante',
  intermedio: 'Intermedio',
  avanzado: 'Avanzado',
};

export const lecturas = [
  mercado01,
  diaDeAna,
  finDeSemana,
  leonYRaton,
  liebreYTortuga,
  hormigaYCigarra,
  sterntaler,
  ollaMagica,
  vientoYSol,
  rotkaeppchen,
];

// Idiomas en los que existe una lectura (una lectura ya no tiene que ser
// trilingüe: puede ser de+es, en+es, etc.). El español actúa además como
// idioma de traducción, así que se asume siempre presente.
export function idiomasDisponibles(lectura) {
  return IDIOMAS.filter(
    (i) => Array.isArray(lectura.cuerpo?.[i]) && lectura.cuerpo[i].length > 0
  );
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
