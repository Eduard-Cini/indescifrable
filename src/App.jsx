import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './Home';
import JuegoApp from './JuegoApp';
import Juegos from './secciones/juegos/Juegos';
import JuegosDeLectura from './secciones/juegos/JuegosDeLectura';
import Escalera from './secciones/juegos/Escalera';
import Crucigrama from './secciones/juegos/Crucigrama';
import Wordle from './secciones/juegos/Wordle';
import Sopa from './secciones/juegos/Sopa';
import Biblioteca from './secciones/lectura/Biblioteca';
import Lector from './secciones/lectura/Lector';
import Bolsa from './secciones/lectura/Bolsa';
import Repaso from './secciones/repaso/Repaso';
import Gramatica from './secciones/gramatica/Gramatica';
import TemasDeLectura from './secciones/gramatica/TemasDeLectura';
import Ejercicios from './secciones/gramatica/Ejercicios';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/juegos" element={<Juegos />} />
        <Route path="/juegos/codenames/*" element={<JuegoApp />} />
        <Route path="/juegos/:lectura" element={<JuegosDeLectura />} />
        <Route path="/juegos/:lectura/escalera" element={<Escalera />} />
        <Route path="/juegos/:lectura/crucigrama" element={<Crucigrama />} />
        <Route path="/juegos/:lectura/wordle" element={<Wordle />} />
        <Route path="/juegos/:lectura/sopa" element={<Sopa />} />
        <Route path="/lectura" element={<Biblioteca />} />
        <Route path="/lectura/:idioma/:nivel/:id" element={<Lector />} />
        <Route path="/bolsa" element={<Bolsa />} />
        <Route path="/repaso" element={<Repaso />} />
        <Route path="/gramatica" element={<Gramatica />} />
        <Route path="/gramatica/:lectura" element={<TemasDeLectura />} />
        <Route path="/gramatica/:lectura/:tema" element={<Ejercicios />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
