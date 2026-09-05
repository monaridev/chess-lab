"""Gera as quatro skins SVG originais; Cartoon evoluída na V1.2; Classic permanece intacta.

Formas autorais do Chess Lab, sem fontes, imagens ou personagens externos.
Execute com Python na raiz do projeto; os SVGs gerados são versionados.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "frontend/pieces/skins"

# Cada família tem silhuetas próprias e os símbolos convencionais do xadrez:
# cruz, coroa, ameias, mitra fendida, perfil de cavalo e cabeça de peão.
SHAPES = {
    "soft": {
        "p": '<circle cx="32" cy="19" r="9"/><path d="M26 29Q29 40 21 47Q32 52 43 47Q35 40 38 29Z"/>',
        "r": '<path d="M19 14h7v7h6v-7h6v7h7v-7h5v14l-8 5v13H22V33l-8-5V14Z"/><path d="M23 29h18" fill="none"/>',
        "b": '<path d="M32 9Q15 25 23 32Q27 36 25 40l-6 8q13 5 26 0l-6-8q-2-4 2-8Q49 25 32 9Z"/><path d="m35 18-8 10" fill="none"/>',
        "n": '<path d="M19 48q7-9 9-18l-10 5-6-7 10-12 2-9 8 6q16-1 16 18l-2 17Z"/><path d="M34 23q8 5 6 15" fill="none"/>',
        "q": '<path d="m15 21 8 6 9-12 9 12 8-6-7 22H22Z"/><circle cx="15" cy="18" r="4"/><circle cx="32" cy="11" r="4"/><circle cx="49" cy="18" r="4"/><path d="M22 43h20l4 5H18Z"/>',
        "k": '<path d="M28 6h8v7h6v7h-6v7h-8v-7h-6v-7h6Z"/><path d="M32 29Q20 20 17 31q0 7 7 12l-4 5h24l-4-5q7-5 7-12Q44 20 32 29Z"/>',
    },
    "cute": {
        "p": '<circle cx="32" cy="20" r="11"/><path d="M25 31q-1 8-7 15q0 6 14 6t14-6q-6-7-7-15Z"/>',
        "r": '<path d="M15 15q0-3 4-3h6v9h5v-9h5v9h5v-9h6q4 0 4 3v13q0 4-8 7l1 13H21l1-13q-7-3-7-7Z"/><path d="M24 30h16" fill="none"/>',
        "b": '<path d="M32 8Q13 23 21 33q5 5 2 9l-6 7q15 8 30 0l-6-7q-3-4 2-9Q51 23 32 8Z"/><path d="m35 19-8 10" fill="none"/>',
        "n": '<path d="M18 49q6-5 8-16l-9 3q-6-1-5-7l11-14 1-8 9 6q16 0 17 17l-2 19Z"/><path d="M35 24q9 4 7 14" fill="none"/>',
        "q": '<path d="m13 23 11 7 8-13 8 13 11-7-7 21q-12 6-24 0Z"/><circle cx="13" cy="20" r="4"/><circle cx="32" cy="13" r="4"/><circle cx="51" cy="20" r="4"/><path d="M23 43q-3 4-5 7h28l-5-7"/>',
        "k": '<path d="M29 5h6v8h8v7h-8v8h-6v-8h-8v-7h8Z"/><path d="M32 29q-17-11-17 4q1 8 9 11l-5 6h26l-5-6q8-3 9-11q0-15-17-4Z"/>',
    },
    "minimal": {
        "p": '<circle cx="32" cy="18" r="8"/><path d="m28 29-9 20h26l-9-20Z"/>',
        "r": '<path d="M16 13h8v8h5v-8h6v8h5v-8h8v15l-8 5v16H24V33l-8-5Z"/>',
        "b": '<path d="m32 8-12 19 9 10-9 12h24L35 37l9-10Z"/><path d="m36 18-8 11" fill="none"/>',
        "n": '<path d="m18 49 11-20-12 5-5-7 13-14V7l10 7 13 10v25Z"/><path d="m35 24 6 6v11" fill="none"/>',
        "q": '<path d="m15 18 9 12 8-18 8 18 9-12-7 31H22Z"/><circle cx="15" cy="15" r="3"/><circle cx="32" cy="9" r="3"/><circle cx="49" cy="15" r="3"/>',
        "k": '<path d="M29 5h6v8h7v6h-7v10h-6V19h-7v-6h7Z"/><path d="m21 29 11 6 11-6-4 13 6 7H19l6-7Z"/>',
    },
    "cartoon": {
        "p": '<path d="M23 21C19 10 26 7 33 8c10 0 13 7 10 14-2 6-5 9-10 9-6 0-9-4-10-10Z"/><path d="M27 31q2 8-4 15l-4 3q13 5 27-1l-5-5q-4-6-3-12Z"/><path d="m26 35 11 1" fill="none"/>',
        "r": '<path d="m17 13 8-1v9l6 1 1-10h7l-1 10 6-1 1-8 7 1-2 15q-3 4-9 5l1 11 4 4-27 1 4-6 1-11q-7-1-8-5Z"/><path d="m24 30 17-1m-17 15 17-1" fill="none"/>',
        "b": '<path d="M34 8C30 13 18 21 20 29q1 6 9 8-1 6-9 11 10 6 26 0-9-6-10-11 9-3 9-10-1-9-11-19Z"/><path d="m35 19-8 10m0 12 11-1" fill="none"/><circle cx="34" cy="7" r="3"/>',
        "n": '<path d="M19 49q8-7 10-18l-9 5q-4 2-7-3l-2-5 12-12 2-9 8 7c13-1 19 9 18 21l-4 15Z"/><path d="M34 18q12 5 11 19M35 30q-3 6-2 13m-13-15 3 1" fill="none"/><path d="m27 22 2-1" fill="none"/>',
        "q": '<path d="m15 22 9 8 9-15 8 15 10-10-6 23-24 1Z"/><circle cx="14" cy="18" r="4"/><circle cx="33" cy="10" r="4"/><circle cx="52" cy="16" r="4"/><path d="m22 43-3 6q14 4 27-1l-3-5Z"/><path d="m26 37 13-1" fill="none"/>',
        "k": '<path d="m29 6 7-1v8l7-1 1 7-8 1v8h-7v-8l-7 1-1-7 8-1Z"/><path d="M32 30C19 20 14 26 17 34q2 6 8 9l-5 6q12 4 25-1l-5-6q8-4 9-11 0-11-17-1Z"/><path d="m26 40 12-1" fill="none"/>',
    },
}


def generate():
    for skin, pieces in SHAPES.items():
        folder = ROOT / skin
        folder.mkdir(parents=True, exist_ok=True)
        for color in ("white", "black"):
            fill, stroke = ("#fff5df", "#23362d") if color == "white" else ("#26362f", "#fff5df")
            if skin == "cartoon":
                fill, stroke = ("#fff1cf", "#223745") if color == "white" else ("#213749", "#fff1cf")
            width = "2.3" if skin == "cartoon" else "2"
            join = "miter" if skin == "minimal" else "round"
            base = '<path d="M18 49h28l4 7H14Z"/>' if skin == "minimal" else '<rect x="15" y="48" width="34" height="8" rx="4"/>'
            if skin == "cartoon":
                base = '<path d="M18 48q14 2 28-1l3 8q-18 3-35 0Z"/>'
            for kind, drawing in pieces.items():
                svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><g fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="{join}">{drawing}{base}</g></svg>\n'
                (folder / f"{color}-{kind}.svg").write_text(svg)


if __name__ == "__main__":
    generate()
