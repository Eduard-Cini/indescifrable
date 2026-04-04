import { useState, useEffect } from 'react';
import { diccionarios } from './data/diccionarios';
import './tablero.css'; 
import './tableroClave.css';

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

function TableroClave({ datos, onVolver }) {
  // 1. GUARDIA DE SEGURIDAD ABSOLUTA
  // Si datos no existe, o le falta la semilla o el vocabulario, detenemos todo aquí.
  if (!datos || !datos.semilla || !datos.vocabulario) {
    return (
      <div className="preparacion-container">
        <h2>Error de Conexión</h2>
        <p>No se recibieron los datos correctamente. Por favor, regresa al inicio e intenta de nuevo.</p>
      </div>
    );
  }

  const [equipoInicial, setEquipoInicial] = useState('');
  const [palabrasTablero, setPalabrasTablero] = useState([]);
  const [mapaColores, setMapaColores] = useState([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    try {
      const semillaLimpia = datos.semilla.toUpperCase().trim();
      if (semillaLimpia.length !== 4) throw new Error("Semilla muy corta");

      const rng = crearGenerador(semillaLimpia);

      let listaCompleta = [];
      if (datos.vocabulario === 'personalizado' && datos.palabras) {
        listaCompleta = datos.palabras.split(/\s*,\s*/).map(p => p.toUpperCase());
      } else {
        listaCompleta = diccionarios[datos.vocabulario] || diccionarios['es_es'];
      }

      const empiezaVerde = rng() > 0.5;
      setEquipoInicial(empiezaVerde ? 'Iluminatis (Verde)' : 'La MASA (Azul)');

      const indices = Array.from({ length: listaCompleta.length }, (_, i) => i);
      const indicesRevueltos = barajar(indices, rng);
      const seleccionadas = indicesRevueltos.slice(0, 25).map(i => ({
        texto: listaCompleta[i],
        indiceOriginal: i 
      }));
      setPalabrasTablero(seleccionadas);

      const colores = [
        ...Array(9).fill(empiezaVerde ? 'verde' : 'azul'),
        ...Array(8).fill(empiezaVerde ? 'azul' : 'verde'),
        ...Array(7).fill('beige'),
        'rojo'
      ];
      setMapaColores(barajar(colores, rng));
      setError(false);

    } catch (e) {
      console.error("Error al generar clave:", e);
      setError(true);
    }
  }, [datos]);

  // 2. LÓGICA DE TRADUCCIÓN PROTEGIDA
  let diccionarioTraduccion = [];
  if (datos.vocabulario !== 'personalizado') {
    const partes = datos.vocabulario.split('_'); 
    const nivel = partes[1] || 'es'; 
    diccionarioTraduccion = diccionarios[`es_${nivel}`] || diccionarios['es_es'];
  }

  if (error) {
    return (
      <div className="preparacion-container">
        <h2>Semilla Inválida</h2>
        <p>La semilla "{datos.semilla}" no pudo ser decodificada.</p>
      </div>
    );
  }

  // 3. RENDERIZADO DEL TABLERO CLAVE
  return (
    <div className="tablero-container">
      <header className="clave-header">
        <h2>Clave de Descifrado</h2>
        
        {/* Agrupamos las estadísticas y el botón en un solo bloque derecho */}
        <div className="header-info-derecha">
          <div className="header-stats">
            <span className="stat-pill">Semilla: {datos.semilla.toUpperCase()}</span>
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
          // Validamos que el color exista antes de renderizar la tarjeta
          if (!colorAsignado) return null; 

          return (
            <div 
              key={index} 
              className={`tarjeta revelada-${colorAsignado}`}
              style={{ cursor: 'default' }}
            >
              <span className="palabra-principal">{palabra.texto}</span>
              {datos.vocabulario !== 'personalizado' && (
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