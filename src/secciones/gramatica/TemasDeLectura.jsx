import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  agruparPorLectura,
  temaCompletado,
} from '../../engine/gramatica';
import { cargarGramaticaCompletados } from '../../engine/almacenamiento';
import '../lectura/lectura.css';
import './gramatica.css';

const NOMBRE_NIVEL = { principiante: 'Principiante', intermedio: 'Intermedio', avanzado: 'Avanzado' };

// Índice de una lectura: sus temas gramaticales como tarjetas, en orden de
// dificultad. El usuario elige cuál practicar; el tema terminado lleva ✓.
function TemasDeLectura() {
  const { lectura } = useParams();
  const [grupo, setGrupo] = useState(null);
  const [completados, setCompletados] = useState([]);
  const [cargado, setCargado] = useState(false);

  useEffect(() => {
    let vivo = true;
    import('../../data/gramatica.json').then((m) => {
      if (!vivo) return;
      setGrupo(agruparPorLectura(m.default).find((g) => g.slug === lectura) ?? null);
      setCompletados(cargarGramaticaCompletados());
      setCargado(true);
    });
    return () => {
      vivo = false;
    };
  }, [lectura]);

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

  if (!cargado) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  if (!grupo) {
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

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        Elige un tema para practicar. Se marca con ✓ al completar una ronda
        con todas las respuestas correctas.
      </p>

      <div className="gram-temas">
        {grupo.temas.map((t) => {
          const hecho = temaCompletado(grupo, t.id, completados);
          return (
            <Link
              key={t.id}
              to={`/gramatica/${grupo.slug}/${t.id}`}
              className="gram-tema-card"
            >
              <span className={`gram-nivel ${t.nivel}`}>
                {NOMBRE_NIVEL[t.nivel] ?? t.nivel}
              </span>
              <h2>
                {t.titulo}
                {hecho && <span className="gram-palomita" title="Terminado"> ✓</span>}
              </h2>
              <span className="gram-tema-count">
                {t.ejercicios.length} ejercicio{t.ejercicios.length === 1 ? '' : 's'}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default TemasDeLectura;
