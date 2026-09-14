import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { opcionesDe, esCorrecta, resumenSesion } from '../../engine/gramatica';
import { segmentos, rellenar, claveTanda } from '../../engine/ejercicios';
import {
  cargarMasCompletados,
  guardarMasCompletados,
} from '../../engine/almacenamiento';
import { cargarEjercicios } from './datos';
import '../lectura/lectura.css';
import '../repaso/repaso.css';
import '../gramatica/gramatica.css';
import './mas.css';

// Una tanda de ejercicios de opción múltiple. Cada opción puede rellenar
// varios huecos a la vez («wird … gebaut»); si el ejercicio no tiene huecos,
// las opciones son frases completas. Sin fallos en la ronda → ✓ de la tanda.
function TandaMas() {
  const { tema, tanda } = useParams();
  const [banco, setBanco] = useState(undefined); // undefined = cargando
  const [idx, setIdx] = useState(0);
  const [elegida, setElegida] = useState(null);
  const [resultados, setResultados] = useState([]);

  useEffect(() => {
    let vivo = true;
    cargarEjercicios(tema).then((b) => {
      if (!vivo) return;
      setBanco(b);
      setIdx(0);
      setElegida(null);
      setResultados([]);
    });
    return () => {
      vivo = false;
    };
  }, [tema, tanda]);

  const t = banco?.tandas.find((x) => x.id === tanda) ?? null;
  const sesion = t?.ejercicios ?? [];
  const volver = `/mas/gramatica/${tema}/ejercicios`;

  const cabecera = (
    <header className="lectura-top">
      <Link to={volver} className="lectura-link">← Ejercicios</Link>
      <h1>{t?.titulo ?? 'Ejercicios'}</h1>
      <span />
    </header>
  );

  if (banco === undefined) return <div className="lectura-container">{cabecera}</div>;
  if (!t) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Esta tanda no existe. <Link to={volver} className="lectura-link">Volver</Link>.
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
    if (
      proximo >= sesion.length &&
      resultados.length === sesion.length &&
      resultados.every(Boolean)
    ) {
      const clave = claveTanda(tema, tanda);
      const hechas = cargarMasCompletados();
      if (!hechas.includes(clave)) guardarMasCompletados([...hechas, clave]);
    }
    setIdx(proximo);
    setElegida(null);
  };

  // Pantalla final
  if (idx >= sesion.length) {
    const r = resumenSesion(resultados);
    const perfecta = r.total === sesion.length && r.fallos === 0;
    return (
      <div className="lectura-container">
        {cabecera}
        <div className="repaso-fin">
          <p className="repaso-fin-titulo">{perfecta ? 'Tanda completada ✓' : 'Tanda terminada'}</p>
          <p className="repaso-fin-stats">
            {r.aciertos} de {r.total} correcta{r.aciertos === 1 ? '' : 's'} · {r.porcentaje}%
          </p>
          {!perfecta && (
            <p className="lectura-subtitulo">La ✓ llega con una ronda sin fallos. ¡Otra ronda!</p>
          )}
          <div className="gram-nav">
            <button type="button" className="gram-boton" onClick={reiniciar}>
              Otra ronda
            </button>
            <Link to={volver} className="gram-boton gram-boton-sec">
              Otras tandas
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const ej = sesion[idx];
  const opciones = opcionesDe(ej);
  const respondida = elegida !== null;
  const acerto = respondida && esCorrecta(ej, elegida);
  const frases = !ej.partes;

  const elegir = (op) => {
    if (respondida) return;
    setElegida(op);
    setResultados([...resultados, esCorrecta(ej, op)]);
  };

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        {t.instruccion} <span className="mas-modelo">(modelo: {t.modelo})</span>
      </p>
      <p className="lectura-subtitulo">
        {idx + 1} / {sesion.length}
      </p>

      {frases ? (
        <p className="mas-pregunta">{ej.pregunta}</p>
      ) : (
        <p className="gram-frase">
          {segmentos(ej, elegida).map((s, i) =>
            'texto' in s ? (
              <span key={i}>{s.texto}</span>
            ) : (
              <span
                key={i}
                className={`gram-hueco${respondida ? (acerto ? ' bien' : ' mal') : ''}`}
              >
                {s.hueco ?? '_____'}
              </span>
            )
          )}
        </p>
      )}

      <div className={`gram-opciones${frases ? ' frases' : ''}`}>
        {opciones.map((op) => {
          let estado = '';
          if (respondida) {
            if (op === ej.respuesta) estado = ' correcta';
            else if (op === elegida) estado = ' incorrecta';
          }
          return (
            <button
              key={op}
              type="button"
              className={`gram-opcion${frases ? ' frase' : ''}${estado}`}
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
            {acerto ? '✓ Correcto' : `✗ Lo correcto: «${rellenar(ej, ej.respuesta)}»`}
          </p>
          {ej.pista && <p className="gram-pista">{ej.pista}</p>}
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

export default TandaMas;
