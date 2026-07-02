import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  seleccionarSesion,
  opcionesDe,
  esCorrecta,
  resumenSesion,
} from '../../engine/gramatica';
import '../lectura/lectura.css';
import './gramatica.css';

const TOPE_SESION = 10;

function Ejercicios() {
  const { tema } = useParams();
  const [data, setData] = useState(null);
  const [semilla, setSemilla] = useState(() => Math.random().toString(36).slice(2));
  const [idx, setIdx] = useState(0);
  const [elegida, setElegida] = useState(null);
  const [resultados, setResultados] = useState([]);

  useEffect(() => {
    let vivo = true;
    import('../../data/gramatica.json').then((m) => {
      if (vivo) setData(m.default);
    });
    return () => {
      vivo = false;
    };
  }, []);

  const meta = data?.temas.find((t) => t.id === tema) ?? null;
  const banco = data?.ejercicios[tema] ?? [];

  const sesion = useMemo(
    () => seleccionarSesion(banco, { n: TOPE_SESION, semilla }),
    [banco, semilla]
  );

  const cabecera = (
    <header className="lectura-top">
      <Link to="/gramatica" className="lectura-link">← Gramática</Link>
      <h1>{meta?.titulo ?? 'Gramática'}</h1>
      <span />
    </header>
  );

  if (data === null) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  if (!meta || sesion.length === 0) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          No hay ejercicios para este tema todavía. Genera más con{' '}
          <code>pipeline/gramatica.py</code>.
        </p>
      </div>
    );
  }

  const reiniciar = () => {
    setSemilla(Math.random().toString(36).slice(2));
    setIdx(0);
    setElegida(null);
    setResultados([]);
  };

  const leccion = (
    <details className="gram-leccion">
      <summary>Ver la regla</summary>
      <p>{meta.resumen}</p>
      {meta.tabla && (
        <table className="gram-tabla">
          <thead>
            <tr>
              {meta.tabla.cabecera.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {meta.tabla.filas.map((fila, i) => (
              <tr key={i}>
                {fila.map((celda, j) => (
                  <td key={j}>{celda}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </details>
  );

  // Pantalla final
  if (idx >= sesion.length) {
    const r = resumenSesion(resultados);
    return (
      <div className="lectura-container">
        {cabecera}
        {leccion}
        <div className="repaso-fin">
          <p className="repaso-fin-titulo">Sesión terminada 🎉</p>
          <p className="repaso-fin-stats">
            {r.aciertos} de {r.total} correcta{r.aciertos === 1 ? '' : 's'} ·{' '}
            {r.porcentaje}%
          </p>
          <div className="gram-nav">
            <button type="button" className="gram-boton" onClick={reiniciar}>
              Otra ronda
            </button>
            <Link to="/gramatica" className="gram-boton gram-boton-sec">
              Cambiar de tema
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const ejercicio = sesion[idx];
  const opciones = opcionesDe(ejercicio);
  const respondida = elegida !== null;
  const acerto = respondida && esCorrecta(ejercicio, elegida);

  const elegir = (op) => {
    if (respondida) return;
    setElegida(op);
    setResultados([...resultados, esCorrecta(ejercicio, op)]);
  };

  const siguiente = () => {
    setIdx(idx + 1);
    setElegida(null);
  };

  return (
    <div className="lectura-container">
      {cabecera}
      {leccion}

      <p className="lectura-subtitulo">
        {idx + 1} / {sesion.length}
      </p>

      <p className="gram-frase">
        {ejercicio.antes}
        <span className={`gram-hueco${respondida ? (acerto ? ' bien' : ' mal') : ''}`}>
          {respondida ? elegida : '_____'}
        </span>
        {ejercicio.despues}
      </p>

      <div className="gram-opciones">
        {opciones.map((op) => {
          let estado = '';
          if (respondida) {
            if (op === ejercicio.respuesta) estado = ' correcta';
            else if (op === elegida) estado = ' incorrecta';
          }
          return (
            <button
              key={op}
              type="button"
              className={`gram-opcion${estado}`}
              onClick={() => elegir(op)}
              disabled={respondida}
            >
              {op}
            </button>
          );
        })}
      </div>

      {respondida && (
        <div className="gram-feedback">
          <p className={`gram-veredicto ${acerto ? 'bien' : 'mal'}`}>
            {acerto ? '✓ Correcto' : `✗ Era «${ejercicio.respuesta}»`}
          </p>
          {ejercicio.pista && <p className="gram-pista">{ejercicio.pista}</p>}
          {ejercicio.fuente && <p className="gram-fuente">{ejercicio.fuente}</p>}
          <div className="gram-nav">
            <button type="button" className="gram-boton" onClick={siguiente}>
              {idx + 1 < sesion.length ? 'Siguiente' : 'Ver resultado'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Ejercicios;
