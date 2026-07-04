import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  evaluar,
  esVictoria,
  elegirSecreto,
  filtrarConsistentes,
} from '../../engine/wordle';
import { longitudesWordle, poolDe } from '../../engine/juegos';
import { generarSemillaAleatoria } from '../../engine/board';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

const MAX_INTENTOS = 6;

// Adivina la palabra (Sección 4): Wordle sobre el vocabulario alemán del pool
// (todo el corpus o UNA lectura, según la ruta). Los intentos deben ser
// palabras del pool (así cada intento enseña: se muestra su traducción) y el
// contador de candidatas consistentes hace visible la teoría de la
// información del juego (engine/wordle.js). Solo se ofrecen longitudes con
// diccionario suficiente (engine/juegos.js).
function Wordle() {
  const { lectura } = useParams();
  const { idioma } = useIdiomaEstudio();
  const [datos, setDatos] = useState(null);
  const [longitud, setLongitud] = useState('4');
  const [semilla, setSemilla] = useState(() => generarSemillaAleatoria());
  const [intentos, setIntentos] = useState([]);
  const [entrada, setEntrada] = useState('');
  const [aviso, setAviso] = useState(null);
  const [rendido, setRendido] = useState(false);
  const [conPista, setConPista] = useState(false);

  useEffect(() => {
    let vivo = true;
    import('../../data/juegos.json').then((m) => {
      if (vivo) setDatos(m.default[idioma] ?? m.default.de);
    });
    return () => {
      vivo = false;
    };
  }, [idioma]);

  const pool = datos ? poolDe(datos, lectura) : null;
  const longitudes = useMemo(
    () => (pool ? longitudesWordle(pool.escalera) : []),
    [pool]
  );
  const longitudActiva = longitudes.includes(longitud) ? longitud : longitudes[0];
  const glosas = pool?.escalera[longitudActiva] ?? null;
  const palabras = useMemo(() => (glosas ? Object.keys(glosas) : []), [glosas]);
  const enDiccionario = useMemo(() => new Set(palabras), [palabras]);
  const secreto = useMemo(
    () =>
      palabras.length > 0
        ? elegirSecreto(palabras, `${lectura}:${longitudActiva}:${semilla}`)
        : null,
    [palabras, longitudActiva, semilla, lectura]
  );

  useEffect(() => {
    setIntentos([]);
    setEntrada('');
    setAviso(null);
    setRendido(false);
    setConPista(false);
  }, [secreto]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos/wordle" className="lectura-link">← Lecturas</Link>
      <h1>Adivina la palabra</h1>
      {pool ? (
        <span className={`gram-nivel ${pool.nivel ?? ''}`}>{pool.titulo}</span>
      ) : (
        <span />
      )}
    </header>
  );

  if (datos && (!pool || longitudes.length === 0)) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Este vocabulario no da para adivinar la palabra (pocas candidatas).{' '}
          <Link to="/juegos/wordle" className="lectura-link">Elegir otra lectura</Link>.
        </p>
      </div>
    );
  }

  if (!secreto) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  const ganado = intentos.length > 0 && esVictoria(intentos.at(-1).resultado);
  const perdido = !ganado && intentos.length >= MAX_INTENTOS;
  const terminado = ganado || perdido || rendido;
  const candidatas = filtrarConsistentes(palabras, intentos);

  const intentar = (e) => {
    e.preventDefault();
    if (terminado) return;
    const palabra = entrada.trim().toLowerCase();
    if (palabra.length !== Number(longitudActiva)) {
      setAviso(`La palabra tiene ${longitudActiva} letras.`);
      return;
    }
    if (!enDiccionario.has(palabra)) {
      setAviso(`«${palabra}» no está en el vocabulario de las lecturas.`);
      return;
    }
    setIntentos([...intentos, { intento: palabra, resultado: evaluar(secreto, palabra) }]);
    setEntrada('');
    setAviso(null);
  };

  const nuevaPalabra = () => setSemilla(generarSemillaAleatoria());

  return (
    <div className="lectura-container">
      {cabecera}

      <div className="juego-config">
        <label>
          Letras{' '}
          <select
            className="juego-select"
            value={longitudActiva}
            onChange={(e) => setLongitud(e.target.value)}
          >
            {longitudes.map((L) => (
              <option key={L} value={L}>{L}</option>
            ))}
          </select>
        </label>
        <button type="button" className="gram-boton gram-boton-sec" onClick={nuevaPalabra}>
          Nueva palabra
        </button>
      </div>

      <p className="lectura-subtitulo">
        Una palabra de {longitudActiva} letras de este vocabulario, en {MAX_INTENTOS} intentos.
        Verde = letra en su sitio; amarillo = está pero en otra posición.
      </p>

      <div className="wordle-tablero">
        {intentos.map(({ intento, resultado }, i) => (
          <div key={i} className="wordle-fila">
            {[...intento].map((letra, j) => (
              <span key={j} className={`wordle-celda ${resultado[j]}`}>
                {letra}
              </span>
            ))}
            <span className="wordle-glosa">{glosas[intento]}</span>
          </div>
        ))}
      </div>

      {ganado && (
        <p className="juego-exito">
          ✓ ¡«{secreto.toUpperCase()}» ({glosas[secreto]}) en {intentos.length} intento
          {intentos.length === 1 ? '' : 's'}!
        </p>
      )}
      {(perdido || rendido) && (
        <p className="esc-aviso">
          Era «{secreto.toUpperCase()}» ({glosas[secreto]}).
        </p>
      )}

      {!terminado && (
        <>
          <form className="esc-form" onSubmit={intentar}>
            <input
              className="esc-input"
              value={entrada}
              onChange={(e) => setEntrada(e.target.value)}
              maxLength={Number(longitudActiva)}
              placeholder={'·'.repeat(Number(longitudActiva))}
              autoFocus
            />
            <button type="submit" className="gram-boton">Probar</button>
          </form>
          {aviso && <p className="esc-aviso">{aviso}</p>}
          <p className="wordle-candidatas">
            Intento {intentos.length + 1} de {MAX_INTENTOS} · quedan{' '}
            {candidatas.length} palabra{candidatas.length === 1 ? '' : 's'} posibles
          </p>
          {conPista && (
            <p className="esc-glosa">Pista — significa: «{glosas[secreto]}»</p>
          )}
          <div className="gram-nav">
            {!conPista && (
              <button
                type="button"
                className="gram-boton gram-boton-sec"
                onClick={() => setConPista(true)}
              >
                Pista (traducción)
              </button>
            )}
            <button
              type="button"
              className="gram-boton gram-boton-sec"
              onClick={() => setRendido(true)}
            >
              Rendirse
            </button>
          </div>
        </>
      )}

      {terminado && (
        <div className="gram-nav">
          <button type="button" className="gram-boton" onClick={nuevaPalabra}>
            Otra palabra
          </button>
          <Link to="/juegos/wordle" className="gram-boton gram-boton-sec">
            Otra lectura
          </Link>
        </div>
      )}
    </div>
  );
}

export default Wordle;
