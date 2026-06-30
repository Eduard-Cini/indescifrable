import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { obtenerLectura, NOMBRE_IDIOMA } from '../../data/lecturas';
import lexico from '../../data/lexico.json';
import { cargarBolsa, guardarBolsa } from '../../engine/almacenamiento';
import { agregarPalabra, crearEntrada, clavePalabra, tienePalabra } from '../../engine/bolsa';
import PopupPalabra from './PopupPalabra';
import './lectura.css';

// Separa una frase en palabras (clicables) y separadores (puntuación/espacios).
function tokenizar(frase) {
  const tokens = [];
  const re = /\p{L}[\p{L}\p{M}'’-]*/gu;
  let ultimo = 0;
  let m;
  while ((m = re.exec(frase)) !== null) {
    if (m.index > ultimo) tokens.push({ tipo: 'sep', valor: frase.slice(ultimo, m.index) });
    tokens.push({ tipo: 'palabra', valor: m[0] });
    ultimo = m.index + m[0].length;
  }
  if (ultimo < frase.length) tokens.push({ tipo: 'sep', valor: frase.slice(ultimo) });
  return tokens;
}

function Lector() {
  const { idioma, id } = useParams();
  const lectura = obtenerLectura(id);

  const [bolsa, setBolsa] = useState([]);
  const [seleccion, setSeleccion] = useState(null); // { surface, lemma, traduccionEs, id }
  const [traducidas, setTraducidas] = useState({}); // traducción revelada por frase (índice -> bool)

  useEffect(() => {
    setBolsa(cargarBolsa());
  }, []);

  if (!lectura) {
    return (
      <div className="lectura-container">
        <p>Lectura no encontrada.</p>
        <Link to="/lectura" className="lectura-link">← Biblioteca</Link>
      </div>
    );
  }

  const frases = lectura.cuerpo[idioma] ?? [];
  const traduccionFrases = lectura.cuerpo.es ?? [];
  const esEspanol = idioma === 'es';

  const seleccionarPalabra = (superficie) => {
    const id = clavePalabra(idioma, superficie);
    const entradaLex = lexico[id];
    setSeleccion({
      surface: superficie,
      lemma: entradaLex?.lemma ?? superficie,
      traduccionEs: esEspanol ? null : entradaLex?.es ?? null,
      id,
    });
  };

  const agregarABolsa = () => {
    if (!seleccion) return;
    const entrada = crearEntrada({
      lang: idioma,
      surface: seleccion.surface,
      lemma: seleccion.lemma,
      traducciones: seleccion.traduccionEs ? { es: seleccion.traduccionEs } : {},
      origen: 'manual',
    });
    const nueva = agregarPalabra(bolsa, entrada);
    setBolsa(nueva);
    guardarBolsa(nueva);
    setSeleccion(null);
  };

  const toggleFrase = (i) =>
    setTraducidas((prev) => ({ ...prev, [i]: !prev[i] }));

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/lectura" className="lectura-link">← Biblioteca</Link>
        <h1>{lectura.titulo[idioma]}</h1>
        <Link to="/bolsa" className="lectura-link bolsa-badge">🎒 {bolsa.length}</Link>
      </header>

      <p className="lectura-subtitulo">
        Leyendo en <strong>{NOMBRE_IDIOMA[idioma]}</strong>. Toca una palabra para
        traducirla y guardarla{!esEspanol && ', o el ⇄ del margen para traducir la frase'}.
      </p>

      <article className="lectura-texto">
        {frases.map((frase, i) => {
          const visible = traducidas[i] && !esEspanol;
          return (
            <div key={i} className="lectura-frase">
              {!esEspanol && (
                <button
                  className={'frase-toggle' + (visible ? ' activo' : '')}
                  onClick={() => toggleFrase(i)}
                  aria-label="Traducir esta frase"
                  title="Traducir esta frase"
                >
                  ⇄
                </button>
              )}
              <p>
                {tokenizar(frase).map((t, j) =>
                  t.tipo === 'palabra' ? (
                    <span
                      key={j}
                      className={
                        'palabra' +
                        (tienePalabra(bolsa, clavePalabra(idioma, t.valor)) ? ' en-bolsa' : '')
                      }
                      onClick={() => seleccionarPalabra(t.valor)}
                    >
                      {t.valor}
                    </span>
                  ) : (
                    <span key={j}>{t.valor}</span>
                  )
                )}
              </p>

              {visible && <p className="frase-traducida">{traduccionFrases[i]}</p>}
            </div>
          );
        })}
      </article>

      {seleccion && (
        <PopupPalabra
          seleccion={seleccion}
          esEspanol={esEspanol}
          yaEnBolsa={tienePalabra(bolsa, seleccion.id)}
          onAgregar={agregarABolsa}
          onCerrar={() => setSeleccion(null)}
        />
      )}
    </div>
  );
}

export default Lector;
