import { useState, useEffect } from 'react';
import { diccionarios } from './data/diccionarios';
import './tablero.css'; 

// --- HERRAMIENTAS CRIPTOGRÁFICAS (Fuera del componente para mantener el orden) ---

// 1. El Generador Pseudoaleatorio (LCG - Linear Congruential Generator)
function crearGenerador(semilla) {
  // Convierte el texto "X7B2" en un número base único usando sus valores ASCII
  let hash = 0;
  for (let i = 0; i < semilla.length; i++) {
    hash = semilla.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  // Parámetros matemáticos estándar para LCG
  let m = 0x80000000, a = 1103515245, c = 12345;
  let state = hash ? hash : 1; // El estado inicial es nuestro hash
  
  // Retorna una función que, cada vez que se ejecuta, da el siguiente número de la secuencia (entre 0 y 1)
  return function() {
    state = (a * state + c) % m;
    return state / (m - 1);
  };
}

// 2. El Algoritmo Fisher-Yates para barajar usando nuestro generador en lugar de Math.random()
function barajar(array, funcionRandom) {
  let arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    // Elegimos un índice al azar usando nuestra función matemática predecible
    const j = Math.floor(funcionRandom() * (i + 1));
    // Intercambiamos los elementos
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// --- TU COMPONENTE ---

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
  //Control de Victoria
  const [objetivos, setObjetivos] = useState({ verde: 8, azul: 8 });
  const [ganadorRonda, setGanadorRonda] = useState(null);
  const [modalRoja, setModalRoja] = useState(false);
  const [numeroRonda, setNumeroRonda] = useState(1); // Este será nuestro "gatillo" para re-barajar
  const [ganadorFinal, setGanadorFinal] = useState(null); // Para atrapar cuando alguien gane la partida completa
  
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

useEffect(() => {
    // Generador seguro de 4 caracteres exactos
    const nuevaSemilla = Array.from({length: 4}, () => 
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'[Math.floor(Math.random() * 36)]
    ).join('');
    
    setSemilla(nuevaSemilla);
    const rng = crearGenerador(nuevaSemilla);

    let listaCompleta = [];
    if (datos.vocabulario === 'personalizado' && datos.palabras) {
      listaCompleta = datos.palabras.split(/\s*,\s*/).map(p => p.toUpperCase());
    } else {
      listaCompleta = diccionarios[datos.vocabulario] || diccionarios['es_es'];
    }

    const empiezaVerde = rng() > 0.5;
    setEquipoInicial(empiezaVerde ? 'Iluminatis (Verde)' : 'La MASA (Azul)');

    // El equipo que inicia tiene que adivinar 9, el otro 8
    setObjetivos({
      verde: empiezaVerde ? 9 : 8,
      azul: empiezaVerde ? 8 : 9
    });

    const indices = Array.from({ length: listaCompleta.length }, (_, i) => i);
    const indicesRevueltos = barajar(indices, rng);
    const seleccionadas = indicesRevueltos.slice(0, 25).map(i => ({
      texto: listaCompleta[i],
      indiceOriginal: i 
    }));
    setPalabrasTablero(seleccionadas);

    const colores = [...Array(9).fill(empiezaVerde ? 'verde' : 'azul'), ...Array(8).fill(empiezaVerde ? 'azul' : 'verde'), ...Array(7).fill('beige'), 'rojo'];
    setMapaColores(barajar(colores, rng));
  }, [datos,numeroRonda]);

    const manejarClic = (index) => {
      // Bloquear clics si ya se reveló, si ya hay ganador, o si salió la roja
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
        setRelojActivo(false); // Pausamos el reloj
        setModalRoja(true); // Disparamos la alerta manual
      }
  };
  //TERMINAR RONDA
  const terminarRonda = (ganador) => {
    setRelojActivo(false);
    
    // Calculamos las nuevas rondas antes de guardarlas en el estado
    let nuevasRondasVerde = rondasVerde;
    let nuevasRondasAzul = rondasAzul;

    if (ganador === 'verde') {
      nuevasRondasVerde += 1;
      setRondasVerde(nuevasRondasVerde);
    } else if (ganador === 'azul') {
      nuevasRondasAzul += 1;
      setRondasAzul(nuevasRondasAzul);
    }

    // Evaluamos si alguien ya alcanzó el límite de rondas
    if (nuevasRondasVerde >= datos.rondas) {
      setGanadorFinal('verde');
    } else if (nuevasRondasAzul >= datos.rondas) {
      setGanadorFinal('azul');
    } else {
      setGanadorRonda(ganador); // Solo mostramos el modal de ronda si el juego no ha terminado
    }
  };

  //PREPARAR SIGUIENTE RONDA
  const prepararSiguienteRonda = () => {
    setJuegoListo(false); // Nos devuelve a la pantalla inicial para generar nueva semilla
    setGanadorRonda(null);
    setModalRoja(false);
    setReveladas({});
    setPuntosVerde(0);
    setPuntosAzul(0);
    setTiempo(60);
    // Cambiamos 'datos' creando un clon falso para forzar al useEffect a correr de nuevo
    // (Opcional: Si pasas una nueva prop desde el padre, ignora esto, pero esto asegura la recarga)
    setNumeroRonda(prev => prev + 1);
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
          {/* El reloj solo parpadea (clase 'critico') si está entre 1 y 10 segundos */}
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

      {/* MODAL: TARJETA ASESINA */}
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

      {/* MODAL: FIN DE RONDA NORMAL */}
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

      {/* MODAL: FIN DEL JUEGO (VICTORIA TOTAL) */}
      {ganadorFinal && (
        <div className="modal-overlay">
          <div className={`modal-content ${ganadorFinal}`}>
            <h3>¡TRANSMISIÓN COMPLETADA!</h3>
            <p>El ganador definitivo de la partida es:</p>
            <h2>{ganadorFinal === 'verde' ? 'ILUMINATIS' : 'LA MASA'}</h2>
            <button 
              className="btn-primary" 
              style={{ marginTop: '20px' }}
              onClick={onVolver} // Manera rápida de reiniciar toda la App
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