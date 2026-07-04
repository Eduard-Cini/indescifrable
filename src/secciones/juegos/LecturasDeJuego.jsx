import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { lecturasConJuego, SLUG_CORPUS } from '../../engine/juegos';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import { FICHAS } from './fichas';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

const NOMBRE_NIVEL = { principiante: 'Principiante', intermedio: 'Intermedio', avanzado: 'Avanzado' };

// Índice de vocabularios de UN juego: «Todo el corpus» más las lecturas cuyo
// vocabulario lo aguanta (criterios formales de src/engine/juegos.js — una
// lectura de principiante no aparece en la escalera porque su grafo no tiene
// caminos, pero sí en crucigrama y sopa). Cada tarjeta lleva a
// /juegos/:juego/:lectura.
function LecturasDeJuego({ juego }) {
  const { idioma } = useIdiomaEstudio();
  const [datos, setDatos] = useState(null);
  const ficha = FICHAS[juego];

  useEffect(() => {
    let vivo = true;
    import('../../data/juegos.json').then((m) => {
      if (vivo) setDatos(m.default[idioma] ?? m.default.de);
    });
    return () => {
      vivo = false;
    };
  }, [idioma]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos" className="lectura-link">← Juegos</Link>
      <h1>{ficha.nombre}</h1>
      <span />
    </header>
  );

  if (!datos) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  const lecturas = lecturasConJuego(datos, juego);

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        {ficha.descripcion} Elige el vocabulario: solo se listan las lecturas
        que dan para este juego.
      </p>

      <div className="juegos-grid">
        <Link to={`/juegos/${juego}/${SLUG_CORPUS}`} className="juego-card">
          <h2>📚 Todo el corpus</h2>
          <p>El léxico completo de la plataforma: el modo clásico.</p>
          <span className="juego-algoritmo">{ficha.algoritmo}</span>
        </Link>

        {lecturas.map((lectura) => (
          <Link
            key={lectura.slug}
            to={`/juegos/${juego}/${lectura.slug}`}
            className="juego-card"
          >
            <span className={`gram-nivel ${lectura.nivel}`}>
              {NOMBRE_NIVEL[lectura.nivel] ?? lectura.nivel}
            </span>
            <h2>{lectura.titulo}</h2>
            <span className="juego-algoritmo">
              {juego === 'sudoku'
                ? `${lectura.sudoku.length} palabra${lectura.sudoku.length === 1 ? '' : 's'} de 9 letras`
                : `${lectura.crucigrama.length} palabras con pista`}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default LecturasDeJuego;
