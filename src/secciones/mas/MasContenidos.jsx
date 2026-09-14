import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { cargarMazos, cargarMasCompletados } from '../../engine/almacenamiento';
import { resumenDeMazo } from '../../engine/mazos';
import { claveTanda } from '../../engine/ejercicios';
import { cargarIndice, cargarMazo, cargarLeccion, cargarEjercicios } from './datos';
import '../lectura/lectura.css';
import '../gramatica/gramatica.css';
import './mas.css';

// Todo lo que resume la portada: por capítulo (indice.json), sus temas con
// mazo, lección y ejercicios, y sus mazos de vocabulario y verbos.
async function cargarPortada() {
  const indice = await cargarIndice();
  const capitulos = await Promise.all(
    indice.capitulos.map(async (cap) => ({
      ...cap,
      temas: await Promise.all(
        cap.temas.map(async (id) => {
          const [mazo, leccion, banco] = await Promise.all([
            cargarMazo(id),
            cargarLeccion(id),
            cargarEjercicios(id),
          ]);
          return { id, mazo, leccion, banco };
        })
      ),
      mazosCapitulo: await Promise.all(
        cap.mazos.map(async (id) => ({ id, mazo: await cargarMazo(id) }))
      ),
    }))
  );
  return { ...indice, capitulos };
}

// Portada de «Más contenidos»: material de alemán del curso (Netzwerk neu B1)
// en tres bloques — vocabulario por tema, gramática (lección + ejercicios) y
// vocabulario/verbos de cada capítulo —, agrupados por capítulo.
function MasContenidos() {
  const [portada, setPortada] = useState(null);
  const [estados, setEstados] = useState({});
  const [hechas, setHechas] = useState([]);

  useEffect(() => {
    let vivo = true;
    cargarPortada().then((p) => {
      if (!vivo) return;
      setPortada(p);
      setEstados(cargarMazos());
      setHechas(cargarMasCompletados());
    });
    return () => {
      vivo = false;
    };
  }, []);

  const ahora = new Date().toISOString();

  const tarjetaMazo = (id, mazo) => {
    if (!mazo) return null;
    const r = resumenDeMazo(mazo, estados, ahora);
    return (
      <Link key={id} to={`/mas/vocabulario/${id}`} className="gram-tema-card">
        <h2>{mazo.titulo}</h2>
        <p>{mazo.descripcion}</p>
        <span className="gram-tema-count">
          {mazo.tarjetas.length} fichas · {r.nuevas} nuevas · {r.vencidas} para repasar hoy
        </span>
      </Link>
    );
  };

  const tarjetaGramatica = (t) => {
    if (!t.leccion) return null;
    const tandas = t.banco?.tandas ?? [];
    const hechasTema = tandas.filter((x) => hechas.includes(claveTanda(t.id, x.id))).length;
    return (
      <div key={t.id} className="gram-tema-card">
        <Link to={`/mas/gramatica/${t.id}`} className="mas-card-link">
          <h2>{t.leccion.titulo}</h2>
          <p>{t.leccion.descripcion}</p>
        </Link>
        {tandas.length > 0 && (
          <Link to={`/mas/gramatica/${t.id}/ejercicios`} className="mas-subenlace">
            Ejercicios · {hechasTema}/{tandas.length} tandas
            {hechasTema === tandas.length && <span className="gram-palomita"> ✓</span>}
          </Link>
        )}
      </div>
    );
  };

  const porCapitulo = (contenido) =>
    portada?.capitulos.map((cap) => (
      <div key={cap.numero} className="mas-capitulo">
        <h3>
          Capítulo {cap.numero} · {cap.titulo}
        </h3>
        <div className="gram-temas">{contenido(cap)}</div>
      </div>
    ));

  return (
    <div className="lectura-container">
      <header className="lectura-top">
        <Link to="/" className="lectura-link">← Plataforma</Link>
        <h1>Más contenidos</h1>
        <span />
      </header>
      <p className="lectura-subtitulo">
        Alemán · {portada?.libro ?? 'Netzwerk neu B1'}, capítulos 9 y 10. Ordenado por
        vocabulario y por gramática; al final, el vocabulario y los verbos de cada capítulo.
      </p>

      <section className="mas-bloque">
        <h2 className="mas-bloque-titulo">Vocabulario por tema</h2>
        <p className="mas-bloque-sub">
          Fichas con repetición espaciada (el mismo modelo SM-2 de Repaso). Si una
          palabra está en varios mazos, su progreso se comparte.
        </p>
        {porCapitulo((cap) => cap.temas.map((t) => tarjetaMazo(t.id, t.mazo)))}
      </section>

      <section className="mas-bloque">
        <h2 className="mas-bloque-titulo">Gramática</h2>
        <p className="mas-bloque-sub">
          Lección (con lo que explica el libro) y una subsección de ejercicios.
        </p>
        {porCapitulo((cap) => cap.temas.map(tarjetaGramatica))}
      </section>

      <section className="mas-bloque">
        <h2 className="mas-bloque-titulo">Vocabulario y verbos del capítulo</h2>
        <p className="mas-bloque-sub">
          El Lernwortschatz completo de cada capítulo y todos sus verbos, con sus formas.
        </p>
        {porCapitulo((cap) => cap.mazosCapitulo.map((m) => tarjetaMazo(m.id, m.mazo)))}
      </section>
    </div>
  );
}

export default MasContenidos;
