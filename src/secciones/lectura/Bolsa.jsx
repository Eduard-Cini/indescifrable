import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { cargarBolsa, guardarBolsa } from '../../engine/almacenamiento';
import { quitarPalabra } from '../../engine/bolsa';
import { estaPendiente } from '../../engine/srs';
import './lectura.css';

function estadoRepaso(p, ahora) {
  if (!p.srs) return 'nueva';
  if (estaPendiente(p, ahora)) return 'pendiente de repaso';
  const dias = Math.ceil(
    (Date.parse(p.srs.vencimiento) - Date.parse(ahora)) / (24 * 60 * 60 * 1000)
  );
  return `vuelve en ${dias} día(s)`;
}

function Bolsa() {
  const [bolsa, setBolsa] = useState([]);
  const [confirmando, setConfirmando] = useState(null);

  useEffect(() => {
    setBolsa(cargarBolsa());
  }, []);

  const quitar = (id) => {
    const nueva = quitarPalabra(bolsa, id);
    setBolsa(nueva);
    guardarBolsa(nueva);
    setConfirmando(null);
  };

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/lectura" className="lectura-link">← Biblioteca</Link>
        <h1>Tu bolsa de palabras</h1>
        <Link to="/" className="lectura-link">Plataforma →</Link>
      </header>

      <p className="lectura-subtitulo">
        {bolsa.length === 0 ? (
          'Tu bolsa está vacía. Guarda palabras desde una lectura.'
        ) : (
          <>
            {bolsa.length} palabra(s).{' '}
            <Link to="/repaso" className="lectura-link">
              Repásalas con repetición espaciada →
            </Link>
          </>
        )}
      </p>

      <ul className="bolsa-lista">
        {bolsa.map((p) => (
          <li key={p.id} className="bolsa-item">
            <div className="bolsa-item-info">
              <span className="bolsa-palabra">
                {p.surface}
                {p.lemma && p.lemma.toLowerCase() !== p.surface.toLowerCase() && (
                  <span className="bolsa-lemma"> ({p.lemma})</span>
                )}
              </span>
              {p.traducciones?.es && (
                <span className="bolsa-meta">{p.traducciones.es}</span>
              )}
              <span className="bolsa-srs">
                {estadoRepaso(p, new Date().toISOString())}
              </span>
            </div>
            {confirmando === p.id ? (
              <div className="bolsa-confirm">
                <span className="bolsa-confirm-txt">¿Quitar?</span>
                <button className="bolsa-confirm-si" onClick={() => quitar(p.id)}>
                  Sí
                </button>
                <button className="bolsa-confirm-no" onClick={() => setConfirmando(null)}>
                  No
                </button>
              </div>
            ) : (
              <button
                className="bolsa-quitar"
                onClick={() => setConfirmando(p.id)}
                aria-label="Quitar palabra"
                title="Quitar"
              >
                ✕
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Bolsa;
