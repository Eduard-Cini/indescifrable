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
          <p>Indescifrable: el Codenames con vocabulario en tres idiomas.</p>
        </Link>

        <div className="seccion-card proximamente">
          <h2>🗂️ Repaso</h2>
          <p>Repetición espaciada (Leitner / SM-2). Próximamente.</p>
        </div>

        <div className="seccion-card proximamente">
          <h2>✍️ Gramática</h2>
          <p>Ejercicios cloze a partir de los textos. Próximamente.</p>
        </div>
      </main>
    </div>
  );
}

export default Home;
