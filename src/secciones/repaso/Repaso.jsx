import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { cargarBolsa, guardarBolsa } from '../../engine/almacenamiento';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import SelectorIdioma from '../../componentes/SelectorIdioma';
import {
  CALIFICACIONES,
  seleccionarSesion,
  aplicarCalificacion,
  resumen,
} from '../../engine/srs';
import BotonesCalificacion from './BotonesCalificacion';
import './repaso.css';

const NOMBRE_IDIOMA = { de: 'alemán', en: 'inglés', es: 'español' };

function Repaso() {
  const { idioma } = useIdiomaEstudio();
  const [bolsa, setBolsa] = useState(null); // bolsa COMPLETA (todos los idiomas)
  const [cola, setCola] = useState([]); // ids pendientes de la sesión
  const [volteada, setVolteada] = useState(false);
  const [hechas, setHechas] = useState(0);
  const [fallos, setFallos] = useState(0);

  // La sesión se arma solo con las palabras del idioma de estudio, pero se
  // conserva la bolsa completa para no perder el otro idioma al persistir.
  useEffect(() => {
    const b = cargarBolsa();
    setBolsa(b);
    const delIdioma = b.filter((p) => p.lang === idioma);
    setCola(seleccionarSesion(delIdioma, new Date().toISOString()).map((p) => p.id));
    setHechas(0);
    setFallos(0);
    setVolteada(false);
  }, [idioma]);

  if (bolsa === null) return null;

  const bolsaIdioma = bolsa.filter((p) => p.lang === idioma);
  const actual = bolsa.find((p) => p.id === cola[0]);

  const graduar = (clave) => {
    const q = CALIFICACIONES[clave];
    const ahora = new Date().toISOString();
    const nueva = aplicarCalificacion(bolsa, actual.id, q, ahora);
    setBolsa(nueva);
    guardarBolsa(nueva);
    if (q < 3) {
      // La fallada se repite al final de la misma sesión.
      setCola([...cola.slice(1), actual.id]);
      setFallos(fallos + 1);
    } else {
      setCola(cola.slice(1));
      setHechas(hechas + 1);
    }
    setVolteada(false);
  };

  const cabecera = (
    <header className="lectura-top">
      <Link to="/" className="lectura-link">← Plataforma</Link>
      <h1>Repaso</h1>
      <div className="repaso-top-acciones">
        <SelectorIdioma />
        <Link to="/bolsa" className="lectura-link bolsa-badge">🎒 {bolsaIdioma.length}</Link>
      </div>
    </header>
  );

  if (bolsaIdioma.length === 0) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          No tienes palabras en {NOMBRE_IDIOMA[idioma] ?? idioma} en tu bolsa.
          Guarda palabras desde una{' '}
          <Link to="/lectura" className="lectura-link">lectura</Link> o cambia el
          idioma de estudio arriba.
        </p>
      </div>
    );
  }

  if (!actual) {
    const r = resumen(bolsaIdioma, new Date().toISOString());
    return (
      <div className="lectura-container">
        {cabecera}
        {hechas > 0 ? (
          <div className="repaso-fin">
            <p className="repaso-fin-titulo">Sesión terminada 🎉</p>
            <p className="repaso-fin-stats">
              {hechas} palabra(s) repasada(s)
              {fallos > 0 && ` · ${fallos} fallo(s) por el camino`}.
            </p>
            <p className="lectura-subtitulo">
              {r.programadas} palabra(s) programadas para los próximos días.
            </p>
          </div>
        ) : (
          <p className="lectura-subtitulo">
            Todo al día: no hay palabras pendientes. {r.programadas} palabra(s)
            programadas volverán cuando les toque.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        {cola.length} pendiente(s) en esta sesión · palabra en{' '}
        {NOMBRE_IDIOMA[actual.lang] ?? actual.lang}
      </p>

      <button
        type="button"
        className={`repaso-tarjeta${volteada ? ' volteada' : ''}`}
        onClick={() => setVolteada(true)}
      >
        <span className="repaso-idioma">{actual.lang.toUpperCase()}</span>
        <span className="repaso-anverso">
          {actual.surface}
          {actual.lemma &&
            actual.lemma.toLowerCase() !== actual.surface.toLowerCase() && (
              <span className="repaso-lemma"> ({actual.lemma})</span>
            )}
        </span>
        {volteada ? (
          <span className="repaso-reverso">{actual.traducciones.es}</span>
        ) : (
          <span className="repaso-pista">toca para ver la traducción</span>
        )}
      </button>

      {volteada && (
        <BotonesCalificacion srs={actual.srs} onCalificar={graduar} />
      )}
    </div>
  );
}

export default Repaso;
