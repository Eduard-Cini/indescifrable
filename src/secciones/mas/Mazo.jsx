import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { cargarMazos, guardarMazos } from '../../engine/almacenamiento';
import { CALIFICACIONES } from '../../engine/srs';
import {
  claveTarjeta,
  sesionDeMazo,
  calificarTarjeta,
  estadoTarjeta,
  formasPasiva,
  textoPlural,
  textoPerfecto,
} from '../../engine/mazos';
import BotonesCalificacion from '../repaso/BotonesCalificacion';
import { cargarMazo } from './datos';
import '../lectura/lectura.css';
import '../repaso/repaso.css';
import '../gramatica/gramatica.css';
import './mas.css';

// Nuevas por sesión (el tope por defecto de Repaso es 10).
const TOPES = { 10: 10, 20: 20, todas: Infinity };

// Qué hay que recordar antes de voltear, según el tipo de ficha.
const PISTAS = {
  sustantivo: '¿artículo, plural y significado?',
  verbo: '¿presente, Präteritum, Partizip II y significado?',
  otro: '¿significado?',
};

// Ids de la cola de una sesión nueva (vencidas + nuevas hasta el tope).
function colaInicial(mazo, estados, claveTope) {
  if (!mazo) return [];
  const ahora = new Date().toISOString();
  return sesionDeMazo(mazo, estados, ahora, { maxNuevas: TOPES[claveTope] }).map((x) => x.id);
}

function textoEstado(srs, ahora) {
  const e = estadoTarjeta(srs, ahora);
  if (e.tipo === 'nueva') return 'nueva';
  if (e.tipo === 'pendiente') return 'para hoy';
  return `en ${e.dias} día(s)`;
}

// La palabra tal como se recuerda: el anverso esconde el artículo.
function textoAnverso(t) {
  if (t.tipo === 'verbo') return t.infinitivo;
  return t.palabra;
}

function Encabezado({ t }) {
  if (t.tipo === 'sustantivo') {
    return (
      <span className="repaso-anverso">
        <span className={`genero ${t.articulo}`}>{t.articulo}</span> {t.palabra}
      </span>
    );
  }
  return <span className="repaso-anverso">{textoAnverso(t)}</span>;
}

// Reverso: todas las formas (la regla de los mazos) + significado y ejemplo.
function Reverso({ t }) {
  const pasiva = formasPasiva(t);
  return (
    <>
      <Encabezado t={t} />
      <table className="mazo-formas">
        <tbody>
          {t.tipo === 'sustantivo' && (
            <tr>
              <th>Plural</th>
              <td>{textoPlural(t)}</td>
            </tr>
          )}
          {t.tipo === 'verbo' && (
            <>
              <tr>
                <th>Präsens</th>
                <td>er/sie/es {t.presente}</td>
              </tr>
              <tr>
                <th>Präteritum</th>
                <td>er/sie/es {t.preterito}</td>
              </tr>
              <tr>
                <th>Partizip II</th>
                <td>
                  <strong>{t.participio}</strong> ({textoPerfecto(t)})
                </td>
              </tr>
            </>
          )}
          {t.tipo === 'otro' && t.categoria && (
            <tr>
              <th>Tipo</th>
              <td>{t.categoria}</td>
            </tr>
          )}
          {t.base && (
            <tr>
              <th>Se forma con</th>
              <td>{t.base}</td>
            </tr>
          )}
        </tbody>
      </table>
      <span className="mazo-significado">{t.es}</span>
      {t.familia && <p className="mazo-familia">Familia: {t.familia}</p>}
      {pasiva && (
        <p className="mazo-pasiva">
          Pasiva: {pasiva.presente} · {pasiva.preterito} · {pasiva.perfecto}
        </p>
      )}
      {t.nota && <p className="mazo-nota">{t.nota}</p>}
      {t.ejemplo && <p className="mazo-ejemplo">{t.ejemplo}</p>}
      {t.ejemploEs && <p className="mazo-ejemplo-es">{t.ejemploEs}</p>}
      {t.fuente && <p className="mazo-fuente">{t.fuente}</p>}
    </>
  );
}

