import { Link } from 'react-router-dom';
import SelectorIdioma from './componentes/SelectorIdioma';
import { useIdiomaEstudio } from './contexto/idiomaEstudio';
import { NOMBRE_IDIOMA } from './data/lecturas';
import './home.css';

function Home() {
  const { idioma } = useIdiomaEstudio();
  // El español (estudio para nativos) aún no tiene ejercicios de gramática ni
  // juegos de vocabulario: esas tarjetas se desactivan en vez de llevar a
  // contenido de otro idioma. El Indescifrable sí soporta español.
  const sinDatosEs = idioma === 'es';
  return (
    <div className="home-container">
      <header className="home-header">
        <h1>El castillo de la memoria</h1>
        <p className="home-sub">Plataforma de idiomas</p>
        <p>Aprende alemán e inglés — y amplía tu español — leyendo, repasando y jugando.</p>
        <div className="home-idioma">
          <SelectorIdioma />
          <span className="home-idioma-nota">
            Estudias <strong>{NOMBRE_IDIOMA[idioma]}</strong>: la lectura, la
            bolsa y el repaso se adaptan a este idioma.
          </span>
        </div>
      </header>

      <main className="home-secciones">
        <Link to="/lectura" className="seccion-card lectura">
          <h2>📖 Lectura</h2>
          <p>Lee textos por nivel, consulta traducciones y arma tu bolsa de palabras.</p>
        </Link>

        <Link to="/juegos" className="seccion-card juegos">
          <h2>🎮 Juegos</h2>
          <p>Cinco juegos de palabras: Codenames, escalera (BFS), crucigrama (backtracking), adivina la palabra (entropía) y sopa de letras.</p>
          {sinDatosEs && (
            <span className="seccion-nodisp">En español, solo el Indescifrable por ahora</span>
          )}
        </Link>

        <Link to="/repaso" className="seccion-card repaso">
          <h2>🗂️ Repaso</h2>
          <p>Repetición espaciada (SM-2) sobre tu bolsa de palabras.</p>
        </Link>

        {sinDatosEs ? (
          <div className="seccion-card gramatica deshabilitada" aria-disabled="true">
            <h2>✍️ Gramática</h2>
            <p>Ejercicios cloze por tema, adaptados a tu idioma de estudio, con distractores por similitud.</p>
            <span className="seccion-nodisp">No disponible en español todavía</span>
          </div>
        ) : (
          <Link to="/gramatica" className="seccion-card gramatica">
            <h2>✍️ Gramática</h2>
            <p>Ejercicios cloze por tema, adaptados a tu idioma de estudio, con distractores por similitud.</p>
          </Link>
        )}
      </main>
    </div>
  );
}

export default Home;
