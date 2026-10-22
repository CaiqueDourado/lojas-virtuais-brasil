"""Cover image for README and Kaggle (EN and PT): the numbers of the dataset and the platforms. Reads stats.json.

    python scripts/make_cover.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, LINE, BG, BLUE = "#111111", "#555555", "#e6e6e6", "#fdfdfc", "#2a78d6"
TEXT = {
    "en": {"suffix": "", "title": "Brazilian online stores", "sub": "Platform, SSL, Reclame Aqui and the 2022 e-commerce census · April 2023",
           "facts": [("{lojas}", "stores with a confirmed name"), ("{ra}", "Reclame Aqui profiles"),
                     ("{gpt}", "GPT-3.5 pages (synthetic)"), ("{censo}", "domains in the 2022 census")],
           "plat": "Stores per platform"},
    "pt": {"suffix": ".pt-BR", "title": "Lojas virtuais do Brasil", "sub": "Plataforma, SSL, Reclame Aqui e o censo de e-commerce de 2022 · abril de 2023",
           "facts": [("{lojas}", "lojas com nome confirmado"), ("{ra}", "perfis do Reclame Aqui"),
                     ("{gpt}", "páginas do GPT-3.5 (sintéticas)"), ("{censo}", "domínios no censo de 2022")],
           "plat": "Lojas por plataforma"},
}
for family in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(family, fallback_to_default=False)
        plt.rcParams["font.family"] = family
        break
    except ValueError:
        continue


def main() -> None:
    st = json.loads((ROOT / "stats.json").read_text(encoding="utf-8"))
    plat = [(k, v) for k, v in st["lojas_por_plataforma"].items() if k != "(sem)"][:7]
    for lang, t in TEXT.items():
        fmt = (lambda n: f"{n:,}".replace(",", ".")) if lang == "pt" else (lambda n: f"{n:,}")
        vals = {"lojas": fmt(st["lojas"]), "ra": fmt(st["reclame_aqui"]), "gpt": fmt(st["textos_gpt"]), "censo": fmt(st["censo_2022"])}
        fig = plt.figure(figsize=(11.2, 5.6), dpi=100)
        fig.patch.set_facecolor(BG)
        fig.text(0.04, 0.86, t["title"], fontsize=28, weight="bold", color=INK)
        fig.text(0.04, 0.78, t["sub"], fontsize=12.5, color=MUTED)
        for i, (num, label) in enumerate(t["facts"]):
            y = 0.62 - i * 0.13
            fig.text(0.04, y, num.format(**vals), fontsize=22, weight="bold", color=BLUE)
            fig.text(0.04, y - 0.05, label, fontsize=11.5, color=INK)
        ax = fig.add_axes([0.62, 0.1, 0.34, 0.58])
        ax.set_facecolor(BG)
        names, values = [p[0] for p in plat][::-1], [p[1] for p in plat][::-1]
        ax.barh(names, values, color=BLUE, height=0.65)
        for y, v in enumerate(values):
            ax.text(v, y, " " + fmt(v), va="center", fontsize=9, color=INK)
        for side in ("top", "right", "bottom"):
            ax.spines[side].set_visible(False)
        ax.spines["left"].set_color(LINE)
        ax.tick_params(colors=INK, labelsize=10, length=0)
        ax.set_xticks([])
        ax.set_xlim(0, max(values) * 1.25)
        ax.set_title(t["plat"], loc="left", fontsize=10, color=MUTED)
        fig.savefig(ROOT / "docs" / "img" / f"cover{t['suffix']}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    main()
