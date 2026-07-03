import { useRef, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  cargarBolsa,
  guardarBolsa,
  cargarIdiomaEstudio,
  exportarPerfil,
  importarPerfil,
} from '../../engine/almacenamiento';
import { quitarPalabra } from '../../engine/bolsa';
import { estaPendiente } from '../../engine/srs';
import { useIdiomaEstudio } from '../../contexto/idiomaEstudio';
import SelectorIdioma from '../../componentes/SelectorIdioma';
import { NOMBRE_IDIOMA } from '../../data/lecturas';
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
  const { idioma, setIdioma } = useIdiomaEstudio();
  const [bolsa, setBolsa] = useState([]); // bolsa COMPLETA (todos los idiomas)
  const [confirmando, setConfirmando] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const inputArchivo = useRef(null);

  useEffect(() => {
    setBolsa(cargarBolsa());
  }, []);

  const bolsaIdioma = bolsa.filter((p) => p.lang === idioma);

  const quitar = (id) => {
    const nueva = quitarPalabra(bolsa, id);
    setBolsa(nueva);
    guardarBolsa(nueva);
    setConfirmando(null);
  };

  const exportar = () => {
    const perfil = exportarPerfil();
    const blob = new Blob([JSON.stringify(perfil, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = `indescifrable-perfil-${new Date().toISOString().slice(0, 10)}.json`;
    enlace.click();
    URL.revokeObjectURL(url);
    setMensaje('Progreso exportado.');
  };

  const importar = (evento) => {
    const archivo = evento.target.files?.[0];
    evento.target.value = ''; // permite reimportar el mismo archivo
    if (!archivo) return;
    const lector = new FileReader();
    lector.onload = () => {
      try {
        const n = importarPerfil(JSON.parse(lector.result));
        setBolsa(cargarBolsa());
        setIdioma(cargarIdiomaEstudio());
        setMensaje(`Progreso importado (${n} sección(es) restaurada(s)).`);
      } catch (err) {
        setMensaje(`No se pudo importar: ${err.message}`);
      }
    };
    lector.readAsText(archivo);
  };

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/lectura" className="lectura-link">← Biblioteca</Link>
        <h1>Tu bolsa de palabras</h1>
        <SelectorIdioma />
      </header>

      <div className="bolsa-perfil">
        <button className="bolsa-perfil-btn" onClick={exportar}>
          ⬇ Exportar progreso
        </button>
        <button
          className="bolsa-perfil-btn"
          onClick={() => inputArchivo.current?.click()}
        >
          ⬆ Importar progreso
        </button>
        <input
          ref={inputArchivo}
          type="file"
          accept="application/json,.json"
          onChange={importar}
          hidden
        />
        {mensaje && <span className="bolsa-perfil-msg">{mensaje}</span>}
      </div>

      <p className="lectura-subtitulo">
        {bolsaIdioma.length === 0 ? (
          `Tu bolsa de ${NOMBRE_IDIOMA[idioma]} está vacía. Guarda palabras desde una lectura.`
        ) : (
          <>
            {bolsaIdioma.length} palabra(s) en {NOMBRE_IDIOMA[idioma]}.{' '}
            <Link to="/repaso" className="lectura-link">
              Repásalas con repetición espaciada →
            </Link>
          </>
        )}
      </p>

      <ul className="bolsa-lista">
        {bolsaIdioma.map((p) => (
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
