"""Build the online stores dataset from the raw export (exportar_lojas.py).

    python build_lojas.py --raw D:\\lojas_raw --out D:\\lojas_out

Writes <out>/kaggle/*.parquet (full), <out>/sample/*.csv (GitHub sample) and <out>/stats.json.

Tables
    lojas                    63,974 Brazilian online stores with a confirmed name: domain, platform, catalog size,
                             SSL certificate, Reclame Aqui summary, whether a GPT page was written about it
    plataformas              the 13 platforms of the author's feed reader (nlp_management.dbo.Platform)
    reclame_aqui             the Reclame Aqui profile(s) linked to each store
    reclame_aqui_candidatos  every profile the Reclame Aqui search returned for each store
    textos_gpt               the 63,933 pages "A loja X é confiável?" written by GPT-3.5 in April 2023 (SYNTHETIC)
    censo_2022               the 2022 census of Brazilian e-commerce domains: platform and two online checks
    censo_2022_feeds         product feeds found for the census domains
    feeds_importados         feeds imported into the author's crawler, by platform

MEI company names (CNPJ root + the owner's name) are emptied in the Reclame Aqui tables.
Left out on purpose: partners, the third-party commercial list (e-mails, phones, Instagram, client flags), raw
WHOIS, the Reclame Aqui `documents` column (CNPJ, and CPF for individual micro-entrepreneurs), the meta author
and copyright tags (they name people), DataForSEO keywords.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

import duckdb

VALID = "coalesce(trim(nome_loja_final), '') <> '' AND NOT coalesce(ignorar_nome_repetido, false)"
PLATFORMS = [(1, "Moovin"), (2, "xTech"), (3, "NuvemShop"), (4, "Vtex"), (5, "EzCommerce/Lynx"), (6, "CiaShop"),
             (7, "Magento"), (8, "Shopify"), (9, "Awin/Zanox"), (10, "Magazine Luiza / BazaarVoice"), (11, "AdMatic"),
             (12, "Mercado Shops"), (13, "Jet Commerce")]
# spellings found in lojas.plataforma -> one name
PLATFORM_NAMES = {"nuvem shop": "NuvemShop", "nuvemshop": "NuvemShop", "nuvemshop / xtech": "NuvemShop", "xtech": "xTech",
                  "ezcommerce": "EzCommerce/Lynx", "ezcommerce/lynx": "EzCommerce/Lynx", "loja integrada pro": "Loja Integrada",
                  "moovin / shopify": "Moovin", "mercado shops": "Mercado Shops", "jet commerce": "Jet Commerce"}
TEXT_SIGNS = {"woocommerce": "WooCommerce", "wordpress": "WordPress", "lojaintegrada": "Loja Integrada", "lynx": "Lynx",
              "nuvemshop": "NuvemShop", "mercadoshops": "Mercado Shops", "tray": "Tray", "wix": "Wix", "jet": "Jet",
              "magento": "Magento", "shopify": "Shopify", "vtex": "Vtex", "xtech": "xTech", "iluria": "Iluria",
              "prestashop": "PrestaShop", "moovin": "Moovin", "linx": "Linx"}


def fix_name(s: str | None) -> str | None:
    """HTML entities ('TechAudio &#8211') and UTF-8 read as Latin-1 ('PeÃ§as') in store names."""
    if s is None:
        return None
    s = html.unescape(s.replace("&#8211", "&#8211;")).strip(" –-")
    if "Ã" in s:
        try:
            s = s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return s.strip() or None


def platform(s: str | None) -> str | None:
    if s is None or not s.strip():
        return None
    return PLATFORM_NAMES.get(s.strip().lower(), s.strip())


def text_signs(s: str | None) -> str | None:
    """', Woocommerce, Wordpress, Woocommerce, Wordpress' -> 'WooCommerce, WordPress'."""
    if not s:
        return None
    seen = []
    for part in s.split(","):
        p = part.strip().lower()
        if p and TEXT_SIGNS.get(p, part.strip()) not in seen:
            seen.append(TEXT_SIGNS.get(p, part.strip()))
    return ", ".join(seen) or None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--sample-stores", type=int, default=500)
    a = ap.parse_args()
    k, s = a.out / "kaggle", a.out / "sample"
    k.mkdir(parents=True, exist_ok=True)
    s.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    for fn in (fix_name, platform, text_signs):
        con.create_function(fn.__name__, fn, ["VARCHAR"], "VARCHAR", null_handling="special")
    for folder in sorted(p for p in a.raw.iterdir() if p.is_dir() and not p.name.startswith("_") and any(p.glob("*.parquet"))):
        con.execute(f"CREATE VIEW raw_{folder.name} AS SELECT * FROM read_parquet('{(folder / '*.parquet').as_posix()}')")
    stats: dict = {}

    con.execute(f"""CREATE TABLE base AS SELECT * FROM raw_lojas WHERE {VALID}""")
    con.execute("""CREATE TABLE ra AS
        SELECT r.id, r.id_loja, nullif(r.name, '') nome, nullif(r.fantasy_name, '') nome_fantasia,
               CASE WHEN regexp_matches(coalesce(r.company_name, ''), '^\\s*\\d{2}\\.?\\d{3}\\.?\\d{3}') THEN NULL ELSE nullif(r.company_name, '') END razao_social,
               nullif(r.shortname, '') shortname, r.url, r.logo, r.acronym,
               TRY_CAST(replace(r.final_score, ',', '.') AS DOUBLE) nota, r.count reclamacoes,
               TRY_CAST(replace(replace(r.solved_percentual, '%', ''), ',', '.') AS DOUBLE) percentual_resolvido,
               r.status, nullif(r.segment, '') segmento, r.ra_id, nullif(r.marcas, '') marcas,
               nullif(r.previous_names, '') nomes_anteriores, coalesce(r.principal, false) principal
        FROM raw_reclame_aqui r WHERE r.id_loja IN (SELECT id FROM base)""")
    con.execute("""CREATE TABLE ra_principal AS SELECT * FROM (
        SELECT *, row_number() OVER (PARTITION BY id_loja ORDER BY principal DESC, id) rn FROM ra) WHERE rn = 1""")
    con.execute("""CREATE TABLE posts AS
        SELECT p.id, b.id id_loja, p.chave nome_loja, p.title titulo, p.meta_description, p.texto,
               CAST(p.creation_date AS DATE) AS data, 'gpt-' || p.versao_gpt AS modelo
        FROM raw_posts_lojas p LEFT JOIN base b ON b.nome_loja_final = p.chave
        WHERE coalesce(p.texto, '') <> ''""")
    con.execute("""CREATE TABLE lojas AS
        SELECT b.id id_loja, lower(b.dominio_sem_www) dominio, fix_name(b.nome_loja_final) nome, b.slug,
               platform(b.plataforma) plataforma, nullif(trim(b.plataforma), '') plataforma_original,
               text_signs(b.contem_texto_plataforma_utf) sinais_no_html, b.protocolo,
               regexp_extract(lower(b.dominio_sem_www), '(\\.[a-z]+(\\.br)?)$', 1) tld,
               b.total_produtos, fix_name(nullif(b.title_utf, '')) titulo_pagina, fix_name(nullif(b.meta_og_site_name_utf, '')) og_site_name,
               trim(split_part(b.certificado_common_name, ',', 1)) certificado_dominio,
               nullif(CASE WHEN b.certificado_organization LIKE '"%' THEN regexp_extract(b.certificado_organization, '^"([^"]*)"', 1)
                      ELSE b.certificado_organization END, '') certificado_emissor,
               CAST(b.certificado_expiration AS DATE) certificado_validade, b.certificado_error IS NOT NULL certificado_com_erro,
               (SELECT count(*) FROM raw_lojas_rel_source r WHERE r.id_loja = b.id) fontes_no_crawler,
               ra.status reclame_aqui_status, ra.nota reclame_aqui_nota, ra.shortname reclame_aqui_perfil,
               EXISTS (SELECT 1 FROM posts p WHERE p.id_loja = b.id) tem_texto_gpt
        FROM base b LEFT JOIN ra_principal ra ON ra.id_loja = b.id""")
    con.execute("""CREATE TABLE candidatos AS
        SELECT c.id, c.id_loja, c.name nome, CASE WHEN regexp_matches(coalesce(c.company_name, ''), '^\\s*\\d{2}\\.?\\d{3}\\.?\\d{3}') THEN NULL ELSE nullif(c.company_name, '') END razao_social, c.shortname, c.url,
               TRY_CAST(replace(c.final_score, ',', '.') AS DOUBLE) nota, TRY_CAST(c.count AS BIGINT) reclamacoes,
               c.status, nullif(c.segment, '') segmento, c.ra_id,
               c.ra_id IN (SELECT ra_id FROM ra WHERE ra.id_loja = c.id_loja) escolhido
        FROM raw_reclame_aqui_candidatos c WHERE c.id_loja IN (SELECT id FROM base)""")
    dom = "lower(regexp_replace(regexp_replace({}, '^https?://', ''), '^www\\.', ''))"
    con.execute(f"""CREATE TABLE censo AS
        SELECT c.id, {dom.format('c.dominio')} dominio, c.protocolo, platform(c.plataforma) plataforma,
               nullif(c.plataforma_verificada, '') plataforma_verificada, c.online, nullif(c.online_msg, '') online_msg,
               nullif(c.redirecionado_para, '') redirecionado_para, c.online_check_2, nullif(c.online_msg_check_2, '') online_msg_check_2,
               nullif(c.redirecionado_para_check_2, '') redirecionado_para_check_2,
               nullif(nullif(c.url_feed, ''), 'Não identificada') url_feed, nullif(nullif(c.plataforma_feed, ''), 'Não identificada') plataforma_feed,
               nullif(c.contem_texto_plataforma, '') texto_plataforma,
               nullif(nullif(c.id_mercado_shops, ''), 'Não tem') id_mercado_shops,
               l.id_loja
        FROM raw_censo_2022 c LEFT JOIN lojas l ON l.dominio = {dom.format('c.dominio')}""")
    con.execute("""CREATE TABLE censo_feeds AS
        SELECT id, id_censo, url, plataforma plataformas_testadas, produtos, paginas, checado,
               CASE status WHEN 's' THEN 'sucesso' WHEN 'e' THEN 'erro' ELSE status END status, nullif(msg_erro, '') erro
        FROM raw_censo_2022_feeds""")
    con.execute(f"""CREATE TABLE feeds AS
        SELECT f.id, f.plataforma, f.id_plataforma, {dom.format('f.dominio')} dominio, f.url, f.produtos, l.id_loja
        FROM raw_feeds_para_importar f LEFT JOIN lojas l ON l.dominio = {dom.format('f.dominio')}""")
    con.execute("CREATE TABLE plataformas (id_plataforma INTEGER, nome VARCHAR)")
    con.executemany("INSERT INTO plataformas VALUES (?, ?)", PLATFORMS)

    tables = {"lojas": "id_loja", "plataformas": "id_plataforma", "reclame_aqui": "id_loja, id",
              "reclame_aqui_candidatos": "id_loja, id", "textos_gpt": "id", "censo_2022": "id",
              "censo_2022_feeds": "id", "feeds_importados": "id"}
    source = {"reclame_aqui": "ra", "reclame_aqui_candidatos": "candidatos", "textos_gpt": "posts", "censo_2022": "censo",
              "censo_2022_feeds": "censo_feeds", "feeds_importados": "feeds"}
    for t, order in tables.items():
        con.execute(f"COPY (SELECT * FROM {source.get(t, t)} ORDER BY {order}) TO '{(k / (t + '.parquet')).as_posix()}' "
                    f"(FORMAT parquet, COMPRESSION zstd)")
        stats[t] = con.execute(f"SELECT count(*) FROM {source.get(t, t)}").fetchone()[0]

    con.execute(f"CREATE TABLE amostra AS SELECT id_loja FROM lojas USING SAMPLE {a.sample_stores} ROWS (reservoir, 2026)")
    samples = {
        "lojas": "SELECT * FROM lojas WHERE id_loja IN (SELECT id_loja FROM amostra) ORDER BY id_loja",
        "plataformas": "SELECT * FROM plataformas ORDER BY 1",
        "reclame_aqui": "SELECT * FROM ra WHERE id_loja IN (SELECT id_loja FROM amostra) ORDER BY id_loja, id",
        "reclame_aqui_candidatos": "SELECT * FROM candidatos WHERE id_loja IN (SELECT id_loja FROM amostra) ORDER BY id_loja, id",
        "textos_gpt": "SELECT * FROM posts WHERE id_loja IN (SELECT id_loja FROM amostra) ORDER BY id LIMIT 60",
        "censo_2022": "SELECT * FROM censo USING SAMPLE 2000 ROWS (reservoir, 2026) ORDER BY id",
        "censo_2022_feeds": "SELECT * FROM censo_feeds USING SAMPLE 1000 ROWS (reservoir, 2026) ORDER BY id",
        "feeds_importados": "SELECT * FROM feeds USING SAMPLE 1000 ROWS (reservoir, 2026) ORDER BY id",
    }
    for t, q in samples.items():
        con.execute(f"COPY ({q}) TO '{(s / (t + '_sample.csv')).as_posix()}' (HEADER)")

    q = lambda sql: con.execute(sql).fetchall()  # noqa: E731
    stats["lojas_por_plataforma"] = dict(q("SELECT coalesce(plataforma, '(sem)'), count(*) FROM lojas GROUP BY 1 ORDER BY 2 DESC"))
    stats["lojas_por_tld"] = dict(q("SELECT tld, count(*) FROM lojas GROUP BY 1 ORDER BY 2 DESC LIMIT 10"))
    stats["lojas_com_total_produtos"] = q("SELECT count(*) FROM lojas WHERE total_produtos > 0")[0][0]
    stats["lojas_com_certificado"] = q("SELECT count(*) FROM lojas WHERE certificado_validade IS NOT NULL")[0][0]
    stats["lojas_com_reclame_aqui"] = q("SELECT count(*) FROM lojas WHERE reclame_aqui_status IS NOT NULL")[0][0]
    stats["reclame_aqui_status"] = dict(q("SELECT coalesce(reclame_aqui_status, '(sem)'), count(*) FROM lojas GROUP BY 1 ORDER BY 2 DESC"))
    stats["reclame_aqui_nota_media_por_status"] = dict(q("""SELECT reclame_aqui_status, round(avg(reclame_aqui_nota), 2)
        FROM lojas WHERE reclame_aqui_nota IS NOT NULL GROUP BY 1"""))
    stats["textos_gpt_sem_loja"] = q("SELECT count(*) FROM posts WHERE id_loja IS NULL")[0][0]
    stats["nomes_corrigidos"] = q("SELECT count(*) FROM base WHERE fix_name(nome_loja_final) <> nome_loja_final")[0][0]
    stats["censo_online"] = dict(q("SELECT online || ' / ' || online_check_2, count(*) FROM censo GROUP BY 1 ORDER BY 2 DESC LIMIT 8"))
    stats["censo_com_loja"] = q("SELECT count(*) FROM censo WHERE id_loja IS NOT NULL")[0][0]
    stats["censo_feeds_produtos"] = dict(q("""SELECT plataformas_testadas, sum(produtos) FROM censo_feeds WHERE status = 'sucesso'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 8"""))
    (a.out / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
