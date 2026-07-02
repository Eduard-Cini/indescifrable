import { Link } from 'react-router-dom';
import './home.css';

function Home() {
  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Plataforma de Idiomas</h1>
        <p>Aprende español, inglés y alemán leyendo, repasando y jugando.</p>
      </header>

      <main className="home-secciones">
        <Link to="/lectura" className="seccion-card lectura">
          <h2>📖 Lectura</h2>
          <p>Lee textos por nivel, consulta traducciones y arma tu bolsa de palabras.</p>
        </Link>

        <Link to="/juegos" className="seccion-card juegos">
          <h2>🎮 Juegos</h2>
          <p>Cinco juegos de palabras: Codenames, escalera (BFS), crucigrama (backtracking), adivina la palabra (entropía) y sopa de letras.</p>
        </Link>

        <Link to="/repaso" className="seccion-card repaso">
          <h2>🗂️ Repaso</h2>
          <p>Repetición espaciada (SM-2) sobre tu bolsa de palabras.</p>
        </Link>

        <Link to="/gramatica" className="seccion-card gramatica">
          <h2>✍️ Gramática</h2>
          <p>Ejercicios cloze de alemán por tema: declinación, casos, conjugación y verbos separables.</p>
        </Link>
      </main>
    </div>
  );
}

export default Home;
