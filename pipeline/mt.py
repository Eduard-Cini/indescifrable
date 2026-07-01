"""Traducción automática offline alemán -> español con opus-mt (Helsinki-NLP,
modelos Marian) vía transformers. Alternativa sin API a la traducción por
frase con un LLM. Traducción directa de->es (sin pivote por inglés).

Primera ejecución: descarga el modelo Helsinki-NLP/opus-mt-de-es (~300 MB).
Uso como módulo:  from mt import traducir_mt   # traducir_mt(list[str]) -> list[str]
Uso directo:      python mt.py                  # prueba de ejemplo
"""
MODELO = "Helsinki-NLP/opus-mt-de-es"
_tok = None
_model = None


def _cargar():
    global _tok, _model
    if _model is None:
        from transformers import MarianMTModel, MarianTokenizer
        print(f"Cargando {MODELO}...")
        _tok = MarianTokenizer.from_pretrained(MODELO)
        _model = MarianMTModel.from_pretrained(MODELO)
    return _tok, _model


def traducir_mt(frases, tam_lote=16):
    """Traduce una lista de frases de->es, en lotes. Devuelve una lista del
    mismo tamaño (alineación 1:1 garantizada)."""
    tok, model = _cargar()
    salida = []
    for i in range(0, len(frases), tam_lote):
        lote = frases[i : i + tam_lote]
        batch = tok(lote, return_tensors="pt", padding=True, truncation=True, max_length=512)
        gen = model.generate(**batch, max_length=512)
        salida.extend(tok.decode(g, skip_special_tokens=True) for g in gen)
    return salida


if __name__ == "__main__":
    ejemplos = [
        "Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, "
        "fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt.",
        "Es war kein Traum.",
    ]
    for s, t in zip(ejemplos, traducir_mt(ejemplos)):
        print("DE:", s)
        print("MT:", t, "\n")
