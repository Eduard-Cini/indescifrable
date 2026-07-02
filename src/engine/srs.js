// engine/srs.js
// Planificador de repaso espaciado: SM-2 (SuperMemo-2, Wozniak 1990).
//
// Modelo de la tesis: el estado de cada palabra evoluciona con la recurrencia
//   EF' = max(1.3, EF + 0.1 − (5−q)·(0.08 + (5−q)·0.02))
//   I(1) = 1, I(2) = 6, I(n) = round(I(n−1) · EF)      si q ≥ 3
//   I = 0 (repetir hoy) y n = 0                        si q < 3
// donde q ∈ {2,3,4,5} es la calificación del usuario (4 niveles estilo Anki).
// SM-2 gobierna la UI; Leitner (cadena de Markov) se compara fuera de
// producción por simulación (próxima iteración).
//
// El estado vive dentro de cada entrada de la bolsa bajo la clave `srs`
// (una entrada sin `srs` es una palabra "nueva"). Módulo puro: el tiempo
// `ahora` se inyecta siempre (ISO string) para que las pruebas y la futura
// simulación sean deterministas. La persistencia sigue en almacenamiento.js.

const MS_POR_DIA = 24 * 60 * 60 * 1000;
const EF_INICIAL = 2.5;
const EF_MINIMO = 1.3;

/** Los 4 niveles de la UI mapeados a la calidad q de SM-2 (q<3 = fallo). */
export const CALIFICACIONES = {
  otraVez: 2,
  dificil: 3,
  bien: 4,
  facil: 5,
};

/** Estado SRS de una palabra recién incorporada al repaso. */
export function estadoInicial(ahora) {
  return {
    reps: 0, // repeticiones correctas consecutivas (n de SM-2)
    ef: EF_INICIAL, // factor de facilidad
    intervalo: 0, // días hasta el próximo repaso
    vencimiento: ahora, // ISO: cuándo vuelve a estar pendiente
    repasos: 0, // total de calificaciones recibidas (estadística)
    fallos: 0, // total de q<3 (lapsos)
  };
}

function nuevoEf(ef, q) {
  return Math.max(EF_MINIMO, ef + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
}

function sumarDias(iso, dias) {
  return new Date(Date.parse(iso) + dias * MS_POR_DIA).toISOString();
}

/**
 * Aplica una calificación q al estado `srs` en el instante `ahora`.
 * Devuelve el nuevo estado sin mutar el anterior.
 * EF se actualiza en toda respuesta (también en fallos), con suelo 1.3.
 */
export function calificar(srs, q, ahora) {
  const base = srs ?? estadoInicial(ahora);
  const ef = nuevoEf(base.ef, q);

  if (q < 3) {
    // Fallo: la palabra vuelve al principio y se repite en la misma sesión.
    return {
      ...base,
      reps: 0,
      ef,
      intervalo: 0,
      vencimiento: ahora,
      repasos: base.repasos + 1,
      fallos: base.fallos + 1,
    };
  }

  const reps = base.reps + 1;
  const intervalo =
    reps === 1 ? 1 : reps === 2 ? 6 : Math.round(base.intervalo * ef);
  return {
    ...base,
    reps,
    ef,
    intervalo,
    vencimiento: sumarDias(ahora, intervalo),
    repasos: base.repasos + 1,
    fallos: base.fallos,
  };
}

/** ¿La entrada está pendiente de repaso en `ahora`? (nueva o vencida) */
export function estaPendiente(entrada, ahora) {
  if (!entrada.srs) return true;
  return Date.parse(entrada.srs.vencimiento) <= Date.parse(ahora);
}

/** ¿Se puede repasar? Sin traducción al español no hay reverso de tarjeta. */
export function esRepasable(entrada) {
  return Boolean(entrada.traducciones?.es);
}

/**
 * Construye la cola de una sesión: primero las vencidas (la más atrasada
 * primero), después las nuevas (orden de incorporación, tope `maxNuevas`).
 */
export function seleccionarSesion(bolsa, ahora, { maxNuevas = 10 } = {}) {
  const repasables = bolsa.filter(esRepasable);
  const vencidas = repasables
    .filter((p) => p.srs && estaPendiente(p, ahora))
    .sort((a, b) => Date.parse(a.srs.vencimiento) - Date.parse(b.srs.vencimiento));
  const nuevas = repasables
    .filter((p) => !p.srs)
    .sort((a, b) => Date.parse(a.addedAt) - Date.parse(b.addedAt))
    .slice(0, maxNuevas);
  return [...vencidas, ...nuevas];
}

/**
 * Califica la palabra `id` dentro de la bolsa y devuelve la bolsa nueva.
 * El resto de la entrada (traducciones, origen, …) queda intacto.
 */
export function aplicarCalificacion(bolsa, id, q, ahora) {
  return bolsa.map((p) =>
    p.id === id ? { ...p, srs: calificar(p.srs, q, ahora) } : p
  );
}

/** Conteos para cabeceras y badges: nuevas, vencidas y programadas a futuro. */
export function resumen(bolsa, ahora) {
  const repasables = bolsa.filter(esRepasable);
  const nuevas = repasables.filter((p) => !p.srs).length;
  const vencidas = repasables.filter(
    (p) => p.srs && estaPendiente(p, ahora)
  ).length;
  return {
    nuevas,
    vencidas,
    programadas: repasables.length - nuevas - vencidas,
    sinTraduccion: bolsa.length - repasables.length,
  };
}
