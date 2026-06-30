import { diccionarios } from '../data/diccionarios';

// Códigos compactos de 2 caracteres para incrustar el vocabulario en la semilla.
// Primera letra = idioma (S/E/D), segunda = nivel (E/P/I/A). XX = personalizado.
export const CODIGOS_DICCIONARIO = {
  es_es: 'SE',
  es_principiante: 'SP',
  es_intermedio: 'SI',
  es_avanzado: 'SA',
  en_es: 'EE',
  en_principiante: 'EP',
  en_intermedio: 'EI',
  en_avanzado: 'EA',
  de_es: 'DE',
  de_principiante: 'DP',
  de_intermedio: 'DI',
  de_avanzado: 'DA',
  personalizado: 'XX',
};

const VOCABULARIO_POR_CODIGO = Object.fromEntries(
  Object.entries(CODIGOS_DICCIONARIO).map(([k, v]) => [v, k])
);

const ALFABETO_SEMILLA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

export function crearGenerador(semilla) {
  let hash = 0;
  for (let i = 0; i < semilla.length; i++) {
    hash = semilla.charCodeAt(i) + ((hash << 5) - hash);
  }
  const m = 0x80000000;
  const a = 1103515245;
  const c = 12345;
  let state = hash || 1;
  return function () {
    state = (a * state + c) % m;
    return state / (m - 1);
  };
}

export function barajar(array, rng) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function generarSemillaAleatoria(longitud = 4) {
  return Array.from({ length: longitud }, () =>
    ALFABETO_SEMILLA[Math.floor(Math.random() * ALFABETO_SEMILLA.length)]
  ).join('');
}

export function componerSemilla(vocabulario, semillaAleatoria) {
  const codigo = CODIGOS_DICCIONARIO[vocabulario] ?? CODIGOS_DICCIONARIO.personalizado;
  return `${codigo}-${semillaAleatoria}`;
}

export function parsearSemilla(semillaCompleta) {
  if (typeof semillaCompleta !== 'string') return null;
  const limpia = semillaCompleta.trim().toUpperCase();
  const match = limpia.match(/^([A-Z]{2})-?([A-Z0-9]{4})$/);
  if (!match) return null;
  const [, codigo, semillaCorta] = match;
  const vocabulario = VOCABULARIO_POR_CODIGO[codigo];
  if (!vocabulario) return null;
  return {
    vocabulario,
    semillaCorta,
    semillaCompleta: `${codigo}-${semillaCorta}`,
  };
}

export function obtenerListaPalabras(vocabulario, palabrasPersonalizadas = '') {
  if (vocabulario === 'personalizado') {
    return palabrasPersonalizadas
      .split(/\s*,\s*/)
      .map(p => p.trim().toUpperCase())
      .filter(Boolean);
  }
  return diccionarios[vocabulario] ?? diccionarios.es_es;
}

export function generarTablero(semillaCorta, listaPalabras) {
  const rng = crearGenerador(semillaCorta);
  const empiezaVerde = rng() > 0.5;

  const indices = Array.from({ length: listaPalabras.length }, (_, i) => i);
  const indicesRevueltos = barajar(indices, rng);
  const palabrasTablero = indicesRevueltos.slice(0, 25).map(i => ({
    texto: listaPalabras[i],
    indiceOriginal: i,
  }));

  const colores = [
    ...Array(9).fill(empiezaVerde ? 'verde' : 'azul'),
    ...Array(8).fill(empiezaVerde ? 'azul' : 'verde'),
    ...Array(7).fill('beige'),
    'rojo',
  ];
  const mapaColores = barajar(colores, rng);

  return {
    empiezaVerde,
    equipoInicial: empiezaVerde ? 'Iluminatis (Verde)' : 'La MASA (Azul)',
    palabrasTablero,
    mapaColores,
  };
}
