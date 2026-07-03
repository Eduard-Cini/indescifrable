// Ficha de presentación de cada juego de palabras (título, descripción y el
// algoritmo que lo genera). La usan el hub (/juegos) y el índice de
// vocabularios de cada juego (/juegos/:juego).
export const FICHAS = {
  escalera: {
    titulo: '🪜 Escalera de palabras',
    nombre: 'Escalera de palabras',
    descripcion:
      'Transforma una palabra alemana en otra cambiando una sola letra por ' +
      'paso. ¿Igualas el camino mínimo?',
    algoritmo: 'Grafo de Hamming 1 + BFS',
  },
  crucigrama: {
    titulo: '✏️ Crucigrama',
    nombre: 'Crucigrama',
    descripcion: 'Palabras alemanas entrelazadas; las pistas, en español.',
    algoritmo: 'Colocación por backtracking',
  },
  wordle: {
    titulo: '🎯 Adivina la palabra',
    nombre: 'Adivina la palabra',
    descripcion:
      'Una palabra alemana en seis intentos, con la traducción de cada ' +
      'intento y el conteo de candidatas.',
    algoritmo: 'Feedback exacto + entropía de Shannon',
  },
  sopa: {
    titulo: '🔍 Sopa de letras',
    nombre: 'Sopa de letras',
    descripcion:
      'Las pistas en español, las palabras escondidas en alemán: encontrar ' +
      '«regalo» es encontrar GESCHENK.',
    algoritmo: 'Colocación aleatorizada por semilla',
  },
};
