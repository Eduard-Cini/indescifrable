import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { generarSudoku } from '../../engine/sudoku';
import { poolDe } from '../../engine/juegos';
import { generarSemillaAleatoria } from '../../engine/board';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './juegos.css';

const NOMBRE_DIFICULTAD = { facil: 'Fácil', medio: 'Intermedio', dificil: 'Difícil' };

// Sudoku de palabras (Sección 4): un sudoku 9×9 cuyos símbolos son las 9
// letras (todas distintas) de una palabra alemana del pool; una fila esconde
// la palabra y al resolver se revela con su traducción. La dificultad es la
// del sudoku (casillas dadas: 40/32/26), no la del vocabulario; la generación
// (backtracking + excavado con unicidad) vive en src/engine/sudoku.js.
function Sudoku() {
  const { lectura } = useParams();
  const { idioma } = useIdiomaEstudio();
  const [datos, setDatos] = useState(null);
  const [dificultad, setDificultad] = useState('facil');
  const [semilla, setSemilla] = useState(() => generarSemillaAleatoria());
  const [letras, setLetras] = useState({}); // pos "f,c" -> letra escrita
  const [malas, setMalas] = useState(null);
  const [rendido, setRendido] = useState(false);
  const refs = useRef(new Map());

  useEffect(() => {
    let vivo = true;
    import('../../data/juegos.json').then((m) => {
      if (vivo) setDatos(m.default[idioma] ?? false);
    });
    return () => {
      vivo = false;
    };
  }, [idioma]);

  const pool = datos ? poolDe(datos, lectura) : null;
  const sudoku = useMemo(
    () =>
      pool?.sudoku?.length
        ? generarSudoku(pool.sudoku, {
            dificultad,
            semilla: `${lectura}:${dificultad}:${semilla}`,
          })
        : null,
    [pool, dificultad, semilla, lectura]
  );

  useEffect(() => {
    setLetras({});
    setMalas(null);
    setRendido(false);
    refs.current.clear();
  }, [sudoku]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/juegos/sudoku" className="lectura-link">← Lecturas</Link>
      <h1>Sudoku de palabras</h1>
      {pool ? (
        <span className={`gram-nivel ${pool.nivel ?? ''}`}>{pool.titulo}</span>
      ) : (
        <span />
      )}
    </header>
  );

  if (datos === false) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Este juego aún no está disponible en tu idioma de estudio.{' '}
          <Link to="/juegos" className="lectura-link">← Volver a Juegos</Link>
        </p>
      </div>
    );
  }

  if (datos && (!pool || !pool.sudoku?.length)) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Este vocabulario no tiene palabras de 9 letras distintas.{' '}
          <Link to="/juegos/sudoku" className="lectura-link">Elegir otra lectura</Link>.
        </p>
      </div>
    );
  }

  if (!sudoku) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  const letraEn = (f, c) => sudoku.inicial[f][c] ?? letras[`${f},${c}`] ?? '';
  const completado = sudoku.solucion.every((fila, f) =>
    fila.every((letra, c) => letraEn(f, c) === letra)
  );
  const terminado = completado || rendido;

  const enfocar = (f, c) => refs.current.get(`${f},${c}`)?.focus();

  const escribir = (f, c, valor) => {
    const v = valor.slice(-1).toLowerCase();
    if (v && !sudoku.letras.includes(v)) return; // solo las 9 letras del puzle
    setLetras({ ...letras, [`${f},${c}`]: v });
    setMalas(null);
  };

  const teclas = (f, c, e) => {
    const flechas = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
    if (flechas[e.key]) {
      e.preventDefault();
      let [nf, nc] = [f + flechas[e.key][0], c + flechas[e.key][1]];
      // salta las dadas hasta la siguiente casilla editable en esa dirección
      while (nf >= 0 && nf < 9 && nc >= 0 && nc < 9) {
        if (sudoku.inicial[nf][nc] === null) {
          enfocar(nf, nc);
          return;
        }
        nf += flechas[e.key][0];
        nc += flechas[e.key][1];
      }
    }
  };

  const comprobar = () => {
    const falladas = new Set();
    sudoku.solucion.forEach((fila, f) =>
      fila.forEach((letra, c) => {
        const pos = `${f},${c}`;
        if (sudoku.inicial[f][c] === null && letras[pos] && letras[pos] !== letra) {
          falladas.add(pos);
        }
      })
    );
    setMalas(falladas);
  };

  const revelar = () => {
    const todas = {};
    sudoku.solucion.forEach((fila, f) =>
      fila.forEach((letra, c) => {
        if (sudoku.inicial[f][c] === null) todas[`${f},${c}`] = letra;
      })
    );
    setLetras(todas);
    setMalas(null);
    setRendido(true);
  };

  const nuevo = () => setSemilla(generarSemillaAleatoria());

  return (
    <div className="lectura-container">
      {cabecera}

      <div className="juego-config">
        <label>
          Dificultad{' '}
          <select
            className="juego-select"
            value={dificultad}
            onChange={(e) => setDificultad(e.target.value)}
          >
            {Object.entries(NOMBRE_DIFICULTAD).map(([id, nombre]) => (
              <option key={id} value={id}>{nombre}</option>
            ))}
          </select>
        </label>
        <button type="button" className="gram-boton gram-boton-sec" onClick={nuevo}>
          Nuevo sudoku
        </button>
      </div>

      <p className="lectura-subtitulo">
        Cada fila, columna y caja 3×3 lleva las 9 letras{' '}
        <b className="sudoku-letras">{sudoku.letras.join(' · ')}</b> sin repetir
        ({sudoku.dadas} casillas dadas). Una fila esconde una palabra del
        vocabulario.
      </p>

      <div className="sudoku-tablero">
        {sudoku.solucion.map((filaSol, f) =>
          filaSol.map((_, c) => {
            const pos = `${f},${c}`;
            const dada = sudoku.inicial[f][c] !== null;
            const bordes =
              (c % 3 === 2 && c !== 8 ? ' caja-der' : '') +
              (f % 3 === 2 && f !== 8 ? ' caja-abajo' : '');
            const enPalabra = terminado && f === sudoku.fila;
            if (dada) {
              return (
                <div key={pos} className={`sudoku-celda dada${bordes}${enPalabra ? ' palabra' : ''}`}>
                  {sudoku.inicial[f][c]}
                </div>
              );
            }
            let estado = '';
            if (malas?.has(pos)) estado = ' mal';
            else if (terminado) estado = ' bien';
            if (enPalabra) estado += ' palabra';
            return (
              <div key={pos} className={`sudoku-celda${bordes}`}>
                <input
                  ref={(el) => el && refs.current.set(pos, el)}
                  className={estado.trim() || undefined}
                  value={letras[pos] ?? ''}
                  onChange={(e) => escribir(f, c, e.target.value)}
                  onKeyDown={(e) => teclas(f, c, e)}
                  disabled={rendido}
                  aria-label={`fila ${f + 1}, columna ${c + 1}`}
                />
              </div>
            );
          })
        )}
      </div>

      {completado && !rendido && (
        <p className="juego-exito">
          ✓ ¡Resuelto! La fila {sudoku.fila + 1} escondía «{sudoku.palabra.toUpperCase()}»
          ({sudoku.pista}).
        </p>
      )}
      {rendido && (
        <p className="lectura-subtitulo">
          La fila {sudoku.fila + 1} escondía «{sudoku.palabra.toUpperCase()}» ({sudoku.pista}).
        </p>
      )}
      {!terminado && malas && (
        <p className={malas.size > 0 ? 'esc-aviso' : 'lectura-subtitulo'}>
          {malas.size > 0
            ? `${malas.size} casilla${malas.size === 1 ? '' : 's'} incorrecta${malas.size === 1 ? '' : 's'}.`
            : 'Sin errores por ahora; faltan casillas.'}
        </p>
      )}

      {!terminado && (
        <div className="gram-nav">
          <button type="button" className="gram-boton" onClick={comprobar}>
            Comprobar
          </button>
          <button type="button" className="gram-boton gram-boton-sec" onClick={revelar}>
            Revelar
          </button>
        </div>
      )}
      {terminado && (
        <div className="gram-nav">
          <button type="button" className="gram-boton" onClick={nuevo}>
            Otro sudoku
          </button>
          <Link to="/juegos/sudoku" className="gram-boton gram-boton-sec">
            Otra lectura
          </Link>
        </div>
      )}
    </div>
  );
}

export default Sudoku;
