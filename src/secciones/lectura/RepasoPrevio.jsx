import { useState } from 'react';
import { CALIFICACIONES, aplicarCalificacion } from '../../engine/srs';
import { agregarPalabra, crearEntrada } from '../../engine/bolsa';
import {
  guardarBolsa,
  cargarConocidas,
  guardarConocidas,
} from '../../engine/almacenamiento';
import BotonesCalificacion from '../repaso/BotonesCalificacion';
import '../repaso/repaso.css';

// Repaso previo a una lectura: desfila las palabras del texto que el modelo
// de conocimiento (engine/conocimiento.js) estima que el lector no conoce.
//  - Palabra ya en bolsa → tarjeta SM-2 real (voltear + 4 niveles).
//  - Palabra nueva → ficha de estudio con dos salidas: «Ya la conocía»
//    (no vuelve a proponerse) o «A la bolsa» (el SM-2 la programa).
// Siempre saltable con «Ir al texto →».
function RepasoPrevio({ candidatas, idioma, bolsa, onBolsa, onTerminar }) {
  const [cola, setCola] = useState(candidatas.map((c) => c.id));
  const [volteada, setVolteada] = useState(false);

  const actual = candidatas.find((c) => c.id === cola[0]);
  const entradaBolsa = actual ? bolsa.find((p) => p.id === actual.id) : null;

  const avanzar = (reciclar = false) => {
    const resto = cola.slice(1);
    const nueva = reciclar ? [...resto, cola[0]] : resto;
    setVolteada(false);
    if (nueva.length === 0) onTerminar();
    else setCola(nueva);
  };

  const graduar = (clave) => {
    const q = CALIFICACIONES[clave];
    const nueva = aplicarCalificacion(bolsa, actual.id, q, new Date().toISOString());
    onBolsa(nueva);
    guardarBolsa(nueva);
    avanzar(q < 3); // la fallada se repite al final del previo
  };

  const yaConocia = () => {
    guardarConocidas([...cargarConocidas(), actual.id]);
    avanzar();
  };

  const aBolsa = () => {
    const entrada = crearEntrada({
      lang: idioma,
      surface: actual.surface,
      lemma: actual.lemma,
      traducciones: { es: actual.es },
      origen: 'previo',
    });
    const nueva = agregarPalabra(bolsa, entrada);
    onBolsa(nueva);
    guardarBolsa(nueva);
    avanzar();
  };

  if (!actual) return null;

  const cabeceraTarjeta = (
    <>
      <span className="repaso-idioma">{idioma.toUpperCase()}</span>
      <span className="repaso-anverso">
        {actual.surface}
        {actual.lemma &&
          actual.lemma.toLowerCase() !== actual.surface.toLowerCase() && (
            <span className="repaso-lemma"> ({actual.lemma})</span>
          )}
      </span>
    </>
  );

  return (
    <div className="repaso-previo">
      <p className="lectura-subtitulo">
        Repaso previo: {cola.length} palabra(s) de este texto que quizá no
        conozcas todavía.
      </p>

      {entradaBolsa ? (
        <>
          <button
            type="button"
            className={`repaso-tarjeta${volteada ? ' volteada' : ''}`}
            onClick={() => setVolteada(true)}
          >
            {cabeceraTarjeta}
            {volteada ? (
              <span className="repaso-reverso">{actual.es}</span>
            ) : (
              <span className="repaso-pista">toca para ver la traducción</span>
            )}
          </button>
          {volteada && (
            <BotonesCalificacion srs={entradaBolsa.srs} onCalificar={graduar} />
          )}
        </>
      ) : (
        <>
          <div className="repaso-tarjeta volteada">
            {cabeceraTarjeta}
            <span className="repaso-reverso">{actual.es}</span>
          </div>
          <div className="repaso-botones previo-acciones">
            <button type="button" className="repaso-btn conocia" onClick={yaConocia}>
              Ya la conocía
            </button>
            <button type="button" className="repaso-btn bolsa" onClick={aBolsa}>
              🎒 A la bolsa
            </button>
          </div>
        </>
      )}

      <div className="previo-saltar-zona">
        <button type="button" className="previo-saltar" onClick={onTerminar}>
          Ir al texto →
        </button>
      </div>
    </div>
  );
}

export default RepasoPrevio;
