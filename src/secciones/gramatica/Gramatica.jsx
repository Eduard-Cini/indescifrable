import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { agruparPorLectura, lecturaCompletada, totalEjercicios } from '../../engine/gramatica';
import { cargarGramaticaCompletados } from '../../engine/almacenamiento';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import '../lectura/lectura.css';
import './gramatica.css';

// No se importa de data/lecturas para no arrastrar el glob de lecturas al chunk.
const NOMBRE_NIVEL = { principiante: 'Principiante', intermedio: 'Intermedio', avanzado: 'Avanzado' };

// Selector de la Sección 3, organizado POR LECTURA: cada lectura del corpus
// con ejercicios aparece como tarjeta (ordenadas por nivel ascendente), con su
// etiqueta de nivel y una palomita si todos sus ejercicios ya se respondieron
// bien alguna vez. Dentro, los ejercicios van agrupados por tema gramatical.
function Gramatica() {
  const { idioma } = useIdiomaEstudio();
  const [grupos, setGrupos] = useState(null);
  const [hechos, setHechos] = useState([]);

  useEffect(() => {
    let vivo = true;
    import('../../data/gramatica.json').then((m) => {
      if (!vivo) return;
      // false = sin ejercicios para este idioma (p. ej. español): la sección
      // se desactiva en vez de caer al alemán en silencio.
      const bloque = m.default[idioma];
      setGrupos(bloque ? agruparPorLectura(bloque) : false);
      setHechos(cargarGramaticaCompletados());
    });
    return () => {
      vivo = false;
    };
  }, [idioma]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/" className="lectura-link">← Plataforma</Link>
      <h1>Gramática</h1>
      <span />
    </header>
  );

  if (grupos === null) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  if (grupos === false) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          La gramática aún no está disponible en tu idioma de estudio.{' '}
          <Link to="/" className="lectura-link">← Volver a la plataforma</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        Elige una lectura y, dentro, el tema gramatical que quieras practicar
        (ordenados del más básico al más avanzado). Cada tema terminado se
        marca con ✓.
      </p>

      <div className="gram-temas">
        {grupos.map((g) => {
          const completada = lecturaCompletada(g, hechos);
          return (
            <Link key={g.slug} to={`/gramatica/${g.slug}`} className="gram-tema-card">
              <span className={`gram-nivel ${g.nivel}`}>
                {NOMBRE_NIVEL[g.nivel] ?? g.nivel}
              </span>
              <h2>
                {g.titulo}
                {completada && <span className="gram-palomita" title="Completada"> ✓</span>}
              </h2>
              <span className="gram-tema-count">
                {g.temas.length} tema{g.temas.length === 1 ? '' : 's'} ·{' '}
                {totalEjercicios(g)} ejercicio{totalEjercicios(g) === 1 ? '' : 's'}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default Gramatica;
