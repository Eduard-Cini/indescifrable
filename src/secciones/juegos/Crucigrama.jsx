import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { generarCrucigrama, cuadricula } from '../../engine/crucigrama';
import { poolDe, tamanosTablero } from '../../engine/juegos';
import { generarSemillaAleatoria } from '../../engine/board';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

// Crucigrama (Sección 4): palabras alemanas del pool (todo el corpus o UNA
// lectura, según la ruta) con la pista en español. La colocación la decide
// src/engine/crucigrama.js (backtracking) de forma determinista por semilla;
// los tamaños ofrecidos dependen del pool (engine/juegos.js).
function Crucigrama() {
  const { lectura } = useParams();
  const [datos, setDatos] = useState(null);
  const [n, setN] = useState(8);
  const [semilla, setSemilla] = useState(() => generarSemillaAleatoria());
  const [letras, setLetras] = useState({});
  const [malas, setMalas] = useState(null); // posiciones falladas al comprobar
  const [rendido, setRendido] = useState(false);
  const [dir, setDir] = useState('H');
  const refs = useRef(new Map());
  const enfocada = useRef(null);

  useEffect(() => {
    let vivo = true;
    import('../../data/juegos.json').then((m) => {
      if (vivo) setDatos(m.default);
    });
    return () => {
      vivo = false;
    };
  }, []);

  const pool = datos ? poolDe(datos, lectura) : null;
  const tamanos = useMemo(() => (pool ? tamanosTablero(pool.crucigrama) : []), [pool]);
  const nActivo = tamanos.includes(n) ? n : tamanos[0];
  const cruci = useMemo(
    () =>
      pool && nActivo
        ? generarCrucigrama(pool.crucigrama, {
            n: nActivo,
            semilla: `${lectura}:${nActivo}:${semilla}`,
          })
        : null,
    [pool, nActivo, semilla, lectura]
  );
  const solucion = useMemo(() => (cruci ? cuadricula(cruci) : null), [cruci]);
  const numeros = useMemo(() => {
    const m = new Map();
    for (const p of cruci?.palabras ?? []) m.set(`${p.fila},${p.col}`, p.numero);
    return m;
  }, [cruci]);

  useEffect(() => {
    setLetras({});
    setMalas(null);
    setRendido(false);
    refs.current.clear();
    enfocada.current = null;
  }, [cruci]);

  const cabecera = (
    <header className="lectura-top">
      <Link to={`/juegos/${lectura}`} className="lectura-link">
        ← {pool?.titulo ?? 'Juegos'}
      </Link>
      <h1>Crucigrama</h1>
      <span />
    </header>
  );

  if (datos && (!pool || tamanos.length === 0)) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Este vocabulario no da para un crucigrama (pocas entradas).{' '}
          <Link to={`/juegos/${lectura}`} className="lectura-link">Otros juegos</Link>.
        </p>
      </div>
    );
  }

  if (!cruci || !solucion) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  const completado = solucion.every((fila, f) =>
    fila.every((letra, c) => !letra || letras[`${f},${c}`] === letra)
  );

  const enfocar = (f, c) => refs.current.get(`${f},${c}`)?.focus();

  const mover = (f, c, delta) => {
    const [dF, dC] = dir === 'H' ? [0, delta] : [delta, 0];
    if (solucion[f + dF]?.[c + dC]) enfocar(f + dF, c + dC);
  };

  const escribir = (f, c, valor) => {
    const v = valor.slice(-1).toLowerCase().replace(/[^a-z]/, '');
    setLetras({ ...letras, [`${f},${c}`]: v });
    setMalas(null);
    if (v) mover(f, c, 1);
  };

  const teclas = (f, c, e) => {
    const flechas = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
    if (flechas[e.key]) {
      e.preventDefault();
      const [dF, dC] = flechas[e.key];
      setDir(dF === 0 ? 'H' : 'V');
      if (solucion[f + dF]?.[c + dC]) enfocar(f + dF, c + dC);
    } else if (e.key === 'Backspace' && !letras[`${f},${c}`]) {
      e.preventDefault();
      mover(f, c, -1);
    }
  };

  // Un click sobre la casilla ya enfocada alterna horizontal ⇄ vertical.
  const alClicar = (pos) => {
    if (enfocada.current === pos) setDir((d) => (d === 'H' ? 'V' : 'H'));
    enfocada.current = pos;
  };

  const comprobar = () => {
    const falladas = new Set();
    solucion.forEach((fila, f) =>
      fila.forEach((letra, c) => {
        const pos = `${f},${c}`;
        if (letra && letras[pos] && letras[pos] !== letra) falladas.add(pos);
      })
    );
    setMalas(falladas);
  };

  const revelar = () => {
    const todas = {};
    solucion.forEach((fila, f) =>
      fila.forEach((letra, c) => {
        if (letra) todas[`${f},${c}`] = letra;
      })
    );
    setLetras(todas);
    setMalas(null);
    setRendido(true);
  };

  const nuevo = () => setSemilla(generarSemillaAleatoria());
  const horizontales = cruci.palabras.filter((p) => p.dir === 'H');
  const verticales = cruci.palabras.filter((p) => p.dir === 'V');

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
        <button type="button" className="gram-boton gram-boton-sec" onClick={nuevo}>
          Nuevo crucigrama
        </button>
      </div>

      <div
        className="cruci-tablero"
        style={{ gridTemplateColumns: `repeat(${cruci.columnas}, 2.2rem)` }}
      >
        {solucion.flatMap((fila, f) =>
          fila.map((letra, c) => {
            const pos = `${f},${c}`;
            if (!letra) return <div key={pos} className="cruci-celda negra" />;
            let estado = '';
            if (malas?.has(pos)) estado = ' mal';
            else if (completado || rendido) estado = ' bien';
            return (
              <div key={pos} className="cruci-celda">
                {numeros.has(pos) && <span className="cruci-num">{numeros.get(pos)}</span>}
                <input
                  ref={(el) => el && refs.current.set(pos, el)}
                  className={estado.trim() || undefined}
                  value={letras[pos] ?? ''}
                  onChange={(e) => escribir(f, c, e.target.value)}
                  onKeyDown={(e) => teclas(f, c, e)}
                  onClick={() => alClicar(pos)}
                  disabled={rendido}
                  aria-label={`fila ${f + 1}, columna ${c + 1}`}
                />
              </div>
            );
          })
        )}
      </div>

      {completado && !rendido && (
        <p className="juego-exito">✓ ¡Crucigrama completado!</p>
      )}
      {!completado && malas && (
        <p className={malas.size > 0 ? 'esc-aviso' : 'lectura-subtitulo'}>
          {malas.size > 0
            ? `${malas.size} casilla${malas.size === 1 ? '' : 's'} incorrecta${malas.size === 1 ? '' : 's'}.`
            : 'Sin errores por ahora; faltan casillas.'}
        </p>
      )}
      {rendido && <p className="lectura-subtitulo">Solución revelada.</p>}

      {!completado && !rendido && (
        <div className="gram-nav">
          <button type="button" className="gram-boton" onClick={comprobar}>
            Comprobar
          </button>
          <button type="button" className="gram-boton gram-boton-sec" onClick={revelar}>
            Revelar
          </button>
        </div>
      )}
      {(completado || rendido) && (
        <div className="gram-nav">
          <button type="button" className="gram-boton" onClick={nuevo}>
            Otro crucigrama
          </button>
          <Link to={`/juegos/${lectura}`} className="gram-boton gram-boton-sec">
            Otros juegos
          </Link>
        </div>
      )}

      <div className="cruci-pistas">
        <div>
          <h3>Horizontales</h3>
          <ol>
            {horizontales.map((p) => (
              <li key={`H${p.numero}`}>
                <b>{p.numero}.</b> {p.pista} <span className="cruci-len">({p.palabra.length})</span>
              </li>
            ))}
          </ol>
        </div>
        <div>
          <h3>Verticales</h3>
          <ol>
            {verticales.map((p) => (
              <li key={`V${p.numero}`}>
                <b>{p.numero}.</b> {p.pista} <span className="cruci-len">({p.palabra.length})</span>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}

export default Crucigrama;
