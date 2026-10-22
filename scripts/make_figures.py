"""Figures for README and Kaggle (EN and PT).

    python scripts/make_figures.py                            # platforms (from stats.json)
    python scripts/make_figures.py --data D:\\lojas_out\\kaggle # + what GPT said x what Reclame Aqui says

1. stores per e-commerce platform;
2. share of GPT pages that answer "yes, it is reliable", by the store's Reclame Aqui status.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
INK, MUTED, LINE, BG, BLUE, GRAY = "#111111", "#555555", "#e6e6e6", "#fdfdfc", "#2a78d6", "#b8b8b8"
for family in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(family, fallback_to_default=False)
        plt.rcParams["font.family"] = family
        break
    except ValueError:
        continue
ANSWER = re.compile(r"conf[ií]?[aá]vel\??\s*</h2>\s*(.{0,120})", re.I | re.S)
ORDER = ["RA1000", "GREAT", "GOOD", "REGULAR", "BAD", "NOT_RECOMMENDED"]
TEXT = {
    "en": {"suffix": "", "t1": "Which platform Brazilian online stores run on",
           "s1": "{n} stores with a confirmed name, April 2023 · {none} with no platform detected",
           "t2": "GPT said every store was reliable, whatever Reclame Aqui said",
           "s2": "Share of GPT-3.5 pages whose answer to \"Is the store reliable?\" is yes, by the store's Reclame Aqui status",
           "pages": "{n} pages", "src": "Source: dataset lojas-virtuais-brasil (Caique Dourado)"},
    "pt": {"suffix": ".pt-BR", "t1": "Em que plataforma rodam as lojas virtuais brasileiras",
           "s1": "{n} lojas com nome confirmado, abril de 2023 · {none} sem plataforma detectada",
           "t2": "O GPT disse que toda loja era confiável, dissesse o Reclame Aqui o que fosse",
           "s2": "Fração das páginas do GPT-3.5 que respondem sim a \"A loja é confiável?\", pelo status da loja no Reclame Aqui",
           "pages": "{n} páginas", "src": "Fonte: base lojas-virtuais-brasil (Caique Dourado)"},
}


def says_yes(text: str) -> bool | None:
    m = ANSWER.search(text or "")
    if not m:
        return None
    a = m.group(1).strip().lower()
    if a.startswith(("não", "nao")) or "não é confiável" in a or "não podemos" in a:
        return False
    return True


def frame(fig, t, s, src):
    fig.patch.set_facecolor(BG)
    fig.text(0.02, 0.93, t, fontsize=15, weight="bold", color=INK)
    fig.text(0.02, 0.875, s, fontsize=10, color=MUTED)
    fig.text(0.02, 0.02, src, fontsize=8, color=MUTED)


def style(ax):
    ax.set_facecolor(BG)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.tick_params(colors=INK, labelsize=9, length=0)
    ax.set_xticks([])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    stats = json.loads((ROOT / "stats.json").read_text(encoding="utf-8"))
    plat = {k: v for k, v in stats["lojas_por_plataforma"].items() if k != "(sem)"}
    top = dict(sorted(plat.items(), key=lambda kv: -kv[1])[:14])
    figures = {}
    gpt = None
    if a.data:
        lo = pd.read_parquet(a.data / "lojas.parquet", columns=["id_loja", "reclame_aqui_status"])
        tx = pd.read_parquet(a.data / "textos_gpt.parquet", columns=["id_loja", "texto"])
        tx["sim"] = tx.texto.map(says_yes)
        j = tx.merge(lo, on="id_loja")
        figures["gpt_answer"] = {str(k): int(v) for k, v in tx.sim.value_counts(dropna=False).items()}
        gpt = (j[j.reclame_aqui_status.isin(ORDER) & j.sim.notna()].groupby("reclame_aqui_status").sim
               .agg(["mean", "count"]).reindex(ORDER).dropna())
        figures["gpt_yes_by_status"] = {k: [round(float(r["mean"]), 4), int(r["count"])] for k, r in gpt.iterrows()}
    for lang, t in TEXT.items():
        fmt = (lambda n: f"{n:,}".replace(",", ".")) if lang == "pt" else (lambda n: f"{n:,}")
        fig, ax = plt.subplots(figsize=(10, 5.6), dpi=110)
        fig.subplots_adjust(left=0.2, right=0.95, top=0.82, bottom=0.07)
        frame(fig, t["t1"], t["s1"].format(n=fmt(stats["lojas"]), none=fmt(stats["lojas_por_plataforma"].get("(sem)", 0))), t["src"])
        style(ax)
        names, values = list(top)[::-1], list(top.values())[::-1]
        ax.barh(names, values, color=BLUE, height=0.7)
        for y, v in enumerate(values):
            ax.text(v, y, " " + fmt(v), va="center", fontsize=9, color=INK)
        fig.savefig(OUT / f"platforms{t['suffix']}.png", facecolor=BG)
        plt.close(fig)
        if gpt is not None and len(gpt):
            fig, ax = plt.subplots(figsize=(10, 4.6), dpi=110)
            fig.subplots_adjust(left=0.2, right=0.9, top=0.8, bottom=0.08)
            frame(fig, t["t2"], t["s2"], t["src"])
            style(ax)
            labels = list(gpt.index)[::-1]
            vals = (gpt["mean"] * 100).tolist()[::-1]
            counts = gpt["count"].tolist()[::-1]
            ax.barh(labels, [100] * len(vals), color=LINE, height=0.6)
            ax.barh(labels, vals, color=BLUE, height=0.6)
            for y, (v, c) in enumerate(zip(vals, counts)):
                ax.text(101, y, f"{v:.0f}%  ·  " + t["pages"].format(n=fmt(c)), va="center", fontsize=9, color=INK)
            ax.set_xlim(0, 140)
            fig.savefig(OUT / f"gpt-vs-reclame-aqui{t['suffix']}.png", facecolor=BG)
            plt.close(fig)
    (ROOT / "docs" / "figures.json").write_text(json.dumps(figures, indent=1), encoding="utf-8")
    print(json.dumps(figures, indent=1))


if __name__ == "__main__":
    main()
