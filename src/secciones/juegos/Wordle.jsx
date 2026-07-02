import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  evaluar,
  esVictoria,
  elegirSecreto,
  filtrarConsistentes,
} from '../../engine/wordle';
import { generarSemillaAleatoria } from '../../engine/board';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

const MAX_INTENTOS = 6;

// Adivina la palabra (Sección 4): Wordle sobre el vocabulario alemán del
// corpus. Los intentos deben ser palabras de las lecturas (así cada intento
// enseña: se muestra su traducción) y el contador de candidatas consistentes
// hace visible la teoría de la información del juego (engine/wordle.js).
function Wordle() {
  const [datos, setDatos] = useState(null);
  const [longitud, setLongitud] = useState('4');
  const [semilla, setSemilla] = useState(() => generarSemillaAleatoria());
  const [intentos, setIntentos] = useState([]);
  const [entrada, setEntrada] = useState('');
  const [aviso, setAviso] = useState(null);
  const [rendido, setRendido] = useState(false);

  useEffect(() => {
    let vivo = true;
    import('../../data/juegos.json').then((m) => {
      if (vivo) setDatos(m.default);
    });
    return () => {
      vivo = false;
    };
  }, []);

  const glosas = datos?.escalera[longitud] ?? null;
  const palabras = useMemo(() => (glosas ? Object.keys(glosas) : []), [glosas]);
  const enDiccionario = useMemo(() => new Set(palabras), [palabras]);
  const secreto = useMemo(
    () =>
      palabras.length > 0 ? elegirSecreto(palabras, `${longitud}:${semilla}`) : null,
    [palabras, longitud, semilla]
  );

  useEffect(() => {
    setIntentos([]);
    setEntrada('');
    setAviso(null);
    setRendido(false);
  }, [secreto]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos" className="lectura-link">← Juegos</Link>
      <h1>Adivina la palabra</h1>
      <span />
    </header>
  );

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
    if (palabra.length !== Number(longitud)) {
      setAviso(`La palabra tiene ${longitud} letras.`);
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
            value={longitud}
            onChange={(e) => setLongitud(e.target.value)}
          >
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
        </label>
        <button type="button" className="gram-boton gram-boton-sec" onClick={nuevaPalabra}>
          Nueva palabra
        </button>
      </div>

      <p className="lectura-subtitulo">
        Una palabra alemana de {longitud} letras del corpus, en {MAX_INTENTOS} intentos.
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
              maxLength={Number(longitud)}
              placeholder={'·'.repeat(Number(longitud))}
              autoFocus
            />
            <button type="submit" className="gram-boton">Probar</button>
          </form>
          {aviso && <p className="esc-aviso">{aviso}</p>}
          <p className="wordle-candidatas">
            Intento {intentos.length + 1} de {MAX_INTENTOS} · quedan{' '}
            {candidatas.length} palabra{candidatas.length === 1 ? '' : 's'} posibles
          </p>
          <div className="gram-nav">
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
          <Link to="/juegos" className="gram-boton gram-boton-sec">
            Otros juegos
          </Link>
        </div>
      )}
    </div>
  );
}

export default Wordle;
