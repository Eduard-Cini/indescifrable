import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  agruparPorLectura,
  lecturaCompletada,
  claveEjercicio,
  opcionesDe,
  esCorrecta,
  resumenSesion,
} from '../../engine/gramatica';
import {
  cargarGramaticaHechos,
  guardarGramaticaHechos,
} from '../../engine/almacenamiento';
import '../lectura/lectura.css';
import './gramatica.css';

const NOMBRE_NIVEL = { principiante: 'Principiante', intermedio: 'Intermedio', avanzado: 'Avanzado' };

// Sesión de gramática de UNA lectura: recorre todos sus ejercicios en orden
// (agrupados por tema, del más básico al más avanzado). Cada acierto se
// registra con una clave estable; la lectura queda «completada» (palomita en
// el selector) cuando todos sus ejercicios se han respondido bien alguna vez.
function Ejercicios() {
  const { lectura } = useParams();
  const [data, setData] = useState(null);
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

  const grupo = data
    ? agruparPorLectura(data).find((g) => g.slug === lectura) ?? null
    : null;
  const sesion = grupo?.ejercicios ?? [];

  const cabecera = (
    <header className="lectura-top">
      <Link to="/gramatica" className="lectura-link">← Gramática</Link>
      <h1>{grupo?.titulo ?? 'Gramática'}</h1>
      {grupo ? (
        <span className={`gram-nivel ${grupo.nivel}`}>
          {NOMBRE_NIVEL[grupo.nivel] ?? grupo.nivel}
        </span>
      ) : (
        <span />
      )}
    </header>
  );

  if (data === null) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  if (!grupo || sesion.length === 0) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          No hay ejercicios para esta lectura. Genera más con{' '}
          <code>pipeline/gramatica.py</code>.
        </p>
      </div>
    );
  }

  const reiniciar = () => {
    setIdx(0);
    setElegida(null);
    setResultados([]);
  };

  // Pantalla final
  if (idx >= sesion.length) {
    const r = resumenSesion(resultados);
    const completada = lecturaCompletada(grupo, cargarGramaticaHechos());
    return (
      <div className="lectura-container">
        {cabecera}
        <div className="repaso-fin">
          <p className="repaso-fin-titulo">
            {completada ? 'Lectura completada ✓' : 'Sesión terminada 🎉'}
          </p>
          <p className="repaso-fin-stats">
            {r.aciertos} de {r.total} correcta{r.aciertos === 1 ? '' : 's'} ·{' '}
            {r.porcentaje}%
          </p>
          {!completada && (
            <p className="lectura-subtitulo">
              La palomita llega cuando todos los ejercicios de la lectura se
              hayan respondido bien alguna vez.
            </p>
          )}
          <div className="gram-nav">
            <button type="button" className="gram-boton" onClick={reiniciar}>
              Otra ronda
            </button>
            <Link to="/gramatica" className="gram-boton gram-boton-sec">
              Otras lecturas
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const ejercicio = sesion[idx];
  const meta = data.temas.find((t) => t.id === ejercicio.tema) ?? null;
  const opciones = opcionesDe(ejercicio);
  const respondida = elegida !== null;
  const acerto = respondida && esCorrecta(ejercicio, elegida);

  const elegir = (op) => {
    if (respondida) return;
    setElegida(op);
    const bien = esCorrecta(ejercicio, op);
    setResultados([...resultados, bien]);
    if (bien) {
      const clave = claveEjercicio(ejercicio);
      const hechos = cargarGramaticaHechos();
      if (!hechos.includes(clave)) guardarGramaticaHechos([...hechos, clave]);
    }
  };

  const siguiente = () => {
    setIdx(idx + 1);
    setElegida(null);
  };

  return (
    <div className="lectura-container">
      {cabecera}

      {meta && (
        <details className="gram-leccion">
          <summary>
            {meta.titulo}
            {meta.nivel && (
              <span className={`gram-nivel ${meta.nivel}`}>
                {NOMBRE_NIVEL[meta.nivel] ?? meta.nivel}
              </span>
            )}
            {' '}— ver la regla
          </summary>
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
      )}

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
