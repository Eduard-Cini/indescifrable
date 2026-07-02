// engine/gramatica.js
// Núcleo puro de la Sección 3 (Gramática): selección de ejercicios cloze y
// barajado determinista de las opciones. Los ejercicios se generan offline con
// pipeline/gramatica.py (spaCy Matcher/DependencyMatcher para localizar el
// hueco; distractores híbridos: el paradigma morfológico define el CONJUNTO de
// candidatos y la similitud coseno de los vectores spaCy los ORDENA para quedarse
// con los k «hard negatives» más plausibles). Viven en src/data/gramatica.json.
//
// Este módulo no toca el DOM ni localStorage: solo transforma datos, para poder
// testearlo con Vitest igual que srs.js / leitner.js. El azar entra siempre por
// el LCG determinista de board.js, así que la salida es reproducible por semilla.

import { crearGenerador, barajar } from './board';

// crearGenerador de board.js puede devolver valores fuera de [0,1) (negativos
// cuando el hash de la semilla es negativo, o 1.0 en el borde), lo que haría a
// barajar leer índices fuera de rango. Tomamos la parte fraccionaria para
// garantizar [0,1) sin alterar board.js (usado por el tablero del juego).
function rngDeterminista(semilla) {
  const base = crearGenerador(String(semilla));
  return () => {
    const v = base();
    return v - Math.floor(v);
  };
}

/**
 * Opciones (respuesta + distractores) de un ejercicio, barajadas de forma
 * determinista a partir de una semilla. Un mismo ejercicio conserva su orden
 * entre renders (semilla = id por defecto) pero cada ejercicio baraja distinto.
 * Deduplica por si un distractor coincidiera con la respuesta.
 */
export function opcionesDe(ejercicio, semilla = ejercicio?.id ?? 'ej') {
  const crudas = [ejercicio.respuesta, ...(ejercicio.distractores ?? [])];
  const unicas = [...new Set(crudas)];
  return barajar(unicas, rngDeterminista(semilla));
}

/** ¿La opción elegida es la respuesta correcta del ejercicio? */
export function esCorrecta(ejercicio, opcion) {
  return opcion === ejercicio.respuesta;
}

// Dificultad de la lectura de origen; lo desconocido va al final.
const ORDEN_NIVEL = { principiante: 0, intermedio: 1, avanzado: 2 };

/**
 * Selecciona una sesión de hasta n ejercicios de un tema. La semilla decide
 * CUÁLES entran (barajado sin reemplazo, determinista); la presentación va en
 * orden pedagógico: nivel de la lectura de origen ascendente y, dentro del
 * nivel, agrupados por lectura (sort estable: conserva el orden de la semilla
 * entre iguales).
 */
export function seleccionarSesion(ejercicios, { n = 10, semilla = 'sesion' } = {}) {
  if (!Array.isArray(ejercicios) || ejercicios.length === 0) return [];
  const revueltos = barajar(ejercicios, rngDeterminista(semilla));
  return revueltos
    .slice(0, Math.max(0, n))
    .sort(
      (a, b) =>
        (ORDEN_NIVEL[a.nivel] ?? 9) - (ORDEN_NIVEL[b.nivel] ?? 9) ||
        String(a.fuente ?? '').localeCompare(String(b.fuente ?? ''))
    );
}

/** Slug de URL a partir del título de la lectura («Un día de Ana» → un-dia-de-ana). */
export function slugDeLectura(titulo) {
  return String(titulo)
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '') // fuera diacríticos combinantes (tras NFD)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Reorganiza gramatica.json por LECTURA: una entrada por lectura de origen,
 * ordenadas por nivel ascendente (y título dentro del nivel). Dentro de cada
 * lectura, los ejercicios quedan en SUBGRUPOS POR TEMA, en el orden (de
 * dificultad) en que los temas aparecen en data.temas: el usuario elige qué
 * tema practicar y cada tema se completa por separado.
 */
export function agruparPorLectura(data) {
  const grupos = new Map(); // fuente -> entrada
  for (const tema of data.temas) {
    for (const ej of data.ejercicios[tema.id] ?? []) {
      const titulo = String(ej.fuente ?? '').split('·')[1]?.trim() || ej.fuente || '?';
      let g = grupos.get(ej.fuente);
      if (!g) {
        g = {
          slug: slugDeLectura(titulo),
          titulo,
          nivel: ej.nivel,
          fuente: ej.fuente,
          temas: [],
        };
        grupos.set(ej.fuente, g);
      }
      let t = g.temas.find((x) => x.id === tema.id);
      if (!t) {
        t = { id: tema.id, titulo: tema.titulo, nivel: tema.nivel, ejercicios: [] };
        g.temas.push(t); // data.temas va por dificultad → los subgrupos también
      }
      t.ejercicios.push({ ...ej, tema: tema.id });
    }
  }
  return [...grupos.values()].sort(
    (a, b) =>
      (ORDEN_NIVEL[a.nivel] ?? 9) - (ORDEN_NIVEL[b.nivel] ?? 9) ||
      a.titulo.localeCompare(b.titulo)
  );
}

/** Total de ejercicios de una lectura, sumando sus temas. */
export function totalEjercicios(grupo) {
  return grupo.temas.reduce((s, t) => s + t.ejercicios.length, 0);
}

/**
 * Progreso: se marca por (lectura, tema) cuando el usuario TERMINA la tanda de
 * ese tema. La clave es estable frente a regenerar el corpus (no usa ids).
 */
export function claveGrupo(grupo, temaId) {
  return `${grupo.fuente}|${temaId}`;
}

export function temaCompletado(grupo, temaId, completados) {
  return completados.includes(claveGrupo(grupo, temaId));
}

/** Una lectura está completada cuando todos sus temas lo están. */
export function lecturaCompletada(grupo, completados) {
  const hechas = new Set(completados);
  return (
    grupo.temas.length > 0 &&
    grupo.temas.every((t) => hechas.has(claveGrupo(grupo, t.id)))
  );
}

/**
 * Resumen de una sesión a partir de la lista de resultados booleanos
 * (true = acierto). porcentaje redondeado a entero.
 */
export function resumenSesion(resultados) {
  const total = resultados.length;
  const aciertos = resultados.filter(Boolean).length;
  return {
    total,
    aciertos,
    fallos: total - aciertos,
    porcentaje: total ? Math.round((100 * aciertos) / total) : 0,
  };
}
