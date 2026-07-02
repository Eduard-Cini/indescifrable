import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { generarSopa, buscarSeleccion, casillasDe } from '../../engine/sopa';
import { generarSemillaAleatoria } from '../../engine/board';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

// Sopa de letras (Sección 4): las pistas van en ESPAÑOL y lo que se busca en
// la cuadrícula es la palabra alemana del corpus — encontrar «regalo» es
// encontrar GESCHENK. Selección por dos clicks: inicio y fin de la palabra.
// La generación (colocación aleatorizada + relleno con la distribución de
// letras del pool) vive en src/engine/sopa.js, determinista por semilla.
function Sopa() {
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
      if (vivo) setDatos(m.default);
    });
    return () => {
      vivo = false;
    };
  }, []);

  const sopa = useMemo(
    () =>
      datos
        ? generarSopa(datos.crucigrama, {
            n,
            filas: 12,
            columnas: 12,
            semilla: `${n}:${semilla}`,
          })
        : null,
    [datos, n, semilla]
  );

  useEffect(() => {
    setInicio(null);
    setHalladas([]);
    setAviso(null);
    setRendido(false);
  }, [sopa]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos" className="lectura-link">← Juegos</Link>
      <h1>Sopa de letras</h1>
      <span />
    </header>
  );

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
            value={n}
            onChange={(e) => setN(Number(e.target.value))}
          >
            <option value="6">6</option>
            <option value="8">8</option>
            <option value="10">10</option>
          </select>
        </label>
        <button type="button" className="gram-boton gram-boton-sec" onClick={nuevaSopa}>
          Nueva sopa
        </button>
      </div>

      <p className="lectura-subtitulo">
        Busca la palabra alemana de cada pista (→, ↓ o ↘). Click en su primera
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
          <Link to="/juegos" className="gram-boton gram-boton-sec">
            Otros juegos
          </Link>
        </div>
      )}
    </div>
  );
}

export default Sopa;