// Lista completa del mazo con el estado de repaso de cada ficha.
function ListaMazo({ mazo, estados, ahora }) {
  const soloVerbos = mazo.tarjetas.every((t) => t.tipo === 'verbo');
  return (
    <details className="mazo-lista">
      <summary>Ver las {mazo.tarjetas.length} fichas del mazo</summary>
      <div className="mas-tabla-envoltura">
        <table className="gram-tabla">
          <thead>
            {soloVerbos ? (
              <tr>
                <th>Infinitiv</th>
                <th>Präsens</th>
                <th>Präteritum</th>
                <th>Partizip II</th>
                <th>Significado</th>
                <th>Repaso</th>
              </tr>
            ) : (
              <tr>
                <th>Palabra</th>
                <th>Plural / tipo</th>
                <th>Significado</th>
                <th>Repaso</th>
              </tr>
            )}
          </thead>
          <tbody>
            {mazo.tarjetas.map((t) => {
              const estado = textoEstado(estados[claveTarjeta(t)], ahora);
              if (soloVerbos) {
                return (
                  <tr key={t.id}>
                    <td>{t.infinitivo}</td>
                    <td>{t.presente}</td>
                    <td>{t.preterito}</td>
                    <td>{textoPerfecto(t)}</td>
                    <td>{t.es}</td>
                    <td className="mazo-estado">{estado}</td>
                  </tr>
                );
              }
              return (
                <tr key={`${t.tipo}:${t.id}`}>
                  <td>
                    {t.tipo === 'sustantivo' && (
                      <span className={`genero ${t.articulo}`}>{t.articulo} </span>
                    )}
                    {textoAnverso(t)}
                  </td>
                  <td>
                    {t.tipo === 'sustantivo'
                      ? textoPlural(t)
                      : t.tipo === 'verbo'
                        ? textoPerfecto(t)
                        : (t.categoria ?? '')}
                  </td>
                  <td>{t.es}</td>
                  <td className="mazo-estado">{estado}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mas-fuente">{mazo.fuente}</p>
    </details>
  );
}

// Sesión de fichas de un mazo con el planificador SM-2 de la Sección 2: la
// palabra sin artículo ni formas en el anverso (hay que recordarlas) y todo
// en el reverso. Falladas se reciclan en la sesión, como en /repaso.
function Mazo() {
  const { mazo: idMazo } = useParams();
  const [mazo, setMazo] = useState(undefined); // undefined = cargando, null = no existe
  const [estados, setEstados] = useState({});
  const [tope, setTope] = useState('10');
  const [cola, setCola] = useState([]);
  const [volteada, setVolteada] = useState(false);
  const [hechas, setHechas] = useState(0);
  const [fallos, setFallos] = useState(0);

  useEffect(() => {
    let vivo = true;
    cargarMazo(idMazo).then((m) => {
      if (!vivo) return;
      const e = cargarMazos();
      setMazo(m);
      setEstados(e);
      setTope('10');
      setCola(colaInicial(m, e, '10'));
      setVolteada(false);
      setHechas(0);
      setFallos(0);
    });
    return () => {
      vivo = false;
    };
  }, [idMazo]);

  const cabecera = (
    <header className="lectura-top">
      <Link to="/mas" className="lectura-link">← Más contenidos</Link>
      <h1>{mazo?.titulo ?? 'Vocabulario'}</h1>
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

  const ahora = new Date().toISOString();
  const porClave = new Map(mazo.tarjetas.map((t) => [claveTarjeta(t), t]));
  const actualId = cola[0];
  const actual = porClave.get(actualId);

  const graduar = (nivel) => {
    const q = CALIFICACIONES[nivel];
    const nuevos = calificarTarjeta(estados, actualId, q, new Date().toISOString());
    setEstados(nuevos);
    guardarMazos(nuevos);
    if (q < 3) {
      setCola([...cola.slice(1), actualId]); // la fallada vuelve al final
      setFallos(fallos + 1);
    } else {
      setCola(cola.slice(1));
      setHechas(hechas + 1);
    }
    setVolteada(false);
  };

  // Cambiar el tope reinicia la sesión con la nueva cantidad de fichas nuevas.
  const cambiarTope = (evento) => {
    setTope(evento.target.value);
    setCola(colaInicial(mazo, estados, evento.target.value));
    setVolteada(false);
    setHechas(0);
    setFallos(0);
  };

  const controles = (
    <div className="mazo-controles">
      <span>{cola.length} ficha(s) en esta sesión</span>
      <label>
        Nuevas por sesión{' '}
        <select value={tope} onChange={cambiarTope}>
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="todas">todas</option>
        </select>
      </label>
    </div>
  );

  const lista = <ListaMazo mazo={mazo} estados={estados} ahora={ahora} />;

  if (!actual) {
    return (
      <div className="lectura-container">
        {cabecera}
        {controles}
        <div className="repaso-fin">
          <p className="repaso-fin-titulo">
            {hechas > 0 ? 'Sesión terminada' : 'Todo al día ✓'}
          </p>
          <p className="repaso-fin-stats">
            {hechas > 0
              ? `${hechas} ficha(s) repasada(s)${fallos > 0 ? ` · ${fallos} fallo(s) por el camino` : ''}.`
              : 'No quedan fichas pendientes: vuelven cuando les toque.'}
          </p>
        </div>
        {lista}
      </div>
    );
  }

  return (
    <div className="lectura-container">
      {cabecera}
      {controles}

      {volteada ? (
        <div className="repaso-tarjeta volteada">
          <span className="repaso-idioma">DE</span>
          {actual.lws && <span className="mazo-lws">Lernwortschatz</span>}
          <Reverso t={actual} />
        </div>
      ) : (
        <button type="button" className="repaso-tarjeta" onClick={() => setVolteada(true)}>
          <span className="repaso-idioma">DE</span>
          {actual.lws && <span className="mazo-lws">Lernwortschatz</span>}
          <span className="repaso-anverso">{textoAnverso(actual)}</span>
          <span className="repaso-pista">
            {PISTAS[actual.tipo]} · toca para ver la respuesta
          </span>
        </button>
      )}

      {volteada && (
        <BotonesCalificacion srs={estados[actualId]} onCalificar={graduar} />
      )}

      {lista}
    </div>
  );
}

export default Mazo;
