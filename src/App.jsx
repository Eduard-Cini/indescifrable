import { useState } from 'react';
import Landing from './Landing';
import Tablero from './Tablero';
import TableroClave from './TableroClave';
import './App.css';

function App() {
  // 1. Estado para controlar la pantalla activa ('landing' por defecto)
  const [pantallaActiva, setPantallaActiva] = useState('landing');
  
  // 2. Estado para almacenar la configuración de la partida
  const [datosJuego, setDatosJuego] = useState(null);

  // 3. Función que la Landing ejecutará al presionar "Crear" o "Acceder"
  const iniciarPartida = (configuracion) => {
    setDatosJuego(configuracion); // Guardamos la info (rondas, semilla, etc.)
    setPantallaActiva(configuracion.destino); // Cambiamos la vista
  };

  // 4. Renderizado condicional basado en el estado
return (
    <>
      {pantallaActiva === 'landing' && (
        <Landing onIniciarPartida={iniciarPartida} />
      )}
      
      {pantallaActiva === 'tablero_principal' && (
        <Tablero 
          datos={datosJuego} 
          onVolver={() => setPantallaActiva('landing')} 
        />
      )}

      {pantallaActiva === 'tablero_clave' && (
        <TableroClave 
          datos={datosJuego} 
          onVolver={() => setPantallaActiva('landing')} // <--- Agrega esta línea
        />
      )}
    </>
  );
}

export default App;