import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  NIVELES,
  IDIOMAS,
  NOMBRE_IDIOMA,
  NOMBRE_NIVEL,
  lecturasPorNivel,
} from '../../data/lecturas';
import { cargarBolsa } from '../../engine/almacenamiento';
import { contar } from '../../engine/bolsa';
import './lectura.css';

function Biblioteca() {
  const [idioma, setIdioma] = useState('de');
  const [nivel, setNivel] = useState('principiante');
  const navigate = useNavigate();

  const lecturas = lecturasPorNivel(nivel);
  const totalBolsa = contar(cargarBolsa());

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/" className="lectura-link">← Plataforma</Link>
        <h1>Biblioteca</h1>
        <Link to="/bolsa" className="lectura-link bolsa-badge">
          🎒 Bolsa: {totalBolsa}
        </Link>
      </header>

      <div className="biblioteca-filtros">
        <label>
          Idioma de estudio:
          <select value={idioma} onChange={(e) => setIdioma(e.target.value)}>
            {IDIOMAS.map((i) => (
              <option key={i} value={i}>{NOMBRE_IDIOMA[i]}</option>
            ))}
          </select>
        </label>

        <label>
          Nivel:
          <select value={nivel} onChange={(e) => setNivel(e.target.value)}>
            {NIVELES.map((n) => (
              <option key={n} value={n}>{NOMBRE_NIVEL[n]}</option>
            ))}
          </select>
        </label>
      </div>

      <main className="biblioteca-lista">
        {lecturas.length === 0 && (
          <p className="biblioteca-vacia">
            Aún no hay lecturas de nivel {NOMBRE_NIVEL[nivel].toLowerCase()}. Próximamente.
          </p>
        )}

        {lecturas.map((lectura) => (
          <button
            key={lectura.id}
            className="lectura-card"
            onClick={() => navigate(`/lectura/${idioma}/${nivel}/${lectura.id}`)}
          >
            <span className="lectura-card-titulo">{lectura.titulo[idioma]}</span>
            <span className="lectura-card-meta">
              {NOMBRE_IDIOMA[idioma]} · {NOMBRE_NIVEL[lectura.nivel]}
            </span>
          </button>
        ))}
      </main>
    </div>
  );
}

export default Biblioteca;
