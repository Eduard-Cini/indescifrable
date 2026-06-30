import { useState, useEffect } from 'react';
import { diccionarios } from './data/diccionarios';
import {
  generarTablero,
  obtenerListaPalabras,
  parsearSemilla,
} from './engine/board';
import './tablero.css';
import './tableroClave.css';

function TableroClave({ datos, onVolver }) {
  const [equipoInicial, setEquipoInicial] = useState('');
  const [palabrasTablero, setPalabrasTablero] = useState([]);
  const [mapaColores, setMapaColores] = useState([]);
  const [error, setError] = useState(false);

  const semilla = datos?.semilla;
  const palabras = datos?.palabras;

  useEffect(() => {
    if (!semilla) return;
    try {
      const p = parsearSemilla(semilla);
      if (!p) throw new Error('Semilla inválida');

      const lista = obtenerListaPalabras(p.vocabulario, palabras);
      if (lista.length < 25) throw new Error('Vocabulario insuficiente (mínimo 25 palabras)');

      const tablero = generarTablero(p.semillaCorta, lista);
      setEquipoInicial(tablero.equipoInicial);
      setPalabrasTablero(tablero.palabrasTablero);
      setMapaColores(tablero.mapaColores);
      setError(false);
    } catch (e) {
      console.error('Error al generar clave:', e);
      setError(true);
    }
  }, [semilla, palabras]);

  if (!datos || !datos.semilla) {
    return (
      <div className="preparacion-container">
        <h2>Error de Conexión</h2>
        <p>No se recibieron los datos correctamente. Por favor, regresa al inicio e intenta de nuevo.</p>
        <button className="btn-secondary" onClick={onVolver}>Volver al Inicio</button>
      </div>
    );
  }

  const parsed = parsearSemilla(datos.semilla);

  if (error || !parsed) {
    return (
      <div className="preparacion-container">
        <h2>Semilla Inválida</h2>
        <p>La semilla "{datos.semilla}" no pudo ser decodificada.</p>
        <button className="btn-secondary" onClick={onVolver}>Volver al Inicio</button>
      </div>
    );
  }

  // Traducción al español a partir del nivel codificado en la semilla
  let diccionarioTraduccion = [];
  if (parsed.vocabulario !== 'personalizado') {
    const partes = parsed.vocabulario.split('_');
    const nivel = partes[1] || 'es';
    diccionarioTraduccion = diccionarios[`es_${nivel}`] || diccionarios['es_es'];
  }

  return (
    <div className="tablero-container">
      <header className="clave-header">
        <h2>Clave de Descifrado</h2>

        <div className="header-info-derecha">
          <div className="header-stats">
            <span className="stat-pill">Semilla: {parsed.semillaCompleta}</span>
            <span className="stat-pill">Inicia: {equipoInicial}</span>
          </div>

          <button
            className="btn-secondary btn-volver"
            onClick={onVolver}
          >
            Volver al Inicio
          </button>
        </div>
      </header>

      <main className="tablero-grid">
        {palabrasTablero.map((palabra, index) => {
          const colorAsignado = mapaColores[index];
          if (!colorAsignado) return null;

          return (
            <div
              key={index}
              className={`tarjeta revelada-${colorAsignado}`}
              style={{ cursor: 'default' }}
            >
              <span className="palabra-principal">{palabra.texto}</span>
              {parsed.vocabulario !== 'personalizado' && (
                <span className="traduccion">
                  {diccionarioTraduccion[palabra.indiceOriginal]}
                </span>
              )}
            </div>
          );
        })}
      </main>
    </div>
  );
}

export default TableroClave;
