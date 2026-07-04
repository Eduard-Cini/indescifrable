import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  construirGrafo,
  caminoMinimo,
  generarReto,
  sonVecinas,
} from '../../engine/escalera';
import { longitudesEscalera, pasosDisponibles, poolDe } from '../../engine/juegos';
import { generarSemillaAleatoria } from '../../engine/board';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

// Escalera de palabras (Sección 4): transformar origen → destino cambiando una
// letra por paso, pisando solo palabras del pool (todo el corpus o UNA
// lectura, según la ruta). El reto lo genera src/engine/escalera.js (grafo de
// Hamming 1 + BFS) de forma determinista por semilla; cada palabra pisada
// muestra su traducción. Los selectores solo ofrecen longitudes y pasos
// realmente jugables con este pool (src/engine/juegos.js).
function Escalera() {
  const { lectura } = useParams();
  const { idioma } = useIdiomaEstudio();
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
      if (vivo) setDatos(m.default[idioma] ?? m.default.de);
    });
    return () => {
      vivo = false;
    };
  }, [idioma]);

  const pool = datos ? poolDe(datos, lectura) : null;
  const longitudes = useMemo(
    () => (pool ? longitudesEscalera(pool.escalera) : []),
    [pool]
  );
  // Si la longitud elegida no es jugable con este pool, cae a la primera.
  const longitudActiva = longitudes.includes(longitud) ? longitud : longitudes[0];
  const glosas = pool?.escalera[longitudActiva] ?? null;
  const palabras = useMemo(() => (glosas ? Object.keys(glosas) : []), [glosas]);
  const opcionesPasos = useMemo(() => pasosDisponibles(palabras), [palabras]);
  const pasosActivos = opcionesPasos.includes(pasos) ? pasos : opcionesPasos[0];
  const enDiccionario = useMemo(() => new Set(palabras), [palabras]);
  const grafo = useMemo(() => construirGrafo(palabras), [palabras]);
  const reto = useMemo(
    () =>
      palabras.length > 0 && pasosActivos
        ? generarReto(palabras, {
            pasos: pasosActivos,
            semilla: `${lectura}:${longitudActiva}:${pasosActivos}:${semilla}`,
          })
        : null,
    [palabras, pasosActivos, semilla, longitudActiva, lectura]
  );

  useEffect(() => {
    setHistorial(reto ? [reto.origen] : []);
    setEntrada('');
    setAviso(null);
    setRendido(false);
  }, [reto]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos/escalera" className="lectura-link">← Lecturas</Link>
      <h1>Escalera de palabras</h1>
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
          Este vocabulario no da para la escalera (el grafo no tiene caminos).{' '}
          <Link to="/juegos/escalera" className="lectura-link">Elegir otra lectura</Link>.
        </p>
      </div>
    );
  }

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
            value={longitudActiva}
            onChange={(e) => setLongitud(e.target.value)}
          >
            {longitudes.map((L) => (
              <option key={L} value={L}>{L}</option>
            ))}
          </select>
        </label>
        <label>
          Pasos mínimos{' '}
          <select
            className="juego-select"
            value={pasosActivos}
            onChange={(e) => setPasos(Number(e.target.value))}
          >
            {opcionesPasos.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
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
              maxLength={Number(longitudActiva)}
              placeholder={'·'.repeat(Number(longitudActiva))}
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
          <Link to="/juegos/escalera" className="gram-boton gram-boton-sec">
            Otra lectura
          </Link>
        </div>
      )}
    </div>
  );
}

export default Escalera;
