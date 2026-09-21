import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { cargarLeccion } from './datos';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './mas.css';

// Lección de gramática de un tema de «Más contenidos»: secciones con texto,
// tabla, ejemplos y notas, y al final el acceso a los ejercicios y a las fichas.
function LeccionMas() {
  const { tema } = useParams();
  const [leccion, setLeccion] = useState(undefined); // undefined = cargando

  useEffect(() => {
    let vivo = true;
    cargarLeccion(tema).then((l) => {
      if (vivo) setLeccion(l);
    });
    return () => {
      vivo = false;
    };
  }, [tema]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/mas" className="lectura-link">← Más contenidos</Link>
      <h1>{leccion?.titulo ?? 'Gramática'}</h1>
      <span />
    </header>
  );

  if (leccion === undefined) return <div className="lectura-container">{cabecera}</div>;
  if (leccion === null) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Esta lección no existe. <Link to="/mas" className="lectura-link">Volver</Link>.
        </p>
      </div>
    );
  }

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">{leccion.descripcion}</p>

      {leccion.libro && (
        <section className="leccion-seccion leccion-libro">
          <h2>Lo que explica el libro</h2>
          <p className="leccion-referencia">
            Resumen de la explicación del libro. El original está en: {leccion.libro.referencia}
          </p>
          <ul>
            {leccion.libro.puntos.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </section>
      )}

      {leccion.secciones.map((s) => (
        <section key={s.titulo} className="leccion-seccion">
          <h2>{s.titulo}</h2>
          {s.texto?.map((p) => (
            <p key={p}>{p}</p>
          ))}
          {s.tabla && (
            <div className="mas-tabla-envoltura">
              <table className="gram-tabla">
                <thead>
                  <tr>
                    {s.tabla.cabecera.map((c, i) => (
                      <th key={i}>{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {s.tabla.filas.map((fila, i) => (
                    <tr key={i}>
                      {fila.map((celda, j) => (
                        <td key={j}>{celda}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {s.ejemplos && (
            <ul className="leccion-ejemplos">
              {s.ejemplos.map((e) => (
                <li key={e.de}>
                  <span className="de">{e.de}</span>
                  <span className="es">{e.es}</span>
                </li>
              ))}
            </ul>
          )}
          {s.notas?.map((n) => (
            <p key={n} className="leccion-nota">{n}</p>
          ))}
        </section>
      ))}

      <div className="mas-acciones">
        <Link to={`/mas/gramatica/${tema}/ejercicios`} className="gram-boton">
          Ir a los ejercicios
        </Link>
        {leccion.mazo && (
          <Link to={`/mas/vocabulario/${leccion.mazo}`} className="gram-boton gram-boton-sec">
            Fichas de vocabulario
          </Link>
        )}
      </div>
      <p className="mas-fuente">{leccion.fuente}</p>
    </div>
  );
}

export default LeccionMas;
