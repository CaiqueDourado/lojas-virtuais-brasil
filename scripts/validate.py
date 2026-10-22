"""Checks on the sample (and, with --full, on the Kaggle Parquet files). Exits with 1 on any failure.

    python scripts/validate.py
    python scripts/validate.py --full D:\\lojas_out\\kaggle
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FAIL: list[str] = []
STATUS = {"RA1000", "GREAT", "GOOD", "REGULAR", "BAD", "NOT_RECOMMENDED", "NO_INDEX", "UNDER_REVIEW"}


def check(ok: bool, message: str) -> None:
    print(("ok    " if ok else "FAIL  ") + message)
    if not ok:
        FAIL.append(message)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", type=Path)
    a = ap.parse_args()
    meta = json.loads((ROOT / "schema" / "dataset.json").read_text(encoding="utf-8"))
    cols = json.loads((ROOT / "schema" / "columns.json").read_text(encoding="utf-8"))
    names = [t["name"] for t in meta["tables"]]
    d = ({t: pd.read_parquet(a.full / f"{t}.parquet") for t in names} if a.full else
         {t: pd.read_csv(ROOT / "sample" / f"{t}_sample.csv") for t in names})
    for t, df in d.items():
        check(list(df.columns) == [c["name"] for c in cols if c["table"] == t], f"{t}: columns match schema/columns.json")
    lo, ra, ca, gp, ce, cf, fe = (d[x] for x in ("lojas", "reclame_aqui", "reclame_aqui_candidatos", "textos_gpt",
                                               "censo_2022", "censo_2022_feeds", "feeds_importados"))
    check(lo.id_loja.is_unique and lo.dominio.is_unique, "lojas: id and domain unique")
    check(lo.nome.notna().all() and lo.nome.is_unique, "lojas: every store has a name, names unique")
    check(not lo.nome.str.contains("&#|Ã", regex=True).any(), "lojas: no HTML entity or mojibake in names")
    check(not lo.dominio.str.startswith("www.").any(), "lojas: domains without www")
    check(lo.reclame_aqui_status.dropna().isin(STATUS).all(), "lojas: known Reclame Aqui status")
    check(lo.reclame_aqui_nota.dropna().between(0, 10).all(), "lojas: Reclame Aqui score between 0 and 10")
    check(not lo.certificado_emissor.dropna().str.startswith('"').any(), "lojas: certificate issuer without quotes")
    for t, df in (("reclame_aqui", ra), ("reclame_aqui_candidatos", ca)):
        check(df.id_loja.isin(lo.id_loja).all() if not a.full else df.id_loja.isin(lo.id_loja).all(), f"{t}: every store exists")
        check(df.status.dropna().isin(STATUS).all(), f"{t}: known status")
    for t, df in (("reclame_aqui", ra), ("reclame_aqui_candidatos", ca)):
        check(not df.razao_social.dropna().str.match(r"^\s*\d{2}\.?\d{3}\.?\d{3}").any(),
              f"{t}: no MEI company name (CNPJ root + owner's name)")
    cpf = r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"
    check(not any(df[c].astype(str).str.contains(cpf, regex=True).any() for df in d.values()
                  for c in df.columns if df[c].dtype == object), "no CPF-like number anywhere")
    check("documents" not in ra.columns and "documents" not in ca.columns, "reclame_aqui: no documents column (CNPJ/CPF)")
    check(gp.id.is_unique, "textos_gpt: id unique")
    check(gp.id_loja.dropna().isin(lo.id_loja).all(), "textos_gpt: linked stores exist")
    check(gp.modelo.eq("gpt-3.5").all(), "textos_gpt: model recorded")
    check(ce.id.is_unique, "censo_2022: id unique")
    check(cf.id_censo.isin(ce.id).all() if a.full else True, "censo_2022_feeds: every census row exists (full only)")
    check(cf.status.isin({"sucesso", "erro"}).all(), "censo_2022_feeds: status sucesso/erro")
    check(fe.id_plataforma.isin(d["plataformas"].id_plataforma).all(), "feeds_importados: platform exists")
    banned = {"email", "telefone", "socio", "whois", "cpf", "cnpj", "meta_author", "instagram"}
    check(not any(b in c.lower() for df in d.values() for c in df.columns for b in banned), "no personal-data columns")
    if FAIL:
        sys.exit(f"{len(FAIL)} check(s) failed")
    print("all checks passed")


if __name__ == "__main__":
    main()
