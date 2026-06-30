import { useState, useEffect } from 'react';
import { diccionarios } from './data/diccionarios';
import {
  componerSemilla,
  generarSemillaAleatoria,
  generarTablero,
  obtenerListaPalabras,
} from './engine/board';
import './tablero.css';

function Tablero({ datos, onVolver }) {
  const [juegoListo, setJuegoListo] = useState(false);
  const [semilla, setSemilla] = useState('');
  const [equipoInicial, setEquipoInicial] = useState('');
  const [palabrasTablero, setPalabrasTablero] = useState([]);
  const [mapaColores, setMapaColores] = useState([]);

  // Estados de juego
  const [puntosVerde, setPuntosVerde] = useState(0);
  const [puntosAzul, setPuntosAzul] = useState(0);
  const [rondasVerde, setRondasVerde] = useState(0);
  const [rondasAzul, setRondasAzul] = useState(0);
  const [reveladas, setReveladas] = useState({});
  // Control de victoria
  const [objetivos, setObjetivos] = useState({ verde: 8, azul: 8 });
  const [ganadorRonda, setGanadorRonda] = useState(null);
  const [modalRoja, setModalRoja] = useState(false);
  const [ganadorFinal, setGanadorFinal] = useState(null);

  // Cronómetro
  const [tiempo, setTiempo] = useState(60);
  const [relojActivo, setRelojActivo] = useState(false);

  useEffect(() => {
    let intervalo;
    if (relojActivo && tiempo > 0) {
      intervalo = setInterval(() => setTiempo(t => t - 1), 1000);
    } else if (tiempo === 0) {
      setRelojActivo(false);
    }
    return () => clearInterval(intervalo);
  }, [relojActivo, tiempo]);

  const iniciarPartida = () => {
    const semillaCorta = generarSemillaAleatoria(4);
    const semillaCompleta = componerSemilla(datos.vocabulario, semillaCorta);
    const lista = obtenerListaPalabras(datos.vocabulario, datos.palabras);
    const tablero = generarTablero(semillaCorta, lista);

    setSemilla(semillaCompleta);
    setEquipoInicial(tablero.equipoInicial);
    setObjetivos({
      verde: tablero.empiezaVerde ? 9 : 8,
      azul: tablero.empiezaVerde ? 8 : 9,
    });
    setPalabrasTablero(tablero.palabrasTablero);
    setMapaColores(tablero.mapaColores);
  };

  useEffect(() => {
    iniciarPartida();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const manejarClic = (index) => {
    if (reveladas[index] || ganadorRonda || modalRoja) return;

    const colorOculto = mapaColores[index];
    setReveladas(prev => ({ ...prev, [index]: colorOculto }));

    if (colorOculto === 'verde') {
      const nuevosPuntos = puntosVerde + 1;
      setPuntosVerde(nuevosPuntos);
      if (nuevosPuntos === objetivos.verde) terminarRonda('verde');
    } else if (colorOculto === 'azul') {
      const nuevosPuntos = puntosAzul + 1;
      setPuntosAzul(nuevosPuntos);
      if (nuevosPuntos === objetivos.azul) terminarRonda('azul');
    } else if (colorOculto === 'rojo') {
      setRelojActivo(false);
      setModalRoja(true);
    }
  };

  const terminarRonda = (ganador) => {
    setRelojActivo(false);

    let nuevasRondasVerde = rondasVerde;
    let nuevasRondasAzul = rondasAzul;

    if (ganador === 'verde') {
      nuevasRondasVerde += 1;
      setRondasVerde(nuevasRondasVerde);
    } else if (ganador === 'azul') {
      nuevasRondasAzul += 1;
      setRondasAzul(nuevasRondasAzul);
    }

    if (nuevasRondasVerde >= datos.rondas) {
      setGanadorFinal('verde');
    } else if (nuevasRondasAzul >= datos.rondas) {
      setGanadorFinal('azul');
    } else {
      setGanadorRonda(ganador);
    }
  };

  const prepararSiguienteRonda = () => {
    setJuegoListo(false);
    setGanadorRonda(null);
    setModalRoja(false);
    setReveladas({});
    setPuntosVerde(0);
    setPuntosAzul(0);
    setTiempo(60);
    iniciarPartida();
  };

  // --- RENDERIZADO ---

  if (!juegoListo) {
    return (
      <div className="preparacion-container">
        <h2>Preparando la conexión...</h2>
        <div className="info-preparacion">
          <p>Código: <strong>{semilla}</strong></p>
          <p>Inicia: <strong>{equipoInicial}</strong></p>
        </div>
        <button className="btn-primary-tablero" onClick={() => setJuegoListo(true)}>
          INICIAR JUEGO
        </button>
      </div>
    );
  }

  // Lógica de traducción para el hover
  const partes = datos.vocabulario.split('_');
  const nivel = partes[1] || 'es';
  const diccionarioTraduccion = diccionarios[`es_${nivel}`] || diccionarios['es_es'];

  return (
    <div className="tablero-container">
      <header className="tablero-header">
        <div className="header-principal">
          <h2>Terminal de Descifrado</h2>
          <div className="header-stats">
            <span className="stat-pill">Código: {semilla}</span>
            <span className="stat-pill">Inicia: {equipoInicial}</span>
            <span className="stat-pill verde">I: {puntosVerde} (R: {rondasVerde})</span>
            <span className="stat-pill azul">M: {puntosAzul} (R: {rondasAzul})</span>
          </div>
        </div>
      </header>

      <main className="tablero-grid">
        {palabrasTablero.map((palabra, index) => {
          const color = reveladas[index];
          return (
            <div key={index} className={`tarjeta ${color ? `revelada-${color}` : ''}`} onClick={() => manejarClic(index)}>
              <span className="palabra-principal">{palabra.texto}</span>
              {datos.vocabulario !== 'personalizado' && !color && (
                <span className="traduccion">{diccionarioTraduccion[palabra.indiceOriginal]}</span>
              )}
            </div>
          );
        })}
      </main>

      <footer className="tablero-footer">
        <div className="cronometro-container">
          <div className={`tiempo-display ${tiempo <= 10 && tiempo > 0 ? 'critico' : ''}`}>
            00:{tiempo.toString().padStart(2, '0')}
          </div>
          <div className="controles-reloj">
            <button className="btn-reloj" onClick={() => { setTiempo(60); setRelojActivo(true); }}>
              INICIAR
            </button>
          </div>
        </div>
        {tiempo === 0 && <div className="alerta-final">¡TIEMPO AGOTADO!</div>}
      </footer>

      {modalRoja && (
        <div className="modal-overlay">
          <div className="modal-content roja">
            <h3>¡TARJETA ASESINA REVELADA!</h3>
            <p>¿Qué equipo gana esta ronda?</p>
            <div className="modal-botones">
              <button className="btn-stat verde" onClick={() => { setModalRoja(false); terminarRonda('verde'); }}>
                Ganó Iluminatis
              </button>
              <button className="btn-stat azul" onClick={() => { setModalRoja(false); terminarRonda('azul'); }}>
                Ganó La MASA
              </button>
            </div>
          </div>
        </div>
      )}

      {ganadorRonda && (
        <div className="modal-overlay">
          <div className={`modal-content ${ganadorRonda}`}>
            <h3>¡RONDA TERMINADA!</h3>
            <p>Victoria para: <strong>{ganadorRonda === 'verde' ? 'Iluminatis' : 'La MASA'}</strong></p>
            <button className="btn-primary" onClick={prepararSiguienteRonda}>
              Siguiente Ronda
            </button>
          </div>
        </div>
      )}

      {ganadorFinal && (
        <div className="modal-overlay">
          <div className={`modal-content ${ganadorFinal}`}>
            <h3>¡TRANSMISIÓN COMPLETADA!</h3>
            <p>El ganador definitivo de la partida es:</p>
            <h2>{ganadorFinal === 'verde' ? 'ILUMINATIS' : 'LA MASA'}</h2>
            <button
              className="btn-primary"
              style={{ marginTop: '20px' }}
              onClick={onVolver}
            >
              Volver a la Configuración Inicial
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

export default Tablero;
