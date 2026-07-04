import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { generarSopa, buscarSeleccion, casillasDe } from '../../engine/sopa';
import { poolDe, tamanosTablero } from '../../engine/juegos';
import { generarSemillaAleatoria } from '../../engine/board';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

// Sopa de letras (Sección 4): las pistas van en ESPAÑOL y lo que se busca en
// la cuadrícula es la palabra alemana del pool (todo el corpus o UNA lectura,
// según la ruta) — encontrar «regalo» es encontrar GESCHENK. Selección por
// dos clicks: inicio y fin. La generación (colocación aleatorizada + relleno
// con la distribución de letras del pool) vive en src/engine/sopa.js,
// determinista por semilla; los tamaños dependen del pool (engine/juegos.js).
function Sopa() {
  const { lectura } = useParams();
  const { idioma } = useIdiomaEstudio();
  const [datos, setDatos] = useState(null);
  const [n, setN] = useState(8);
  const [semilla, setSemilla] = useState(() => generarSemillaAleatoria());
  const [inicio, setInicio] = useState(null);
  const [halladas, setHalladas] = useState([]);
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
  const tamanos = useMemo(() => (pool ? tamanosTablero(pool.crucigrama) : []), [pool]);
  const nActivo = tamanos.includes(n) ? n : tamanos[0];
  const sopa = useMemo(
    () =>
      pool && nActivo
        ? generarSopa(pool.crucigrama, {
            n: nActivo,
            filas: 12,
            columnas: 12,
            semilla: `${lectura}:${nActivo}:${semilla}`,
          })
        : null,
    [pool, nActivo, semilla, lectura]
  );

  useEffect(() => {
    setInicio(null);
    setHalladas([]);
    setAviso(null);
    setRendido(false);
  }, [sopa]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos/sopa" className="lectura-link">← Lecturas</Link>
      <h1>Sopa de letras</h1>
      {pool ? (
        <span className={`gram-nivel ${pool.nivel ?? ''}`}>{pool.titulo}</span>
      ) : (
        <span />
      )}
    </header>
  );

  if (datos && (!pool || tamanos.length === 0)) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Este vocabulario no da para una sopa de letras (pocas entradas).{' '}
          <Link to="/juegos/sopa" className="lectura-link">Elegir otra lectura</Link>.
        </p>
      </div>
    );
  }

  if (!sopa) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  const visibles = rendido ? sopa.palabras.map((p) => p.palabra) : halladas;
  const resaltadas = new Set(
    sopa.palabras
      .filter((p) => visibles.includes(p.palabra))
      .flatMap((p) => casillasDe(p))
  );
  const completado = halladas.length === sopa.palabras.length;

  const clicar = (fila, col) => {
    if (rendido || completado) return;
    if (!inicio) {
      setInicio({ fila, col });
      setAviso(null);
      return;
    }
    if (inicio.fila === fila && inicio.col === col) {
      setInicio(null);
      return;
    }
    const encontrada = buscarSeleccion(sopa, inicio, { fila, col });
    if (encontrada && !halladas.includes(encontrada.palabra)) {
      setHalladas([...halladas, encontrada.palabra]);
      setAviso(null);
    } else {
      setAviso('Ahí no hay palabra de la lista: marca su primera y su última letra.');
    }
    setInicio(null);
  };

  const nuevaSopa = () => setSemilla(generarSemillaAleatoria());

  return (
    <div className="lectura-container">
      {cabecera}

      <div className="juego-config">
        <label>
          Palabras{' '}
          <select
            className="juego-select"
            value={nActivo}
            onChange={(e) => setN(Number(e.target.value))}
          >
            {tamanos.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </label>
        <button type="button" className="gram-boton gram-boton-sec" onClick={nuevaSopa}>
          Nueva sopa
        </button>
      </div>

      <p className="lectura-subtitulo">
        Busca la palabra de cada pista (→, ↓ o ↘). Click en su primera
        letra y otro en la última.
      </p>

      <div
        className="sopa-tablero"
        style={{ gridTemplateColumns: `repeat(${sopa.columnas}, 1.9rem)` }}
      >
        {sopa.cuadricula.flatMap((fila, f) =>
          fila.map((letra, c) => {
            const pos = `${f},${c}`;
            let estado = '';
            if (resaltadas.has(pos)) estado = ' hallada';
            else if (inicio && inicio.fila === f && inicio.col === c) estado = ' inicio';
            return (
              <button
                key={pos}
                type="button"
                className={`sopa-celda${estado}`}
                onClick={() => clicar(f, c)}
              >
                {letra}
              </button>
            );
          })
        )}
      </div>

      {aviso && <p className="esc-aviso">{aviso}</p>}
      {completado && !rendido && (
        <p className="juego-exito">✓ ¡Las {sopa.palabras.length} palabras encontradas!</p>
      )}
      {rendido && <p className="lectura-subtitulo">Solución revelada.</p>}

      <ul className="sopa-pistas">
        {sopa.palabras.map((p) => {
          const hallada = visibles.includes(p.palabra);
          return (
            <li key={p.palabra} className={hallada ? 'hallada' : ''}>
              {p.pista}
              {hallada && <span className="sopa-solucion">{p.palabra}</span>}
            </li>
          );
        })}
      </ul>

      {!completado && !rendido && (
        <div className="gram-nav">
          <button
            type="button"
            className="gram-boton gram-boton-sec"
            onClick={() => setRendido(true)}
          >
            Rendirse
          </button>
        </div>
      )}
      {(completado || rendido) && (
        <div className="gram-nav">
          <button type="button" className="gram-boton" onClick={nuevaSopa}>
            Otra sopa
          </button>
          <Link to="/juegos/sopa" className="gram-boton gram-boton-sec">
            Otra lectura
          </Link>
        </div>
      )}
    </div>
  );
}

export default Sopa;
