import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import '../lectura/lectura.css';
import './gramatica.css';

// Selector de temas de la Sección 3. Los ejercicios se generan offline con
// pipeline/gramatica.py; aquí solo se presenta el catálogo de temas (la lección)
// y se enlaza a cada sesión de práctica.
function Gramatica() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let vivo = true;
    import('../../data/gramatica.json').then((m) => {
      if (vivo) setData(m.default);
    });
    return () => {
      vivo = false;
    };
  }, []);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/" className="lectura-link">← Plataforma</Link>
      <h1>Gramática</h1>
      <span />
    </header>
  );

  if (data === null) {
    return <div className="lectura-container">{cabecera}</div>;
  }

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        Elige un tema. Se presenta la regla y luego practicas con ejercicios de
        completar (cloze) extraídos de las lecturas en alemán.
      </p>

      <div className="gram-temas">
        {data.temas.map((tema) => {
          const n = data.ejercicios[tema.id]?.length ?? 0;
          return (
            <Link key={tema.id} to={`/gramatica/${tema.id}`} className="gram-tema-card">
              <h2>{tema.titulo}</h2>
              <p>{tema.resumen}</p>
              <span className="gram-tema-count">
                {n} ejercicio{n === 1 ? '' : 's'}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default Gramatica;
