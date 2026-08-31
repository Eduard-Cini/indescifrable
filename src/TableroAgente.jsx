import { useState, useEffect } from 'react';
import {
  generarTablero,
  obtenerListaPalabras,
  parsearSemilla,
} from './engine/board';
import './tablero.css';

// Vista de AGENTE: las mismas 25 palabras del tablero principal, en el mismo
// orden, reconstruidas de forma determinista a partir de la semilla. Pensada
// para jugar en móviles: cada receptor de pistas abre el tablero en su propio
// teléfono en vez de amontonarse alrededor de una sola pantalla.
//
// Es de SOLO LECTURA a propósito: sin backend no hay forma de sincronizar los
// descubrimientos entre dispositivos, así que el tablero compartido sigue
// siendo la fuente de verdad. Y, por supuesto, no muestra los colores.
function TableroAgente({ datos, onVolver }) {
  const [palabrasTablero, setPalabrasTablero] = useState([]);
  const [equipoInicial, setEquipoInicial] = useState('');
  const [error, setError] = useState(null);

  const semilla = datos?.semilla;
  const palabras = datos?.palabras;

  useEffect(() => {
    if (!semilla) return;
    try {
      const p = parsearSemilla(semilla);
      if (!p) throw new Error('La semilla no pudo ser decodificada.');
      const lista = obtenerListaPalabras(p.vocabulario, palabras);
      if (lista.length < 25) {
        throw new Error('Vocabulario insuficiente (mínimo 25 palabras).');
      }
      const tablero = generarTablero(p.semillaCorta, lista);
      setPalabrasTablero(tablero.palabrasTablero);
      setEquipoInicial(tablero.equipoInicial);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }, [semilla, palabras]);

  if (!semilla || error) {
    return (
      <div className="preparacion-container">
        <h2>No se pudo abrir el tablero</h2>
        <p>{error ?? 'No se recibió la semilla de la partida.'}</p>
        <button className="btn-secondary" onClick={onVolver}>Volver al Inicio</button>
      </div>
    );
  }

  return (
    <div className="tablero-container">
      <header className="clave-header">
        <h2>Tablero (agentes)</h2>
        <div className="header-info-derecha">
          <div className="header-stats">
            <span className="stat-pill">Semilla: {parsearSemilla(semilla)?.semillaCompleta}</span>
            <span className="stat-pill">Inicia: {equipoInicial}</span>
          </div>
          <button className="btn-secondary btn-volver" onClick={onVolver}>
            Volver al Inicio
          </button>
        </div>
      </header>

      <p className="agente-nota">
        Vista para seguir la partida desde tu móvil: son las mismas palabras, en
        el mismo orden. Las tarjetas se descubren en el tablero principal.
      </p>

      <main className="tablero-grid">
        {palabrasTablero.map((palabra, index) => (
          <div key={index} className="tarjeta" style={{ cursor: 'default' }}>
            <span className="palabra-principal">{palabra.texto}</span>
          </div>
        ))}
      </main>
    </div>
  );
}

export default TableroAgente;
