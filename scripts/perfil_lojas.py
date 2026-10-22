"""Profile of the exported stores tables: small CSVs to decide the build, without uploading the data.

    python perfil_lojas.py --raw D:\\lojas_raw

Writes <raw>/_perfil/*.csv: counts, distributions and samples. Nothing personal is sampled: meta_author and
meta_copyright appear only as counts.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

VALID = "coalesce(trim(nome_loja_final), '') <> '' AND NOT coalesce(ignorar_nome_repetido, false)"
QUERIES = {
    "lojas_plataforma": "SELECT plataforma, count(*) n, count(*) FILTER (WHERE {v}) com_nome FROM lojas GROUP BY 1 ORDER BY 2 DESC",
    "lojas_texto_plataforma": """SELECT contem_texto_plataforma_utf, count(*) n FROM lojas WHERE {v} GROUP BY 1 ORDER BY 2 DESC LIMIT 60""",
    "lojas_tld": """SELECT regexp_extract(lower(dominio_sem_www), '(\\.[a-z]+(\\.br)?)$', 1) tld, count(*) n,
                    count(*) FILTER (WHERE {v}) com_nome FROM lojas GROUP BY 1 ORDER BY 2 DESC LIMIT 40""",
    "lojas_problemas": """SELECT
          count(*) FILTER (WHERE dominio LIKE '%[%' OR dominio LIKE '%]%') dominio_com_colchetes,
          count(*) FILTER (WHERE nome_loja_final LIKE '%' || chr(65533) || '%') nome_com_fffd,
          count(*) FILTER (WHERE nome_loja_final LIKE '%Ã%') nome_mojibake,
          count(*) FILTER (WHERE nome_loja_final LIKE '%&%;%') nome_entidade_html,
          count(*) FILTER (WHERE coalesce(CAST(meta_author_utf AS VARCHAR), '') <> '') com_meta_author,
          count(*) FILTER (WHERE coalesce(CAST(meta_copyright_utf AS VARCHAR), '') <> '') com_meta_copyright,
          count(*) FILTER (WHERE certificado_error IS NULL AND certificado_expiration IS NOT NULL) com_certificado,
          count(*) FILTER (WHERE TRY_CAST(certificado_expiration AS TIMESTAMP) < TIMESTAMP '2023-04-23') certificado_vencido_na_coleta,
          count(*) FILTER (WHERE total_produtos > 0) com_total_produtos
        FROM lojas WHERE {v}""",
    "lojas_total_produtos": """SELECT CASE WHEN total_produtos IS NULL THEN 'nulo' WHEN total_produtos = 0 THEN '0'
        WHEN total_produtos < 100 THEN '1-99' WHEN total_produtos < 1000 THEN '100-999' WHEN total_produtos < 10000 THEN '1k-9.9k'
        ELSE '10k+' END faixa, count(*) n FROM lojas WHERE {v} GROUP BY 1 ORDER BY min(coalesce(total_produtos, -1))""",
    "lojas_certificado_emissor": """SELECT certificado_organization, count(*) n FROM lojas WHERE {v} AND certificado_organization IS NOT NULL
        GROUP BY 1 HAVING count(*) >= 50 ORDER BY 2 DESC""",
    "lojas_amostra": """SELECT id, dominio, nome_loja_final, loja, total_produtos, protocolo, plataforma, title_utf, meta_og_site_name_utf,
        contem_texto_plataforma_utf, certificado_common_name, certificado_expiration, left(certificado_error, 80) certificado_error
        FROM lojas WHERE {v} USING SAMPLE 300 ROWS (reservoir, 6)""",
    "reclame_status": """SELECT status, principal, count(*) n, round(avg(TRY_CAST(replace(final_score, ',', '.') AS DOUBLE)), 2) nota_media
        FROM reclame_aqui GROUP BY 1, 2 ORDER BY 3 DESC""",
    "reclame_por_loja": """SELECT n, count(*) lojas FROM (SELECT id_loja, count(*) n FROM reclame_aqui GROUP BY 1) GROUP BY 1 ORDER BY 1 LIMIT 20""",
    "reclame_candidatos": """SELECT relacionou, principal, count(*) n, count(DISTINCT id_loja) lojas FROM reclame_aqui_candidatos GROUP BY 1, 2""",
    "reclame_amostra": """SELECT r.id_loja, l.dominio, l.nome_loja_final, r.name, r.company_name, r.status, r.final_score, r.segment, r.principal
        FROM reclame_aqui r JOIN lojas l ON l.id = r.id_loja USING SAMPLE 200 ROWS (reservoir, 6)""",
    "textos_tamanho": """SELECT CASE WHEN length(CAST(texto AS VARCHAR)) < 500 THEN '<500' WHEN length(CAST(texto AS VARCHAR)) < 2000 THEN '500-2k' WHEN length(CAST(texto AS VARCHAR)) < 5000 THEN '2k-5k'
        ELSE '5k+' END faixa, count(*) n FROM lojas_textos_gpt WHERE coalesce(CAST(texto AS VARCHAR), '') <> '' GROUP BY 1""",
    "textos_amostra": """SELECT t.id, l.dominio, l.nome_loja_final, left(CAST(t.texto AS VARCHAR), 3000) texto, left(CAST(t.topicos AS VARCHAR), 1000) topicos
        FROM lojas_textos_gpt t JOIN lojas l USING (id) WHERE coalesce(CAST(t.texto AS VARCHAR), '') <> '' USING SAMPLE 8 ROWS (reservoir, 6)""",
    "textos_backup_vs_atual": """SELECT count(*) backup, count(*) FILTER (WHERE CAST(t.texto AS VARCHAR) = CAST(b.texto AS VARCHAR)) iguais,
        count(*) FILTER (WHERE t.id IS NULL) sem_loja FROM lojas_textos_backup b LEFT JOIN lojas_textos_gpt t USING (id)""",
    "censo_status": """SELECT plataforma, plataforma_verificada, online, online_check_2, count(*) n FROM censo_2022 GROUP BY ALL ORDER BY n DESC LIMIT 80""",
    "censo_msg": "SELECT online_msg, count(*) n FROM censo_2022 GROUP BY 1 ORDER BY 2 DESC LIMIT 40",
    "censo_amostra": "SELECT * FROM censo_2022 USING SAMPLE 200 ROWS (reservoir, 6)",
    "censo_feeds": """SELECT plataforma, status, count(*) n, sum(produtos) produtos, count(*) FILTER (WHERE checado) checados
        FROM censo_2022_feeds GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 60""",
    "feeds_para_importar": "SELECT plataforma, id_plataforma, count(*) n, sum(produtos) produtos FROM feeds_para_importar GROUP BY 1, 2 ORDER BY 3 DESC",
    "censo_x_lojas": """SELECT count(DISTINCT c.dominio) censo, count(DISTINCT CASE WHEN l.id IS NOT NULL THEN c.dominio END) tambem_em_lojas
        FROM censo_2022 c LEFT JOIN lojas l ON lower(l.dominio_sem_www) = lower(regexp_replace(c.dominio, '^www\\.', ''))""",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, type=Path)
    a = ap.parse_args()
    out = a.raw / "_perfil"
    out.mkdir(exist_ok=True)
    con = duckdb.connect()
    for folder in sorted(p for p in a.raw.iterdir() if p.is_dir() and not p.name.startswith("_")):
        con.execute(f"CREATE VIEW {folder.name} AS SELECT * FROM read_parquet('{(folder / '*.parquet').as_posix()}')")
    tables = [r[0] for r in con.execute("SELECT table_name FROM information_schema.tables").fetchall()]
    counts = [f"SELECT '{t}' t, count(*) n FROM {t}" for t in tables]
    if "lojas" in tables:
        counts += [f"SELECT 'lojas_com_nome_valido', count(*) FROM lojas WHERE {VALID}",
                   "SELECT 'dominios_distintos', count(DISTINCT dominio_sem_www) FROM lojas"]
    con.execute(f"COPY ({' UNION ALL '.join(counts)}) TO '{(out / 'contagens.csv').as_posix()}' (HEADER)")
    for name, sql in QUERIES.items():
        try:
            con.execute(f"COPY ({sql.format(v=VALID)}) TO '{(out / (name + '.csv')).as_posix()}' (HEADER)")
            print(f"ok    {name}")
        except duckdb.Error as e:
            print(f"ERRO  {name}: {str(e).splitlines()[0]}")
    print(f"-> {out}  (compacte a pasta _perfil e me envie)")


if __name__ == "__main__":
    main()
