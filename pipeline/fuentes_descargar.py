"""Descarga un texto de Project Gutenberg a fuentes/ e imprime el inicio para
inspeccionar idioma/estructura. Uso: python fuentes_descargar.py <id> <nombre>"""
import sys
import os
import requests

def descargar(ebook_id, nombre):
    os.makedirs("fuentes", exist_ok=True)
    dest = f"fuentes/{nombre}.txt"
    if not os.path.exists(dest):
        for url in (
            f"https://www.gutenberg.org/cache/epub/{ebook_id}/pg{ebook_id}.txt",
            f"https://www.gutenberg.org/files/{ebook_id}/{ebook_id}-0.txt",
        ):
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.text) > 1000:
                    r.encoding = "utf-8"
                    open(dest, "w", encoding="utf-8").write(r.text)
                    print(f"descargado {url} -> {dest} ({len(r.text)} chars)")
                    break
            except Exception as e:
                print("fallo", url, repr(e)[:80])
    txt = open(dest, encoding="utf-8").read()
    i = txt.find("*** START")
    i = txt.find("\n", i) + 1 if i != -1 else 0
    print("--- inicio del contenido ---")
    print(txt[i : i + 700])


if __name__ == "__main__":
    descargar(sys.argv[1], sys.argv[2])
