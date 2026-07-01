import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  NIVELES,
  IDIOMAS,
  NOMBRE_IDIOMA,
  NOMBRE_NIVEL,
  lecturasDisponibles,
} from '../../data/lecturas';
import { cargarBolsa, cargarProgreso } from '../../engine/almacenamiento';
import { contar } from '../../engine/bolsa';
import { estaCompletada, contarCompletadas } from '../../engine/progreso';
import './lectura.css';

function Biblioteca() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();

  // idioma y nivel viven en la URL para conservarse al volver de una lectura
  const idioma = IDIOMAS.includes(params.get('idioma')) ? params.get('idioma') : 'de';
  const nivel = NIVELES.includes(params.get('nivel')) ? params.get('nivel') : 'principiante';

  const setFiltro = (clave, valor) => {
    const next = new URLSearchParams(params);
    next.set(clave, valor);
    setParams(next, { replace: true });
  };

  const lecturas = lecturasDisponibles(nivel, idioma);
  const completadas = cargarProgreso();
  const totalBolsa = contar(cargarBolsa());
  const hechas = contarCompletadas(completadas, lecturas.map((l) => l.id));

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/" className="lectura-link">← Plataforma</Link>
        <h1>Biblioteca</h1>
        <Link to="/bolsa" className="lectura-link bolsa-badge">🎒 Bolsa: {totalBolsa}</Link>
      </header>

      <div className="biblioteca-filtros">
        <label>
          Idioma de estudio:
          <select value={idioma} onChange={(e) => setFiltro('idioma', e.target.value)}>
            {IDIOMAS.map((i) => (
              <option key={i} value={i}>{NOMBRE_IDIOMA[i]}</option>
            ))}
          </select>
        </label>

        <label>
          Nivel:
          <select value={nivel} onChange={(e) => setFiltro('nivel', e.target.value)}>
            {NIVELES.map((n) => (
              <option key={n} value={n}>{NOMBRE_NIVEL[n]}</option>
            ))}
          </select>
        </label>
      </div>

      {lecturas.length > 0 && (
        <p className="biblioteca-progreso">
          Completadas: {hechas} de {lecturas.length} en este nivel.
        </p>
      )}

      <main className="biblioteca-lista">
        {lecturas.length === 0 && (
          <p className="biblioteca-vacia">
            No hay lecturas de nivel {NOMBRE_NIVEL[nivel].toLowerCase()} en {NOMBRE_IDIOMA[idioma]}.
          </p>
        )}

        {lecturas.map((lectura) => {
          const hecha = estaCompletada(completadas, lectura.id);
          return (
            <button
              key={lectura.id}
              className={'lectura-card' + (hecha ? ' completada' : '')}
              onClick={() =>
                navigate(`/lectura/${idioma}/${nivel}/${lectura.id}`)
              }
            >
              <span className="lectura-card-titulo">
                {hecha && <span className="check-completada">✓</span>}
                {lectura.titulo[idioma]}
              </span>
              <span className="lectura-card-meta">
                {NOMBRE_IDIOMA[idioma]} · {NOMBRE_NIVEL[lectura.nivel]}
              </span>
            </button>
          );
        })}
      </main>
    </div>
  );
}

export default Biblioteca;
