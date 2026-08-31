# -*- coding: utf-8 -*-
"""Genera la identidad visual de «El castillo de la memoria»: un castillo sobre
un libro abierto.

Salidas en public/:
  - favicon-castillo.png      512x512  (icono general del sitio)
  - apple-touch-icon.png      180x180
  - og-castillo.png          1200x630  (imagen al compartir el enlace)

Se dibuja con Pillow a 4x y se reduce con LANCZOS para que los bordes queden
suaves (Pillow no antialiasa los polígonos). Reproducible: no hay binarios
opacos en el repo, solo este script y su salida.

Uso:  python scripts/generar_identidad.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
PUBLIC = RAIZ / "public"

# Paleta, tomada de la interfaz (home.css / lectura.css).
FONDO = (26, 26, 26)
FONDO_OG = (18, 18, 18)
PIEDRA = (201, 180, 122)        # dorado cálido del castillo
PIEDRA_OSCURA = (150, 131, 79)
HUECO = (38, 33, 20)            # puertas y ventanas
PAGINA = (242, 232, 213)        # papel
PAGINA_SOMBRA = (206, 193, 168)
CUBIERTA = (63, 143, 102)       # verde de acento del sitio
TEXTO = (240, 240, 240)
ORO = (183, 168, 106)


def almenas(d, x0, x1, base_y, alto, n, color):
    """n merlones (dientes) repartidos entre x0 y x1, creciendo hacia arriba."""
    ancho_total = x1 - x0
    paso = ancho_total / (2 * n - 1)
    for i in range(n):
        mx0 = x0 + 2 * i * paso
        d.rectangle([mx0, base_y - alto, mx0 + paso, base_y], fill=color)


def torre(d, x0, x1, techo_y, base_y, n_almenas=3):
    """Torre con almenas y una ventana."""
    alto_almena = (x1 - x0) * 0.28
    d.rectangle([x0, techo_y, x1, base_y], fill=PIEDRA)
    almenas(d, x0, x1, techo_y, alto_almena, n_almenas, PIEDRA)
    # ventana (arco simple: círculo + rectángulo)
    vw = (x1 - x0) * 0.26
    cx = (x0 + x1) / 2
    vy = techo_y + (x1 - x0) * 0.42
    d.ellipse([cx - vw, vy - vw, cx + vw, vy + vw], fill=HUECO)
    d.rectangle([cx - vw, vy, cx + vw, vy + vw * 1.7], fill=HUECO)


def dibujar_escena(d, S, con_fondo_redondeado=True):
    """Castillo sobre libro abierto en un espacio lógico de 1024x1024."""
    def E(*v):  # escala coordenadas lógicas al lienzo real
        return [x * S for x in v]

    if con_fondo_redondeado:
        d.rounded_rectangle(E(0, 0, 1024, 1024), radius=180 * S, fill=FONDO)

    # ---- Castillo -------------------------------------------------------
    base = 668
    torre(d, 250 * S, 372 * S, 330 * S, base * S)      # torre izquierda
    torre(d, 652 * S, 774 * S, 330 * S, base * S)      # torre derecha

    # muralla central entre torres
    d.rectangle(E(360, 430, 664, base), fill=PIEDRA_OSCURA)
    almenas(d, 360 * S, 664 * S, 430 * S, 34 * S, 5, PIEDRA_OSCURA)

    # torre central, más alta
    torre(d, 452 * S, 572 * S, 214 * S, base * S)

    # portón: arco de medio punto
    pw = 42
    cx = 512
    py = 560
    d.ellipse(E(cx - pw, py - pw, cx + pw, py + pw), fill=HUECO)
    d.rectangle(E(cx - pw, py, cx + pw, base), fill=HUECO)

    # ---- Libro abierto --------------------------------------------------
    # cubierta (asoma por debajo de las páginas)
    d.polygon(E(120, 706, 512, 668, 904, 706, 904, 838, 512, 806, 120, 838),
              fill=CUBIERTA)
    # páginas izquierda y derecha, con el lomo en el centro
    d.polygon(E(140, 700, 505, 664, 505, 792, 140, 812), fill=PAGINA)
    d.polygon(E(519, 664, 884, 700, 884, 812, 519, 792), fill=PAGINA)
    # sombra del lomo y renglones insinuados
    d.polygon(E(505, 664, 519, 664, 519, 792, 505, 792), fill=PAGINA_SOMBRA)
    for i, dy in enumerate((26, 58, 90)):
        d.line(E(205, 716 + dy, 470, 700 + dy), fill=PAGINA_SOMBRA, width=int(7 * S))
        d.line(E(554, 700 + dy, 819, 716 + dy), fill=PAGINA_SOMBRA, width=int(7 * S))


def lienzo_icono(lado, con_fondo=True):
    S = 4  # supermuestreo
    img = Image.new("RGBA", (1024 * S, 1024 * S), (0, 0, 0, 0))
    dibujar_escena(ImageDraw.Draw(img), S, con_fondo)
    return img.resize((lado, lado), Image.LANCZOS)


def fuente(nombres, tam):
    for n in nombres:
        try:
            return ImageFont.truetype(n, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def generar():
    PUBLIC.mkdir(exist_ok=True)

    icono = lienzo_icono(512)
    icono.save(PUBLIC / "favicon-castillo.png")
    lienzo_icono(180).save(PUBLIC / "apple-touch-icon.png")

    # ---- Imagen para compartir el enlace (Open Graph) --------------------
    W, H = 1200, 630
    og = Image.new("RGB", (W, H), FONDO_OG)
    d = ImageDraw.Draw(og)
    # escudo del castillo a la izquierda
    escudo = lienzo_icono(430, con_fondo=False)
    og.paste(escudo, (78, 100), escudo)

    f_tit = fuente(["georgiab.ttf", "Georgia Bold.ttf", "arialbd.ttf"], 74)
    f_sub = fuente(["georgia.ttf", "arial.ttf"], 38)
    f_pie = fuente(["georgia.ttf", "arial.ttf"], 30)

    x = 560
    d.text((x, 214), "El castillo", font=f_tit, fill=TEXTO)
    d.text((x, 300), "de la memoria", font=f_tit, fill=TEXTO)
    d.text((x, 404), "Plataforma de idiomas", font=f_sub, fill=ORO)
    d.text((x, 460), "Lee, repasa y juega en alemán, inglés y español",
           font=f_pie, fill=(154, 154, 154))
    d.rectangle([x, 392, x + 300, 395], fill=ORO)

    og.save(PUBLIC / "og-castillo.png")

    for f in ("favicon-castillo.png", "apple-touch-icon.png", "og-castillo.png"):
        p = PUBLIC / f
        print(f"  {f:26} {p.stat().st_size // 1024:4} KB")
    print(f"-> {PUBLIC}")


if __name__ == "__main__":
    generar()
