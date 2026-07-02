import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  construirGrafo,
  caminoMinimo,
  generarReto,
  sonVecinas,
} from '../../engine/escalera';
import { generarSemillaAleatoria } from '../../engine/board';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

// Escalera de palabras (Sección 4): transformar origen → destino cambiando una
// letra por paso, pisando solo palabras del corpus. El reto lo genera
// src/engine/escalera.js (grafo de Hamming 1 + BFS) de forma determinista por
// semilla; cada palabra pisada muestra su traducción (también aquí se aprende
// vocabulario). El diccionario viene de pipeline/juegos.py vía dynamic import.
function Escalera() {
  const [datos, setDatos] = useState(null);
  const [longitud, setLongitud] = useState('4');
  const [pasos, setPasos] = useState(4);
  const [semilla, setSemilla] = useState(() => generarSemillaAleatoria());
  const [historial, setHistorial] = useState([]);
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
  const grafo = useMemo(() => construirGrafo(palabras), [palabras]);
  const reto = useMemo(
    () =>
      palabras.length > 0
        ? generarReto(palabras, { pasos, semilla: `${longitud}:${pasos}:${semilla}` })
        : null,
    [palabras, pasos, semilla, longitud]
  );

  useEffect(() => {
    setHistorial(reto ? [reto.origen] : []);
    setEntrada('');
    setAviso(null);
    setRendido(false);
  }, [reto]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos" className="lectura-link">← Juegos</Link>
      <h1>Escalera de palabras</h1>
      <span />
    </header>
  );

  if (!datos || !reto || historial.length === 0) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  const actual = historial.at(-1);
  const ganado = actual === reto.destino;
  const movimientos = historial.length - 1;

  const intentar = (e) => {
    e.preventDefault();
    const palabra = entrada.trim().toLowerCase();
    if (!palabra || ganado || rendido) return;
    if (!sonVecinas(actual, palabra)) {
      setAviso('Cambia exactamente UNA letra (misma longitud).');
      return;
    }
    if (!enDiccionario.has(palabra)) {
      setAviso(`«${palabra}» no está en el vocabulario de las lecturas.`);
      return;
    }
    setHistorial([...historial, palabra]);
    setEntrada('');
    setAviso(null);
  };

  const pista = () => {
    const camino = caminoMinimo(grafo, actual, reto.destino);
    if (camino && camino.length > 1) {
      setHistorial([...historial, camino[1]]);
      setEntrada('');
      setAviso(null);
    }
  };

  const deshacer = () => {
    if (historial.length > 1) setHistorial(historial.slice(0, -1));
    setAviso(null);
  };

  const nuevoReto = () => setSemilla(generarSemillaAleatoria());

  const camino = rendido ? reto.camino : historial;

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
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
        </label>
        <label>
          Pasos mínimos{' '}
          <select
            className="juego-select"
            value={pasos}
            onChange={(e) => setPasos(Number(e.target.value))}
          >
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
          </select>
        </label>
        <button type="button" className="gram-boton gram-boton-sec" onClick={nuevoReto}>
          Nuevo reto
        </button>
      </div>

      <p className="esc-reto">
        <span className="esc-palabra">{reto.origen}</span>
        <span className="esc-flecha">⟶</span>
        <span className="esc-palabra">{reto.destino}</span>
        <span className="esc-glosa">
          «{glosas[reto.origen]}» ⟶ «{glosas[reto.destino]}»
        </span>
      </p>

      <ol className="esc-camino">
        {camino.map((palabra, i) => (
          <li
            key={`${i}:${palabra}`}
            className={`esc-paso${palabra === reto.destino ? ' meta' : ''}`}
          >
            <span className="esc-palabra">{palabra}</span>
            <span className="esc-glosa">{glosas[palabra]}</span>
          </li>
        ))}
      </ol>

      {ganado && (
        <p className="juego-exito">
          ✓ ¡Conseguido en {movimientos} paso{movimientos === 1 ? '' : 's'}!
          {movimientos === reto.pasos
            ? ' Camino mínimo: ni un paso de más.'
            : ` El mínimo eran ${reto.pasos}.`}
        </p>
      )}
      {rendido && (
        <p className="lectura-subtitulo">
          Ese era un camino mínimo de {reto.pasos} pasos (BFS).
        </p>
      )}

      {!ganado && !rendido && (
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
          <p className="esc-contador">
            {movimientos} movimiento{movimientos === 1 ? '' : 's'} · mínimo posible: {reto.pasos}
          </p>
          <div className="gram-nav">
            <button
              type="button"
              className="gram-boton gram-boton-sec"
              onClick={deshacer}
              disabled={historial.length === 1}
            >
              Deshacer
            </button>
            <button type="button" className="gram-boton gram-boton-sec" onClick={pista}>
              Pista
            </button>
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

      {(ganado || rendido) && (
        <div className="gram-nav">
          <button type="button" className="gram-boton" onClick={nuevoReto}>
            Otro reto
          </button>
          <Link to="/juegos" className="gram-boton gram-boton-sec">
            Otros juegos
          </Link>
        </div>
      )}
    </div>
  );
}

export default Escalera;
