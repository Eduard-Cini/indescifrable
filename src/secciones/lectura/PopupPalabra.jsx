import './lectura.css';

function PopupPalabra({ seleccion, esEspanol, yaEnBolsa, onAgregar, onCerrar }) {
  const { surface, lemma, traduccionEs } = seleccion;

  return (
    <div className="popup-palabra">
      <button className="popup-cerrar" onClick={onCerrar} aria-label="Cerrar">×</button>

      <div className="popup-cuerpo">
        <span className="popup-surface">{surface}</span>
        {lemma && lemma.toLowerCase() !== surface.toLowerCase() && (
          <span className="popup-lemma">({lemma})</span>
        )}

        {esEspanol ? (
          <p className="popup-traduccion neutral">Estás leyendo en español.</p>
        ) : traduccionEs ? (
          <p className="popup-traduccion">→ {traduccionEs}</p>
        ) : (
          <p className="popup-traduccion sin">Sin traducción en el léxico todavía.</p>
        )}
      </div>

      <button
        className="popup-agregar"
        onClick={onAgregar}
        disabled={yaEnBolsa}
      >
        {yaEnBolsa ? '✓ En la bolsa' : '＋ Añadir a la bolsa'}
      </button>
    </div>
  );
}

export default PopupPalabra;
