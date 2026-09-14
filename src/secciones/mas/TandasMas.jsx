import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { cargarMasCompletados } from '../../engine/almacenamiento';
import { claveTanda } from '../../engine/ejercicios';
import { cargarEjercicios } from './datos';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './mas.css';

// Subsección de ejercicios de un tema: una tarjeta por tanda, con ✓ cuando se
// terminó alguna vez sin fallos (como la palomita de Gramática).
function TandasMas() {
  const { tema } = useParams();
  const [banco, setBanco] = useState(undefined); // undefined = cargando
  const [hechas, setHechas] = useState([]);

  useEffect(() => {
    let vivo = true;
    cargarEjercicios(tema).then((b) => {
      if (!vivo) return;
      setBanco(b);
      setHechas(cargarMasCompletados());
    });
    return () => {
      vivo = false;
    };
  }, [tema]);

  const cabecera = (
    <header className="lectura-top">
      <Link to={`/mas/gramatica/${tema}`} className="lectura-link">← Lección</Link>
      <h1>Ejercicios: {banco?.titulo ?? tema}</h1>
      <span />
    </header>
  );

  if (banco === undefined) return <div className="lectura-container">{cabecera}</div>;
  if (banco === null) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          No hay ejercicios de este tema. <Link to="/mas" className="lectura-link">Volver</Link>.
        </p>
      </div>
    );
  }

  return (
    <div className="lectura-container">
      {cabecera}
      <p className="lectura-subtitulo">
        {banco.nota} Cada tanda se marca con ✓ al terminarla sin fallos.
      </p>
      <div className="gram-temas">
        {banco.tandas.map((t) => (
          <Link
            key={t.id}
            to={`/mas/gramatica/${tema}/ejercicios/${t.id}`}
            className="gram-tema-card"
          >
            <h2>
              {t.titulo}
              {hechas.includes(claveTanda(tema, t.id)) && (
                <span className="gram-palomita" title="Terminada sin fallos"> ✓</span>
              )}
            </h2>
            <p>{t.instruccion}</p>
            <span className="gram-tema-count">
              {t.ejercicios.length} ejercicio{t.ejercicios.length === 1 ? '' : 's'}
            </span>
            {t.modelo && <span className="mas-modelo">Modelo: {t.modelo}</span>}
          </Link>
        ))}
      </div>
    </div>
  );
}

export default TandasMas;
