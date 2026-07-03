import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  juegosDisponibles,
  lecturasOrdenadas,
  poolDe,
  SLUG_CORPUS,
} from '../../engine/juegos';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

const NOMBRE_NIVEL = { principiante: 'Principiante', intermedio: 'Intermedio', avanzado: 'Avanzado' };

// Hub de la Sección 4, organizado POR LECTURA (como la Sección 3): cada
// lectura del corpus es una tarjeta y dentro están los juegos que su
// vocabulario aguanta (src/engine/juegos.js decide cuáles). «Todo el corpus»
// juega con el léxico completo; el Codenames va aparte (usa sus propios
// diccionarios, no el corpus).
function Juegos() {
  const [datos, setDatos] = useState(null);

  useEffect(() => {
    let vivo = true;
    import('../../data/juegos.json').then((m) => {
      if (vivo) setDatos(m.default);
    });
    return () => {
      vivo = false;
    };
  }, []);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/" className="lectura-link">← Plataforma</Link>
      <h1>Juegos</h1>
      <span />
    </header>
  );

  if (!datos) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  const corpus = poolDe(datos, SLUG_CORPUS);

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        Juegos de palabras con el vocabulario de las lecturas: elige una
        lectura (o el corpus entero) y dentro verás los juegos que su
        vocabulario aguanta. Partidas reproducibles por semilla.
      </p>

      <div className="juegos-grid">
        <Link to="/juegos/codenames" className="juego-card">
          <h2>🕵️ Indescifrable</h2>
          <p>
            El Codenames con vocabulario en tres idiomas: pistas de una palabra
            para que tu equipo adivine sus casillas.
          </p>
          <span className="juego-algoritmo">Tablero determinista por LCG</span>
        </Link>

        <Link to={`/juegos/${SLUG_CORPUS}`} className="juego-card">
          <h2>📚 Todo el corpus</h2>
          <p>
            Los cuatro juegos de palabras sobre el léxico completo de la
            plataforma: el modo clásico.
          </p>
          <span className="juego-algoritmo">
            {juegosDisponibles(corpus).length} juegos disponibles
          </span>
        </Link>

        {lecturasOrdenadas(datos).map((lectura) => {
          const disponibles = juegosDisponibles(lectura);
          return (
            <Link key={lectura.slug} to={`/juegos/${lectura.slug}`} className="juego-card">
              <span className={`gram-nivel ${lectura.nivel}`}>
                {NOMBRE_NIVEL[lectura.nivel] ?? lectura.nivel}
              </span>
              <h2>{lectura.titulo}</h2>
              <span className="juego-algoritmo">
                {disponibles.length} juego{disponibles.length === 1 ? '' : 's'} disponible
                {disponibles.length === 1 ? '' : 's'}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default Juegos;
