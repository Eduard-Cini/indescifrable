import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { cargarBolsa, guardarBolsa } from '../../engine/almacenamiento';
import {
  CALIFICACIONES,
  calificar,
  seleccionarSesion,
  aplicarCalificacion,
  resumen,
} from '../../engine/srs';
import './repaso.css';

// Etiquetas de los 4 niveles en el orden en que se pintan los botones.
const NIVELES = [
  { clave: 'otraVez', texto: 'Otra vez' },
  { clave: 'dificil', texto: 'Difícil' },
  { clave: 'bien', texto: 'Bien' },
  { clave: 'facil', texto: 'Fácil' },
];

const NOMBRE_IDIOMA = { de: 'alemán', en: 'inglés', es: 'español' };

function etiquetaIntervalo(dias) {
  if (dias === 0) return 'ahora';
  if (dias === 1) return '1 día';
  if (dias < 30) return `${dias} días`;
  return `${Math.round(dias / 30)} mes(es)`;
}

function Repaso() {
  const [bolsa, setBolsa] = useState(null); // null mientras carga
  const [cola, setCola] = useState([]); // ids pendientes de la sesión
  const [volteada, setVolteada] = useState(false);
  const [hechas, setHechas] = useState(0);
  const [fallos, setFallos] = useState(0);

  useEffect(() => {
    const b = cargarBolsa();
    setBolsa(b);
    setCola(seleccionarSesion(b, new Date().toISOString()).map((p) => p.id));
  }, []);

  if (bolsa === null) return null;

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
      <Link to="/bolsa" className="lectura-link bolsa-badge">🎒 {bolsa.length}</Link>
    </header>
  );

  if (bolsa.length === 0) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Tu bolsa está vacía. Guarda palabras desde una{' '}
          <Link to="/lectura" className="lectura-link">lectura</Link> para
          empezar a repasar.
        </p>
      </div>
    );
  }

  if (!actual) {
    const r = resumen(bolsa, new Date().toISOString());
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
        <div className="repaso-botones">
          {NIVELES.map(({ clave, texto }) => (
            <button
              key={clave}
              type="button"
              className={`repaso-btn ${clave}`}
              onClick={() => graduar(clave)}
            >
              {texto}
              <span className="repaso-btn-intervalo">
                {etiquetaIntervalo(
                  calificar(
                    actual.srs,
                    CALIFICACIONES[clave],
                    new Date().toISOString()
                  ).intervalo
                )}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Repaso;
