"""The GPT store pages ('Tudo sobre a loja X'): SourcePost sourceId 82, linked to the stores by chave = store name.

    python exportar_lojas.py --out D:\\lojas_raw --tables posts_lojas
    python perfil_textos.py --raw D:\\lojas_raw
"""

import argparse
from pathlib import Path

import duckdb

VALID = "coalesce(trim(nome_loja_final), '') <> '' AND NOT coalesce(ignorar_nome_repetido, false)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, type=Path)
    a = ap.parse_args()
    out = a.raw / "_perfil"
    out.mkdir(exist_ok=True)
    con = duckdb.connect()
    for name in ("lojas", "posts_lojas", "lojas_textos_backup"):
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{(a.raw / name / '*.parquet').as_posix()}')")
    queries = {
        "posts_contagens": f"""SELECT count(*) posts, count(*) FILTER (WHERE coalesce(texto, '') <> '') com_texto,
              count(DISTINCT chave) chaves, min(creation_date) primeiro, max(creation_date) ultimo,
              (SELECT count(*) FROM lojas WHERE {VALID}) lojas_validas,
              (SELECT count(DISTINCT p.chave) FROM posts_lojas p JOIN lojas l ON l.nome_loja_final = p.chave WHERE {VALID.replace('nome_loja_final', 'l.nome_loja_final').replace('ignorar_nome_repetido', 'l.ignorar_nome_repetido')}) chaves_que_casam_loja_valida,
              (SELECT count(*) FROM posts_lojas p JOIN lojas_textos_backup b ON b.texto = p.texto) textos_iguais_ao_backup
            FROM posts_lojas""",
        "posts_versao_gpt": "SELECT versao_gpt, count(*) n FROM posts_lojas GROUP BY 1 ORDER BY 2 DESC",
        "posts_tamanho": """SELECT CASE WHEN length(texto) < 1000 THEN '<1k' WHEN length(texto) < 3000 THEN '1k-3k'
            WHEN length(texto) < 6000 THEN '3k-6k' ELSE '6k+' END faixa, count(*) n FROM posts_lojas WHERE coalesce(texto, '') <> '' GROUP BY 1""",
        "posts_amostra": """SELECT id, chave, title, meta_description, left(texto, 2500) texto, versao_gpt, creation_date
            FROM posts_lojas WHERE coalesce(texto, '') <> '' USING SAMPLE 10 ROWS (reservoir, 6)""",
    }
    for name, sql in queries.items():
        try:
            con.execute(f"COPY ({sql}) TO '{(out / (name + '.csv')).as_posix()}' (HEADER)")
            print(f"ok    {name}")
        except duckdb.Error as e:
            print(f"ERRO  {name}: {str(e).splitlines()[0]}")
    print(f"-> {out}  (me envie os 4 posts_*.csv)")


if __name__ == "__main__":
    main()
