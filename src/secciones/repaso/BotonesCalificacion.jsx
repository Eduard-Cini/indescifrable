import { CALIFICACIONES, calificar } from '../../engine/srs';

// Los 4 niveles en el orden en que se pintan, con el intervalo que produciría
// cada uno (como Anki). Compartido por /repaso y el repaso previo del Lector.
const NIVELES = [
  { clave: 'otraVez', texto: 'Otra vez' },
  { clave: 'dificil', texto: 'Difícil' },
  { clave: 'bien', texto: 'Bien' },
  { clave: 'facil', texto: 'Fácil' },
];

function etiquetaIntervalo(dias) {
  if (dias === 0) return 'ahora';
  if (dias === 1) return '1 día';
  if (dias < 30) return `${dias} días`;
  return `${Math.round(dias / 30)} mes(es)`;
}

function BotonesCalificacion({ srs, onCalificar }) {
  const ahora = new Date().toISOString();
  return (
    <div className="repaso-botones">
      {NIVELES.map(({ clave, texto }) => (
        <button
          key={clave}
          type="button"
          className={`repaso-btn ${clave}`}
          onClick={() => onCalificar(clave)}
        >
          {texto}
          <span className="repaso-btn-intervalo">
            {etiquetaIntervalo(calificar(srs, CALIFICACIONES[clave], ahora).intervalo)}
          </span>
        </button>
      ))}
    </div>
  );
}

export default BotonesCalificacion;
