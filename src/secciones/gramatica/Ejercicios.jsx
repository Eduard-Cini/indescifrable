import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  agruparPorLectura,
  claveGrupo,
  opcionesDe,
  esCorrecta,
  resumenSesion,
} from '../../engine/gramatica';
import {
  cargarGramaticaCompletados,
  guardarGramaticaCompletados,
} from '../../engine/almacenamiento';
import '../lectura/lectura.css';
import './gramatica.css';

const NOMBRE_NIVEL = { principiante: 'Principiante', intermedio: 'Intermedio', avanzado: 'Avanzado' };

// Tanda de ejercicios de UN tema dentro de UNA lectura. Al llegar al final se
// registra (lectura|tema) como terminado: esa es la palomita del índice.
function Ejercicios() {
  const { lectura, tema } = useParams();
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
  const subgrupo = grupo?.temas.find((t) => t.id === tema) ?? null;
  const sesion = subgrupo?.ejercicios ?? [];
  const meta = data?.temas.find((t) => t.id === tema) ?? null;

  const cabecera = (
    <header className="lectura-top">
      <Link to={`/gramatica/${lectura}`} className="lectura-link">
        ← {grupo?.titulo ?? 'Gramática'}
      </Link>
      <h1>{subgrupo?.titulo ?? 'Gramática'}</h1>
      {subgrupo ? (
        <span className={`gram-nivel ${subgrupo.nivel}`}>
          {NOMBRE_NIVEL[subgrupo.nivel] ?? subgrupo.nivel}
        </span>
      ) : (
        <span />
      )}
    </header>
  );

  if (data === null) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  if (!grupo || !subgrupo || sesion.length === 0) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          No hay ejercicios de este tema para esta lectura.{' '}
          <Link to="/gramatica" className="lectura-link">Volver a Gramática</Link>.
        </p>
      </div>
    );
  }

  const reiniciar = () => {
    setIdx(0);
    setElegida(null);
    setResultados([]);
  };

  const siguiente = () => {
    const proximo = idx + 1;
    if (proximo >= sesion.length) {
      // Tanda terminada: se registra (lectura|tema) → palomita en el índice.
      const clave = claveGrupo(grupo, subgrupo.id);
      const hechos = cargarGramaticaCompletados();
      if (!hechos.includes(clave)) guardarGramaticaCompletados([...hechos, clave]);
    }
    setIdx(proximo);
    setElegida(null);
  };

  // Pantalla final
  if (idx >= sesion.length) {
    const r = resumenSesion(resultados);
    return (
      <div className="lectura-container">
        {cabecera}
        <div className="repaso-fin">
          <p className="repaso-fin-titulo">Tema terminado ✓</p>
          <p className="repaso-fin-stats">
            {r.aciertos} de {r.total} correcta{r.aciertos === 1 ? '' : 's'} ·{' '}
            {r.porcentaje}%
          </p>
          <div className="gram-nav">
            <button type="button" className="gram-boton" onClick={reiniciar}>
              Otra ronda
            </button>
            <Link to={`/gramatica/${lectura}`} className="gram-boton gram-boton-sec">
              Otros temas
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

  return (
    <div className="lectura-container">
      {cabecera}

      {meta && (
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
              {idx + 1 < sesion.length ? 'Siguiente' : 'Terminar'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Ejercicios;
