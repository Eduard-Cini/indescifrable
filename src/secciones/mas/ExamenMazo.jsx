import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { cargarMazos, guardarMazos } from '../../engine/almacenamiento';
import { CALIFICACIONES } from '../../engine/srs';
import { claveTarjeta, calificarTarjeta } from '../../engine/mazos';
import { TIPOS, sesionDeExamen, comprobar } from '../../engine/examenMazo';
import { Reverso } from './FichaReverso';
import { cargarMazo } from './datos';
import '../lectura/lectura.css';
import '../repaso/repaso.css';
import '../gramatica/gramatica.css';
import './mas.css';

const TOPES = { 10: 10, 20: 20, todas: Infinity };

// Qué se puede practicar. «Todo» mezcla; los demás filtran por tipo de
// pregunta, para poder machacar solo el género o solo el Partizip II.
const MODOS = {
  todo: { etiqueta: 'Todo mezclado', tipos: null },
  genero: { etiqueta: 'Solo el género', tipos: [TIPOS.articulo] },
  partizip: { etiqueta: 'Solo el Partizip II', tipos: [TIPOS.participio] },
  significado: { etiqueta: 'Del español al alemán', tipos: [TIPOS.palabra, TIPOS.infinitivo] },
};

// Preguntas cuyo enunciado ya está en alemán (se pide una forma, no el
// significado): el resto va del español al alemán.
const EN_ALEMAN = new Set([TIPOS.articulo, TIPOS.participio]);

// Lo que se le dice al alumno según QUÉ falló, que es más útil que un ✗ pelado.
const EXPLICACION = {
  articulo: 'El género no es ese.',
  auxiliar: 'El Partizip II está bien; el auxiliar no.',
  forma: 'No es esa la forma.',
  vacia: 'No escribiste nada.',
};

