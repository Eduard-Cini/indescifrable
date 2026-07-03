// Selector compacto del idioma de estudio global. Comparte estado vía el
// contexto, así que cambiarlo en cualquier pantalla se refleja en todas.
import { useIdiomaEstudio, IDIOMAS_ESTUDIO } from '../contexto/idiomaEstudio';
import { NOMBRE_IDIOMA } from '../data/lecturas';
import './selectorIdioma.css';

function SelectorIdioma({ className = '' }) {
  const { idioma, setIdioma } = useIdiomaEstudio();
  return (
    <label className={`selector-idioma ${className}`.trim()}>
      <span className="selector-idioma-etiqueta">Idioma</span>
      <select value={idioma} onChange={(e) => setIdioma(e.target.value)}>
        {IDIOMAS_ESTUDIO.map((i) => (
          <option key={i} value={i}>{NOMBRE_IDIOMA[i]}</option>
        ))}
      </select>
    </label>
  );
}

export default SelectorIdioma;
