import { useState } from 'react';
import { Link } from 'react-router-dom';
import Landing from './Landing';
import Tablero from './Tablero';
import TableroClave from './TableroClave';
import './App.css';

// Sección "Juegos": el Codenames (Indescifrable). Es el mismo router por estado
// que antes vivía en App.jsx; ahora App.jsx enruta las secciones de la plataforma.
function JuegoApp() {
  const [pantallaActiva, setPantallaActiva] = useState('landing');
  const [datosJuego, setDatosJuego] = useState(null);

  const iniciarPartida = (configuracion) => {
    setDatosJuego(configuracion);
    setPantallaActiva(configuracion.destino);
  };

  return (
    <>
      <Link to="/" className="volver-plataforma">← Plataforma</Link>

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
