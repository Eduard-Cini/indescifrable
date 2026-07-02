import { useState } from 'react';
import { Link } from 'react-router-dom';
import Landing from './Landing';
import Tablero from './Tablero';
import TableroClave from './TableroClave';
import './App.css';

// Codenames (Indescifrable), uno de los juegos de la Sección 4. Es el mismo
// router por estado de siempre; el hub de juegos vive en /juegos.
function JuegoApp() {
  const [pantallaActiva, setPantallaActiva] = useState('landing');
  const [datosJuego, setDatosJuego] = useState(null);

  const iniciarPartida = (configuracion) => {
    setDatosJuego(configuracion);
    setPantallaActiva(configuracion.destino);
  };

  return (
    <>
      <Link to="/juegos" className="volver-plataforma">← Juegos</Link>

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
          onVolver={() => setPantallaActiva('landing')}
        />
      )}
    </>
  );
}

export default JuegoApp;
