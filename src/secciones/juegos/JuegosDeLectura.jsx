import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { juegosDisponibles, poolDe } from '../../engine/juegos';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

const NOMBRE_NIVEL = { principiante: 'Principiante', intermedio: 'Intermedio', avanzado: 'Avanzado' };

// Ficha de cada juego para el índice; el orden lo decide juegosDisponibles.
const FICHAS = {
  escalera: {
    titulo: '🪜 Escalera de palabras',
    descripcion:
      'Transforma una palabra en otra cambiando una sola letra por paso. ' +
      '¿Igualas el camino mínimo?',
    algoritmo: 'Grafo de Hamming 1 + BFS',
  },
  crucigrama: {
    titulo: '✏️ Crucigrama',
    descripcion: 'Palabras alemanas entrelazadas; las pistas, en español.',
    algoritmo: 'Colocación por backtracking',
  },
  wordle: {
    titulo: '🎯 Adivina la palabra',
    descripcion:
      'Una palabra alemana en seis intentos, con la traducción de cada ' +
      'intento y el conteo de candidatas.',
    algoritmo: 'Feedback exacto + entropía de Shannon',
  },
  sopa: {
    titulo: '🔍 Sopa de letras',
    descripcion:
      'Las pistas en español, las palabras escondidas en alemán: encontrar ' +
      '«regalo» es encontrar GESCHENK.',
    algoritmo: 'Colocación aleatorizada por semilla',
  },
};

// Índice de juegos de UNA lectura (o del corpus): el equivalente al índice de
// temas de la Sección 3. Solo aparecen los juegos que el vocabulario de la
// lectura aguanta según los criterios de src/engine/juegos.js.
function JuegosDeLectura() {
  const { lectura } = useParams();
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

  const pool = datos ? poolDe(datos, lectura) : null;

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos" className="lectura-link">← Juegos</Link>
      <h1>{pool?.titulo ?? 'Juegos'}</h1>
      {pool?.nivel ? (
        <span className={`gram-nivel ${pool.nivel}`}>
          {NOMBRE_NIVEL[pool.nivel] ?? pool.nivel}
        </span>
      ) : (
        <span />
      )}
    </header>
  );

  if (!datos) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  if (!pool) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          No hay juegos para esa lectura.{' '}
          <Link to="/juegos" className="lectura-link">Volver a Juegos</Link>.
        </p>
      </div>
    );
  }

  const disponibles = juegosDisponibles(pool);

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        Juegos con el vocabulario de esta lectura. Los que su vocabulario no
        aguanta (pocas palabras, grafo sin caminos) no aparecen.
      </p>

      <div className="juegos-grid">
        {disponibles.map((juego) => (
          <Link key={juego} to={`/juegos/${pool.slug}/${juego}`} className="juego-card">
            <h2>{FICHAS[juego].titulo}</h2>
            <p>{FICHAS[juego].descripcion}</p>
            <span className="juego-algoritmo">{FICHAS[juego].algoritmo}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default JuegosDeLectura;
