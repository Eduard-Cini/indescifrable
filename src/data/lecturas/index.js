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
];

export function lecturasPorNivel(nivel) {
  return lecturas.filter((l) => l.nivel === nivel);
}

export function obtenerLectura(id) {
  return lecturas.find((l) => l.id === id);
}
