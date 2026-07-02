import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { obtenerLectura, NOMBRE_IDIOMA, partesDeLibro } from '../../data/lecturas';
import {
  cargarBolsa,
  guardarBolsa,
  cargarProgreso,
  guardarProgreso,
  cargarConocidas,
  cargarRepasoPrevio,
  guardarRepasoPrevio,
} from '../../engine/almacenamiento';
import { agregarPalabra, crearEntrada, clavePalabra, tienePalabra } from '../../engine/bolsa';
import { marcarCompletada, estaCompletada } from '../../engine/progreso';
import { tokenizar } from '../../engine/tokenizar';
import { candidatasRepasoPrevio } from '../../engine/conocimiento';
import PopupPalabra from './PopupPalabra';
import RepasoPrevio from './RepasoPrevio';
import './lectura.css';

function Lector() {
  const { idioma, nivel, id } = useParams();
  const navigate = useNavigate();
  const lectura = obtenerLectura(id);

  const [bolsa, setBolsa] = useState([]);
  const [seleccion, setSeleccion] = useState(null); // { surface, lemma, traduccionEs, id }
  const [traducidas, setTraducidas] = useState({}); // traducción revelada por frase (índice -> bool)
  const [completada, setCompletada] = useState(false);
  // El léxico (~465 KB) y las frecuencias se cargan bajo demanda para no inflar
  // el bundle inicial: Vite los emite como chunks aparte, cacheados, que solo
  // se descargan al abrir una lectura.
  const [lexico, setLexico] = useState(null);
  const [frecuencias, setFrecuencias] = useState(null);
  // Repaso previo: { paraId, fichas } — guarda a qué lectura pertenece para
  // que un render intermedio al navegar entre lecturas no use fichas viejas.
  const [previo, setPrevio] = useState(null);
  const fichasPrevio = previo?.paraId === id ? previo.fichas : null;

  useEffect(() => {
    setBolsa(cargarBolsa());
    setCompletada(estaCompletada(cargarProgreso(), id));
  }, [id]);

  useEffect(() => {
    import('../../data/lexico.json').then((m) => setLexico(m.default));
    import('../../data/frecuencias.json').then((m) => setFrecuencias(m.default));
  }, []);

  // Decide el repaso previo cuando hay datos: solo en idioma extranjero y como
  // mucho una vez al día por lectura (para no estorbar relecturas).
  useEffect(() => {
    if (!lectura?.cuerpo?.[idioma]) return;
    if (idioma === 'es' || !lexico || !frecuencias) {
      if (idioma === 'es') setPrevio({ paraId: id, fichas: [] });
      return;
    }
    const hoy = new Date().toISOString().slice(0, 10);
    const fichas =
      cargarRepasoPrevio()[id]?.slice(0, 10) === hoy
        ? []
        : candidatasRepasoPrevio(lectura, idioma, {
            bolsa: cargarBolsa(),
            lexico,
            frecuencias,
            conocidas: cargarConocidas(),
            ahora: new Date().toISOString(),
          });
    setPrevio({ paraId: id, fichas });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, idioma, lexico, frecuencias]);

  const terminarPrevio = () => {
    guardarRepasoPrevio({ ...cargarRepasoPrevio(), [id]: new Date().toISOString() });
    setPrevio({ paraId: id, fichas: [] });
  };

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

  // La traducción por frase (marcador ⇄) requiere una versión española
  // alineada. Los libros procesados por el pipeline son solo texto original.
  const hayTraduccionFrase =
    !esEspanol &&
    Array.isArray(lectura.cuerpo.es) &&
    lectura.cuerpo.es.length === frases.length;

  // Navegación entre partes cuando la lectura pertenece a un libro.
  const esLibro = !!lectura.libro;
  const hermanas = esLibro ? partesDeLibro(lectura.libro) : [];
  const anterior = esLibro ? hermanas.find((p) => p.parte === lectura.parte - 1) : null;
  const siguiente = esLibro ? hermanas.find((p) => p.parte === lectura.parte + 1) : null;
  const rutaParte = (p) => `/lectura/${idioma}/${nivel}/${p.id}`;

  const finalizarLectura = () => {
    guardarProgreso(marcarCompletada(cargarProgreso(), id));
    navigate(siguiente ? rutaParte(siguiente) : volverBiblioteca);
  };

  const seleccionarPalabra = (superficie) => {
    const id = clavePalabra(idioma, superficie);
    // El override por lectura (verbos separables desambiguados) manda sobre el
    // léxico global, que es context-free y no puede distinguir p. ej. "nahm"
    // como parte de "annehmen" frente a "nehmen".
    const entradaLex = lectura.lexico?.[id] ?? lexico?.[id];
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
      {esLibro && (
        <p className="lectura-parte">Parte {lectura.parte} de {lectura.partes}</p>
      )}

      {fichasPrevio === null && !esEspanol ? (
        <p className="lectura-subtitulo">Preparando la lectura…</p>
      ) : fichasPrevio?.length > 0 ? (
        <RepasoPrevio
          key={id}
          candidatas={fichasPrevio}
          idioma={idioma}
          bolsa={bolsa}
          onBolsa={setBolsa}
          onTerminar={terminarPrevio}
        />
      ) : (
        <>
      <p className="lectura-subtitulo">
        Leyendo en <strong>{NOMBRE_IDIOMA[idioma]}</strong>. Toca una palabra para
        traducirla y guardarla{hayTraduccionFrase && ', o el ⇄ del margen para traducir la frase'}.
      </p>

      <article className="lectura-texto">
        {frases.map((frase, i) => {
          const visible = traducidas[i] && hayTraduccionFrase;
          return (
            <div key={i} className="lectura-frase">
              {hayTraduccionFrase && (
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
        {esLibro && (
          <div className="parte-nav">
            {anterior ? (
              <Link to={rutaParte(anterior)} className="lectura-link">← Parte {anterior.parte}</Link>
            ) : (
              <span />
            )}
            <span className="parte-indicador">{lectura.parte} / {lectura.partes}</span>
            {siguiente ? (
              <Link to={rutaParte(siguiente)} className="lectura-link">Parte {siguiente.parte} →</Link>
            ) : (
              <span />
            )}
          </div>
        )}
        <button className="btn-finalizar" onClick={finalizarLectura}>
          {completada
            ? siguiente
              ? 'Siguiente parte →'
              : '✓ Leída — volver a la biblioteca'
            : siguiente
              ? 'Finalizar y continuar →'
              : 'Finalizar lectura'}
        </button>
      </div>

      {lectura.fuente && <p className="lectura-fuente">{lectura.fuente}</p>}
        </>
      )}

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
