"""Traducción automática offline <idioma> -> español con opus-mt (Helsinki-NLP,
modelos Marian) vía transformers. Alternativa sin API a la traducción por
frase con un LLM. Traducción directa (sin pivote), de->es o en->es.

Primera ejecución: descarga el modelo (~300 MB) del idioma pedido.
Uso como módulo:  from mt import traducir_mt   # traducir_mt(list[str], origen="en")
Uso directo:      python mt.py                  # prueba de ejemplo
"""
MODELOS = {
    "de": "Helsinki-NLP/opus-mt-de-es",
    "en": "Helsinki-NLP/opus-mt-en-es",
}
_cache = {}  # origen -> (tok, model)


def _cargar(origen):
    if origen not in _cache:
        from transformers import MarianMTModel, MarianTokenizer
        nombre = MODELOS[origen]
        print(f"Cargando {nombre}...")
        tok = MarianTokenizer.from_pretrained(nombre)
        model = MarianMTModel.from_pretrained(nombre)
        _cache[origen] = (tok, model)
    return _cache[origen]


def traducir_mt(frases, origen="de", tam_lote=16):
    """Traduce una lista de frases <origen>->es, en lotes. Devuelve una lista del
    mismo tamaño (alineación 1:1 garantizada)."""
    tok, model = _cargar(origen)
    salida = []
    for i in range(0, len(frases), tam_lote):
        lote = frases[i : i + tam_lote]
        batch = tok(lote, return_tensors="pt", padding=True, truncation=True, max_length=512)
        gen = model.generate(**batch, max_length=512)
        salida.extend(tok.decode(g, skip_special_tokens=True) for g in gen)
    return salida


if __name__ == "__main__":
    ejemplos = [
        "The Time Traveller (for so it will be convenient to speak of him) "
        "was expounding a recondite matter to us.",
        "It was not a dream.",
    ]
    for s, t in zip(ejemplos, traducir_mt(ejemplos, origen="en")):
        print("EN:", s)
        print("MT:", t, "\n")
