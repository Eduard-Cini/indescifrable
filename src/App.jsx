import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './Home';
import JuegoApp from './JuegoApp';
import Juegos from './secciones/juegos/Juegos';
import LecturasDeJuego from './secciones/juegos/LecturasDeJuego';
import Escalera from './secciones/juegos/Escalera';
import Crucigrama from './secciones/juegos/Crucigrama';
import Wordle from './secciones/juegos/Wordle';
import Sopa from './secciones/juegos/Sopa';
import Sudoku from './secciones/juegos/Sudoku';
import Biblioteca from './secciones/lectura/Biblioteca';
import Lector from './secciones/lectura/Lector';
import Bolsa from './secciones/lectura/Bolsa';
import Repaso from './secciones/repaso/Repaso';
import Gramatica from './secciones/gramatica/Gramatica';
import TemasDeLectura from './secciones/gramatica/TemasDeLectura';
import Ejercicios from './secciones/gramatica/Ejercicios';
import { IdiomaEstudioProvider } from './contexto/idiomaEstudio';
import './App.css';

function App() {
  return (
    <IdiomaEstudioProvider>
      <BrowserRouter>
        <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/juegos" element={<Juegos />} />
        <Route path="/juegos/codenames/*" element={<JuegoApp />} />
        <Route path="/juegos/escalera" element={<LecturasDeJuego juego="escalera" />} />
        <Route path="/juegos/escalera/:lectura" element={<Escalera />} />
        <Route path="/juegos/crucigrama" element={<LecturasDeJuego juego="crucigrama" />} />
        <Route path="/juegos/crucigrama/:lectura" element={<Crucigrama />} />
        <Route path="/juegos/wordle" element={<LecturasDeJuego juego="wordle" />} />
        <Route path="/juegos/wordle/:lectura" element={<Wordle />} />
        <Route path="/juegos/sopa" element={<LecturasDeJuego juego="sopa" />} />
        <Route path="/juegos/sopa/:lectura" element={<Sopa />} />
        <Route path="/juegos/sudoku" element={<LecturasDeJuego juego="sudoku" />} />
        <Route path="/juegos/sudoku/:lectura" element={<Sudoku />} />
        <Route path="/lectura" element={<Biblioteca />} />
        <Route path="/lectura/:idioma/:nivel/:id" element={<Lector />} />
        <Route path="/bolsa" element={<Bolsa />} />
        <Route path="/repaso" element={<Repaso />} />
        <Route path="/gramatica" element={<Gramatica />} />
        <Route path="/gramatica/:lectura" element={<TemasDeLectura />} />
        <Route path="/gramatica/:lectura/:tema" element={<Ejercicios />} />
        </Routes>
      </BrowserRouter>
    </IdiomaEstudioProvider>
  );
}

export default App;
