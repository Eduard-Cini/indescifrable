import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { cargarBolsa, guardarBolsa } from '../../engine/almacenamiento';
import { quitarPalabra } from '../../engine/bolsa';
import { NOMBRE_IDIOMA } from '../../data/lecturas';
import './lectura.css';

function Bolsa() {
  const [bolsa, setBolsa] = useState([]);

  useEffect(() => {
    setBolsa(cargarBolsa());
  }, []);

  const quitar = (id) => {
    const nueva = quitarPalabra(bolsa, id);
    setBolsa(nueva);
    guardarBolsa(nueva);
  };

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/lectura" className="lectura-link">← Biblioteca</Link>
        <h1>Tu bolsa de palabras</h1>
        <Link to="/" className="lectura-link">Plataforma →</Link>
      </header>

      <p className="lectura-subtitulo">
        {bolsa.length === 0
          ? 'Tu bolsa está vacía. Guarda palabras desde una lectura.'
          : `${bolsa.length} palabra(s). Aquí vivirá el repaso espaciado (Sección 2).`}
      </p>

      <ul className="bolsa-lista">
        {bolsa.map((p) => (
          <li key={p.id} className="bolsa-item">
            <div className="bolsa-item-info">
              <span className="bolsa-palabra">{p.surface}</span>
              {p.lemma && p.lemma.toLowerCase() !== p.surface.toLowerCase() && (
                <span className="bolsa-lemma">({p.lemma})</span>
              )}
              <span className="bolsa-meta">
                {NOMBRE_IDIOMA[p.lang] ?? p.lang}
                {p.traducciones?.es ? ` · ${p.traducciones.es}` : ''}
              </span>
            </div>
            <button className="bolsa-quitar" onClick={() => quitar(p.id)}>
              Quitar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Bolsa;
