import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  NIVELES,
  IDIOMAS,
  NOMBRE_IDIOMA,
  NOMBRE_NIVEL,
  lecturasDisponibles,
  agruparPorLibro,
} from '../../data/lecturas';
import { cargarBolsa, cargarProgreso } from '../../engine/almacenamiento';
import { contar } from '../../engine/bolsa';
import { estaCompletada, contarCompletadas } from '../../engine/progreso';
import { useIdiomaEstudio, IDIOMAS_ESTUDIO } from '../../contexto/idiomaEstudio';
import './lectura.css';

function Biblioteca() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const { idioma: idiomaGlobal, setIdioma: setIdiomaGlobal } = useIdiomaEstudio();

  // El idioma vive en la URL (para conservarse al volver de una lectura); si no
  // hay parámetro, se hereda del idioma de estudio global.
  const idioma = IDIOMAS.includes(params.get('idioma')) ? params.get('idioma') : idiomaGlobal;
  const nivel = NIVELES.includes(params.get('nivel')) ? params.get('nivel') : 'principiante';

  const setFiltro = (clave, valor) => {
    const next = new URLSearchParams(params);
    next.set(clave, valor);
    setParams(next, { replace: true });
    // Cambiar el idioma aquí actualiza la elección global (salvo español, que
    // es solo lengua de traducción, no un objetivo de estudio).
    if (clave === 'idioma' && IDIOMAS_ESTUDIO.includes(valor)) {
      setIdiomaGlobal(valor);
    }
  };

  const lecturas = lecturasDisponibles(nivel, idioma);
  const entradas = agruparPorLibro(lecturas);
  const completadas = cargarProgreso();
  const totalBolsa = contar(cargarBolsa());

  const entradaCompleta = (e) =>
    e.tipo === 'libro'
      ? e.partes.every((p) => estaCompletada(completadas, p.id))
      : estaCompletada(completadas, e.lectura.id);
  const hechas = entradas.filter(entradaCompleta).length;

  const irALectura = (id) => navigate(`/lectura/${idioma}/${nivel}/${id}`);

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/" className="lectura-link">← Plataforma</Link>
        <h1>Biblioteca</h1>
        <Link to="/bolsa" className="lectura-link bolsa-badge">🎒 Bolsa: {totalBolsa}</Link>
      </header>

      <div className="biblioteca-filtros">
        <label>
          Idioma de estudio:
          <select value={idioma} onChange={(e) => setFiltro('idioma', e.target.value)}>
            {IDIOMAS.map((i) => (
              <option key={i} value={i}>{NOMBRE_IDIOMA[i]}</option>
            ))}
          </select>
        </label>

        <label>
          Nivel:
          <select value={nivel} onChange={(e) => setFiltro('nivel', e.target.value)}>
            {NIVELES.map((n) => (
              <option key={n} value={n}>{NOMBRE_NIVEL[n]}</option>
            ))}
          </select>
        </label>
      </div>

      {entradas.length > 0 && (
        <p className="biblioteca-progreso">
          Completadas: {hechas} de {entradas.length} en este nivel.
        </p>
      )}

      <main className="biblioteca-lista">
        {entradas.length === 0 && (
          <p className="biblioteca-vacia">
            No hay lecturas de nivel {NOMBRE_NIVEL[nivel].toLowerCase()} en {NOMBRE_IDIOMA[idioma]}.
          </p>
        )}

        {entradas.map((e) => {
          if (e.tipo === 'lectura') {
            const l = e.lectura;
            const hecha = estaCompletada(completadas, l.id);
            return (
              <button
                key={l.id}
                className={'lectura-card' + (hecha ? ' completada' : '')}
                onClick={() => irALectura(l.id)}
              >
                <span className="lectura-card-titulo">
                  {hecha && <span className="check-completada">✓</span>}
                  {l.titulo[idioma]}
                </span>
                <span className="lectura-card-meta">
                  {NOMBRE_IDIOMA[idioma]} · {NOMBRE_NIVEL[l.nivel]}
                  {l.autor && ` · ${l.autor}`}
                </span>
              </button>
            );
          }

          // entrada de tipo libro: colapsa sus partes
          const leidas = contarCompletadas(completadas, e.partes.map((p) => p.id));
          const total = e.partes.length;
          const completo = leidas === total;
          const continuar = e.partes.find((p) => !estaCompletada(completadas, p.id)) ?? e.partes[0];
          return (
            <button
              key={`libro-${e.id}`}
              className={'lectura-card libro' + (completo ? ' completada' : '')}
              onClick={() => irALectura(continuar.id)}
            >
              <span className="lectura-card-titulo">
                {completo && <span className="check-completada">✓</span>}
                📖 {e.titulo[idioma]}
              </span>
              <span className="lectura-card-meta">
                {NOMBRE_IDIOMA[idioma]} · {NOMBRE_NIVEL[e.nivel]}
                {e.autor && ` · ${e.autor}`} · {leidas}/{total} partes
              </span>
            </button>
          );
        })}
      </main>
    </div>
  );
}

export default Biblioteca;
