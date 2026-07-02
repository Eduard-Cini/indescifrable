import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './Home';
import JuegoApp from './JuegoApp';
import Biblioteca from './secciones/lectura/Biblioteca';
import Lector from './secciones/lectura/Lector';
import Bolsa from './secciones/lectura/Bolsa';
import Repaso from './secciones/repaso/Repaso';
import Gramatica from './secciones/gramatica/Gramatica';
import Ejercicios from './secciones/gramatica/Ejercicios';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/juegos/*" element={<JuegoApp />} />
        <Route path="/lectura" element={<Biblioteca />} />
        <Route path="/lectura/:idioma/:nivel/:id" element={<Lector />} />
        <Route path="/bolsa" element={<Bolsa />} />
        <Route path="/repaso" element={<Repaso />} />
        <Route path="/gramatica" element={<Gramatica />} />
        <Route path="/gramatica/:tema" element={<Ejercicios />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
