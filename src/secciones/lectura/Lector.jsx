import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { obtenerLectura, NOMBRE_IDIOMA } from '../../data/lecturas';
import lexico from '../../data/lexico.json';
import {
  cargarBolsa,
  guardarBolsa,
  cargarProgreso,
  guardarProgreso,
} from '../../engine/almacenamiento';
import { agregarPalabra, crearEntrada, clavePalabra, tienePalabra } from '../../engine/bolsa';
import { marcarCompletada, estaCompletada } from '../../engine/progreso';
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
  const { idioma, nivel, id } = useParams();
  const navigate = useNavigate();
  const lectura = obtenerLectura(id);

  const [bolsa, setBolsa] = useState([]);
  const [seleccion, setSeleccion] = useState(null); // { surface, lemma, traduccionEs, id }
  const [traducidas, setTraducidas] = useState({}); // traducción revelada por frase (índice -> bool)
  const [completada, setCompletada] = useState(false);

  useEffect(() => {
    setBolsa(cargarBolsa());
    setCompletada(estaCompletada(cargarProgreso(), id));
  }, [id]);

  // Enlace de vuelta que conserva el idioma y nivel elegidos en la Biblioteca.
  const volverBiblioteca = `/lectura?idioma=${idioma}&nivel=${nivel}`;

  if (!lectura) {
    return (
      <div className="lectura-container">
        <p>Lectura no encontrada.</p>
        <Link to={volverBiblioteca} className="lectura-link">← Biblioteca</Link>
      </div>
    );
  }

  const frases = lectura.cuerpo[idioma];
  const traduccionFrases = lectura.cuerpo.es ?? [];
  const esEspanol = idioma === 'es';

  if (!frases) {
    return (
      <div className="lectura-container">
        <p>Esta lectura no está disponible en {NOMBRE_IDIOMA[idioma] ?? idioma}.</p>
        <Link to={volverBiblioteca} className="lectura-link">← Biblioteca</Link>
      </div>
    );
  }

  const finalizarLectura = () => {
    guardarProgreso(marcarCompletada(cargarProgreso(), id));
    navigate(volverBiblioteca);
  };

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
        <Link to={volverBiblioteca} className="lectura-link">← Biblioteca</Link>
        <h1>{lectura.titulo[idioma]}</h1>
        <Link to="/bolsa" className="lectura-link bolsa-badge">🎒 {bolsa.length}</Link>
      </header>

      {lectura.autor && <p className="lectura-autor">{lectura.autor}</p>}

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

      <div className="lectura-fin">
        <button className="btn-finalizar" onClick={finalizarLectura}>
          {completada ? '✓ Leída — volver a la biblioteca' : 'Finalizar lectura'}
        </button>
      </div>

      {lectura.fuente && <p className="lectura-fuente">{lectura.fuente}</p>}

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
