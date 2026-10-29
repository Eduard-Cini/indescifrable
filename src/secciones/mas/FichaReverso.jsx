import { formasPasiva, textoAnverso, textoPlural, textoPerfecto } from '../../engine/mazos';

// La cara de atrás de una ficha de «Más contenidos»: todas las formas (la
// regla de los mazos), el significado y el ejemplo. La usan el mazo (al
// voltear) y el examen escrito (al corregir), que enseñan lo mismo.

/** El titular de la ficha: el sustantivo con su artículo en color. */
export function Encabezado({ t }) {
  if (t.tipo === 'sustantivo') {
    return (
      <span className="repaso-anverso">
        <span className={`genero ${t.articulo}`}>{t.articulo}</span> {t.palabra}
      </span>
    );
  }
  return <span className="repaso-anverso">{textoAnverso(t)}</span>;
}

export function Reverso({ t }) {
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
          {t.preposicion && (
            <tr>
              <th>Preposición</th>
              <td className="mazo-preposicion">{t.preposicion}</td>
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
