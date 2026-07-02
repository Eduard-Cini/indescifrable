import { Link } from 'react-router-dom';
import '../lectura/lectura.css';
import './juegos.css';

// Hub de la Sección 4: cada juego de palabras con el algoritmo que lo genera.
function Juegos() {
  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/" className="lectura-link">← Plataforma</Link>
        <h1>Juegos</h1>
        <span />
      </header>
      <p className="lectura-subtitulo">
        Juegos de palabras generados con los algoritmos de la plataforma: mismo
        vocabulario que las lecturas, partidas reproducibles por semilla.
      </p>

      <div className="juegos-grid">
        <Link to="/juegos/codenames" className="juego-card">
          <h2>🕵️ Indescifrable</h2>
          <p>
            El Codenames con vocabulario en tres idiomas: pistas de una palabra
            para que tu equipo adivine sus casillas. Comparte la semilla y todos
            ven el mismo tablero.
          </p>
          <span className="juego-algoritmo">Tablero determinista por LCG</span>
        </Link>

        <Link to="/juegos/escalera" className="juego-card">
          <h2>🪜 Escalera de palabras</h2>
          <p>
            Transforma una palabra alemana en otra cambiando una sola letra por
            paso, pisando siempre palabras del corpus. ¿Igualas el camino
            mínimo?
          </p>
          <span className="juego-algoritmo">Grafo de Hamming 1 + BFS</span>
        </Link>

        <Link to="/juegos/crucigrama" className="juego-card">
          <h2>✏️ Crucigrama</h2>
          <p>
            Crucigrama de alemán con las pistas en español, armado con las
            palabras más frecuentes de las lecturas.
          </p>
          <span className="juego-algoritmo">Colocación por backtracking</span>
        </Link>
      </div>
    </div>
  );
}

export default Juegos;
