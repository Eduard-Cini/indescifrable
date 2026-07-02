// engine/tokenizar.js
// Separa una frase en palabras (clicables) y separadores (puntuación/espacios).
// Compartido por el Lector (render) y el modelo de conocimiento (conteo de
// candidatas), para que ambos vean exactamente las mismas palabras.
export function tokenizar(frase) {
  const tokens = [];
  const re = /\p{L}[\p{L}\p{M}'’-]*/gu;
  let ultimo = 0;
  let m;
  while ((m = re.exec(frase)) !== null) {
    if (m.index > ultimo) tokens.push({ tipo: 'sep', valor: frase.slice(ultimo, m.index) });
    tokens.push({ tipo: 'palabra', valor: m[0] });
    ultimo = m.index + m[0].length;
  }
  if (ultimo < frase.length) tokens.push({ tipo: 'sep', valor: frase.slice(ultimo) });
  return tokens;
}
