import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { lecturasConJuego } from '../../engine/juegos';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import { FICHAS } from './fichas';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

// Hub de la Sección 4, organizado POR JUEGO: cada juego es una tarjeta y
// dentro se elige el vocabulario (todo el corpus o una lectura concreta;
// solo se listan las lecturas que el juego aguanta, según los criterios de
// src/engine/juegos.js). El Codenames va aparte (usa sus propios
// diccionarios, no el corpus).
function Juegos() {
  const { idioma } = useIdiomaEstudio();
  const [datos, setDatos] = useState(null);

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
      <Link to="/" className="lectura-link">← Plataforma</Link>
      <h1>Juegos</h1>
      <span />
    </header>
  );

  if (!datos) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        Juegos de palabras con el vocabulario de las lecturas: elige un juego
        y, dentro, la lectura con la que quieres jugar (o el corpus entero).
        Partidas reproducibles por semilla.
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

        {Object.entries(FICHAS).map(([juego, ficha]) => {
          const lecturas = lecturasConJuego(datos, juego);
          return (
            <Link key={juego} to={`/juegos/${juego}`} className="juego-card">
              <h2>{ficha.titulo}</h2>
              <p>{ficha.descripcion}</p>
              <span className="juego-algoritmo">
                {ficha.algoritmo} · corpus + {lecturas.length} lectura
                {lecturas.length === 1 ? '' : 's'}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default Juegos;
