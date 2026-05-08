"""Genere icon.ico pour PC Tool"""
from PIL import Image, ImageDraw

def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        p = max(1, size // 16)

        # Fond sombre arrondi
        draw.rounded_rectangle([p, p, size-p, size-p],
                                radius=size//5, fill="#1a1a2e")

        # Ecran moniteur bleu
        m = size // 5
        sx1, sy1 = m, m
        sx2, sy2 = size-m, int(size * 0.62)
        draw.rounded_rectangle([sx1, sy1, sx2, sy2],
                                radius=max(1, size//14), fill="#2196f3")

        # Interieur ecran noir
        i = max(1, size//10)
        draw.rounded_rectangle([sx1+i, sy1+i, sx2-i, sy2-i],
                                radius=max(1, size//20), fill="#0d1117")

        # Lignes de code (3 barres colorees)
        if size >= 32:
            lh  = max(1, size//20)
            lx1 = sx1 + i + max(1, size//16)
            for idx, col in enumerate(["#4caf50", "#2196f3", "#ff9800"]):
                ly = sy1 + i + idx * (size//12) + size//14
                lw = [size//3, size//4, size//5][idx]
                draw.rectangle([lx1, ly, lx1+lw, ly+lh], fill=col)

        # Pied moniteur
        cx = size // 2
        py1 = sy2
        py2 = int(size * 0.75)
        pw  = max(1, size//10)
        draw.rectangle([cx-pw, py1, cx+pw, py2], fill="#2196f3")
        bw  = size // 4
        draw.rectangle([cx-bw, py2, cx+bw, py2+max(1,size//12)], fill="#2196f3")

        images.append(img)

    images[0].save("icon.ico", format="ICO", sizes=[(s, s) for s in sizes],
                   append_images=images[1:])
    print("icon.ico cree avec succes !")

if __name__ == "__main__":
    create_icon()
