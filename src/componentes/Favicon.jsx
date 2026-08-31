// Favicon dinámico por sección. El icono general del sitio es el castillo sobre
// el libro (public/favicon-castillo.png, generado por scripts/generar_identidad.py);
// el reptiliano original queda reservado para el juego Indescifrable, y cada
// sección muestra su emoji como SVG inline (sin archivos extra).
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const CASTILLO = '/favicon-castillo.png';
const REPTILIANO = '/faviconReptiliano.png';

// Prefijos de ruta en orden de especificidad (el primero que casa, gana).
const ICONOS = [
  ['/juegos/codenames', REPTILIANO],
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
    const regla = ICONOS.find(([prefijo]) => pathname.startsWith(prefijo));
    const icono = regla ? regla[1] : CASTILLO; // portada y rutas sin regla
    if (icono.startsWith('/')) {
      link.type = 'image/png';
      link.href = icono;
    } else {
      link.type = 'image/svg+xml';
      link.href = dataUri(icono);
    }
  }, [pathname]);

  return null;
}

export default Favicon;
