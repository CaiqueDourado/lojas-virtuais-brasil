"""One store as nested JSON (docs/example-store.json): every row about it in sample/, joined by id_loja.

    python scripts/make_json.py

Starts from the store's row in lojas and nests its rows from reclame_aqui, reclame_aqui_candidatos,
textos_gpt, censo_2022 (with censo_2022_feeds) and feeds_importados. Types come from
schema/columns.json. The GPT page body (textos_gpt.texto) is left out: it is long, synthetic and quotes contact
details. Only pandas is needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STORE = 11187  # estrela10.com.br, the store used in "A look at the data"
SKIP = {"textos_gpt": {"texto"}}


def load(table: str, types: dict[str, str]) -> list[dict]:
    """Rows of sample/<table>_sample.csv as dicts with JSON types; empty cells become None."""
    frame = pd.read_csv(ROOT / "sample" / f"{table}_sample.csv", dtype=str, keep_default_na=False)
    rows = []
    for rec in frame.to_dict("records"):
        row = {}
        for k, v in rec.items():
            if k in SKIP.get(table, set()):
                continue
            t = types[f"{table}.{k}"]
            if v == "":
                row[k] = None
            elif t == "integer":
                row[k] = int(float(v))
            elif t == "float":
                row[k] = float(v)
            elif t == "boolean":
                row[k] = v.lower() == "true"
            else:
                row[k] = v
        rows.append(row)
    return rows


def build() -> dict:
    cols = json.loads((ROOT / "schema" / "columns.json").read_text(encoding="utf-8"))
    types = {f"{c['table']}.{c['name']}": c["type"] for c in cols}
    t = {name: load(name, types) for name in ("lojas", "reclame_aqui", "reclame_aqui_candidatos", "textos_gpt",
                                              "censo_2022", "censo_2022_feeds", "feeds_importados")}
    store = next(r for r in t["lojas"] if r["id_loja"] == STORE)

    def of(table: str) -> list[dict]:
        return sorted((r for r in t[table] if r["id_loja"] == STORE), key=lambda r: r["id"])

    census = [{**c, "censo_2022_feeds": sorted((f for f in t["censo_2022_feeds"] if f["id_censo"] == c["id"]),
                                               key=lambda f: f["id"])} for c in of("censo_2022")]
    return {**store,
            "reclame_aqui": of("reclame_aqui"),
            "reclame_aqui_candidatos": sorted(of("reclame_aqui_candidatos"), key=lambda r: (not r["escolhido"], r["id"])),
            "textos_gpt": of("textos_gpt"),
            "censo_2022": census,
            "feeds_importados": of("feeds_importados")}


def main() -> None:
    out = ROOT / "docs" / "example-store.json"
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
