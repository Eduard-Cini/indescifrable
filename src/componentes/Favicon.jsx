// Favicon dinámico por sección: el icono reptiliano original queda reservado
// para el juego Indescifrable (Codenames); las demás secciones usan su emoji
// (como SVG inline, sin archivos extra) y la portada lleva el camello 🐪.
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// href original de index.html (el reptiliano), capturado antes de tocarlo.
const ORIGINAL = document.querySelector("link[rel~='icon']")?.href ?? null;

// Prefijos de ruta en orden de especificidad (el primero que casa, gana).
// null = conservar el favicon original.
const EMOJIS = [
  ['/juegos/codenames', null],
  ['/juegos/escalera', '🪜'],
  ['/juegos/crucigrama', '✏️'],
  ['/juegos/wordle', '🎯'],
  ['/juegos/sopa', '🔍'],
  ['/juegos/sudoku', '🧩'],
  ['/juegos', '🎮'],
  ['/lectura', '📖'],
  ['/bolsa', '🎒'],
  ['/repaso', '🗂️'],
  ['/gramatica', '✍️'],
];

function dataUri(emoji) {
  const svg =
    `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>` +
    `<text y='.9em' font-size='88'>${emoji}</text></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

function Favicon() {
  const { pathname } = useLocation();

  useEffect(() => {
    const link = document.querySelector("link[rel~='icon']");
    if (!link) return;
    const regla = EMOJIS.find(([prefijo]) => pathname.startsWith(prefijo));
    const emoji = regla ? regla[1] : '🐪'; // portada y rutas sin regla
    if (emoji === null) {
      if (ORIGINAL) {
        link.type = 'image/png';
        link.href = ORIGINAL;
      }
    } else {
      link.type = 'image/svg+xml';
      link.href = dataUri(emoji);
    }
  }, [pathname]);

  return null;
}

export default Favicon;
