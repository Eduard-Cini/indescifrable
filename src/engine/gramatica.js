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
