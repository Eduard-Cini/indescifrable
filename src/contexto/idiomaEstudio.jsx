// Contexto del «idioma de estudio» global: una sola elección (persistida en
// localStorage) que gobierna de forma coherente Repaso, Bolsa y la Biblioteca.
// Los idiomas de estudio son los extranjeros que se aprenden (de/en); el
// español es la lengua de traducción, no un objetivo de estudio.
import { createContext, useContext, useState, useCallback } from 'react';
import {
  cargarIdiomaEstudio,
  guardarIdiomaEstudio,
} from '../engine/almacenamiento';

// El español es también lengua de estudio (para nativos que amplían vocabulario
// con libros difíciles), no solo la lengua de traducción de de/en.
export const IDIOMAS_ESTUDIO = ['de', 'en', 'es'];

const Contexto = createContext(null);

export function IdiomaEstudioProvider({ children }) {
  const [idioma, setIdiomaState] = useState(() => cargarIdiomaEstudio());

  const setIdioma = useCallback((nuevo) => {
    setIdiomaState(nuevo);
    guardarIdiomaEstudio(nuevo);
  }, []);

  return (
    <Contexto.Provider value={{ idioma, setIdioma }}>
      {children}
    </Contexto.Provider>
  );
}

export function useIdiomaEstudio() {
  const valor = useContext(Contexto);
  if (!valor) {
    throw new Error('useIdiomaEstudio debe usarse dentro de IdiomaEstudioProvider');
  }
  return valor;
}