function ExamenMazo() {
  const { mazo: idMazo } = useParams();
  const [mazo, setMazo] = useState(undefined); // undefined = cargando, null = no existe
  const [estados, setEstados] = useState({});
  const [tope, setTope] = useState('10');
  const [modo, setModo] = useState('todo');
  const [cola, setCola] = useState([]);
  const [texto, setTexto] = useState('');
  const [juicio, setJuicio] = useState(null); // null = aún no corregido
  const [aciertos, setAciertos] = useState(0);
  const [fallos, setFallos] = useState(0);
  const campo = useRef(null);

  const nuevaSesion = (m, est, claveTope, claveModo) => {
    if (!m) return [];
    return sesionDeExamen(m, est, new Date().toISOString(), {
      maxNuevas: TOPES[claveTope],
      tipos: MODOS[claveModo].tipos,
      semilla: `${m.id}:${claveModo}`,
    });
  };

  useEffect(() => {
    let vivo = true;
    cargarMazo(idMazo).then((m) => {
      if (!vivo) return;
      const e = cargarMazos();
      setMazo(m);
      setEstados(e);
      setTope('10');
      setModo('todo');
      setCola(nuevaSesion(m, e, '10', 'todo'));
      setTexto('');
      setJuicio(null);
      setAciertos(0);
      setFallos(0);
    });
    return () => {
      vivo = false;
    };
  }, [idMazo]);

  const volver = `/mas/vocabulario/${idMazo}`;
  const cabecera = (
    <header className="lectura-top">
      <Link to={volver} className="lectura-link">← Fichas</Link>
      <h1>{mazo ? `${mazo.titulo} — examen` : 'Examen'}</h1>
      <span />
    </header>
  );

  if (mazo === undefined) return <div className="lectura-container">{cabecera}</div>;
  if (mazo === null) {
    return (
      <div className="lectura-container">
        {cabecera}
        <p className="lectura-subtitulo">
          Este mazo no existe. <Link to="/mas" className="lectura-link">Volver</Link>.
        </p>
      </div>
    );
  }

  const actual = cola[0] ?? null;

  // Corregir: el acierto califica «bien» y el fallo «otra vez», sobre el MISMO
  // estado SM-2 de las fichas (el examen no lleva progreso aparte). La fallada
  // vuelve al final de la cola, como en /repaso.
  const corregir = (evento) => {
    evento.preventDefault();
    if (!actual || juicio) return;
    const r = comprobar(actual, texto);
    const clave = claveTarjeta(actual.tarjeta);
    const nuevos = calificarTarjeta(
      estados,
      clave,
      r.acierto ? CALIFICACIONES.bien : CALIFICACIONES.otraVez,
      new Date().toISOString()
    );
    setEstados(nuevos);
    guardarMazos(nuevos);
    setJuicio(r);
    if (r.acierto) setAciertos(aciertos + 1);
    else setFallos(fallos + 1);
  };

  const siguiente = () => {
    setCola(juicio?.acierto ? cola.slice(1) : [...cola.slice(1), actual]);
    setTexto('');
    setJuicio(null);
    campo.current?.focus();
  };

  const reiniciar = (claveTope, claveModo) => {
    setTope(claveTope);
    setModo(claveModo);
    setCola(nuevaSesion(mazo, estados, claveTope, claveModo));
    setTexto('');
    setJuicio(null);
    setAciertos(0);
    setFallos(0);
  };

  const controles = (
    <div className="mazo-controles">
      <span>{cola.length} pregunta(s)</span>
      <label>
        Practicar{' '}
        <select value={modo} onChange={(e) => reiniciar(tope, e.target.value)}>
          {Object.entries(MODOS).map(([k, m]) => (
            <option key={k} value={k}>{m.etiqueta}</option>
          ))}
        </select>
      </label>
      <label>
        Nuevas{' '}
        <select value={tope} onChange={(e) => reiniciar(e.target.value, modo)}>
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="todas">todas</option>
        </select>
      </label>
    </div>
  );

  if (!actual) {
    const hechas = aciertos + fallos;
    return (
      <div className="lectura-container">
        {cabecera}
        {controles}
        <div className="repaso-fin">
          <p className="repaso-fin-titulo">
            {hechas > 0 ? 'Examen terminado' : 'Nada que preguntar'}
          </p>
          <p className="repaso-fin-stats">
            {hechas > 0
              ? `${aciertos} de ${hechas} a la primera${fallos > 0 ? ` · ${fallos} fallo(s)` : ''}.`
              : 'Con este modo no hay fichas pendientes: prueba otro o vuelve mañana.'}
          </p>
          <Link to={volver} className="gram-boton-sec">Volver a las fichas</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="lectura-container">
      {cabecera}
      {controles}

      <div className="repaso-tarjeta volteada">
        <span className="repaso-idioma">{EN_ALEMAN.has(actual.tipo) ? 'DE' : 'ES → DE'}</span>
        <span className="examen-enunciado">{actual.enunciado}</span>
        <span className="repaso-anverso">{actual.muestra}</span>

        {juicio ? (
          <>
            <p className={`examen-juicio ${juicio.acierto ? 'ok' : 'mal'}`}>
              {juicio.acierto ? '✓ Correcto' : `✗ ${EXPLICACION[juicio.fallo]}`}
            </p>
            {!juicio.acierto && (
              <p className="examen-correccion">
                Escribiste <em>{texto.trim() || '—'}</em> · es <strong>{juicio.esperado}</strong>
              </p>
            )}
            <hr className="examen-separador" />
            <Reverso t={actual.tarjeta} />
          </>
        ) : (
          <form onSubmit={corregir} className="examen-form">
            <input
              ref={campo}
              className="examen-campo"
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder={actual.ayuda}
              autoComplete="off"
              autoCapitalize="off"
              spellCheck="false"
              autoFocus
            />
            <button type="submit" className="gram-boton">Comprobar</button>
          </form>
        )}
      </div>

      {juicio && (
        <button type="button" className="gram-boton examen-siguiente" onClick={siguiente} autoFocus>
          {juicio.acierto ? 'Siguiente' : 'Siguiente (vuelve al final)'}
        </button>
      )}

      <p className="examen-marcador">
        {aciertos} ✓ · {fallos} ✗
      </p>
    </div>
  );
}

export default ExamenMazo;
