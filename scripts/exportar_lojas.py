"""Export the online stores database (base 6) and the 2022 e-commerce census from the author's SQL Server
into Parquet files (raw layer). Same exporter as the other datasets: keyset pagination, resumable.

    python -m pip install --user pyodbc pyarrow
    python exportar_lojas.py --out D:\\lojas_raw
    python exportar_lojas.py --out D:\\lojas_raw --status

The GPT store pages are the SourcePost rows of sourceId 82 ('Tudo sobre a loja X'; chave = store name).
Never selected, so they never leave the database: partners (dados_sm_socios), the third-party commercial
list (dados_sm_todos: e-mails, phones, Instagram, client flags), raw WHOIS, the Reclame Aqui `documents`
column (CNPJ, and CPF for individual micro-entrepreneurs), DataForSEO keywords. Windows authentication.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

DB = "fipe.dbo"


@dataclass
class Table:
    name: str
    source: str              # schema-qualified table
    columns: list[tuple[str, str, pa.DataType]]  # (SQL expression, output name, Arrow type)
    block: int = 500_000
    small: bool = False      # exported whole, in one file
    key: str = "id"          # column used for keyset pagination
    where: str = ""          # extra filter, e.g. one sourceId

    @property
    def select(self) -> str:
        return ", ".join(f"{expr} AS [{name}]" for expr, name, _ in self.columns)

    @property
    def schema(self) -> pa.Schema:
        return pa.schema([(name, kind) for _, name, kind in self.columns])


S, I, B, F, T = pa.string(), pa.int64(), pa.bool_(), pa.float64(), pa.timestamp("ms")


TABLES = [
    Table("lojas", "lojas.dbo.lojas", [
        ("id", "id", I), ("dominio", "dominio", S), ("dominioSemWWW", "dominio_sem_www", S),
        ("nome_loja_final", "nome_loja_final", S), ("nome_loja_final_decode", "nome_loja_final_decode", S),
        ("loja", "loja", S), ("ignorar_nome_repetido", "ignorar_nome_repetido", B), ("totalProdutos", "total_produtos", I),
        ("protocolo", "protocolo", S), ("plataforma", "plataforma", S), ("buscouNomeLoja", "buscou_nome_loja", B),
        ("DC_title_utf", "dc_title_utf", S), ("meta_author_utf", "meta_author_utf", S),
        ("meta_copyright_utf", "meta_copyright_utf", S), ("title_utf", "title_utf", S),
        ("meta_og_site_name_utf", "meta_og_site_name_utf", S), ("contem_texto_plataforma_utf", "contem_texto_plataforma_utf", S),
        ("title_ascii", "title_ascii", S), ("meta_og_site_name_ascii", "meta_og_site_name_ascii", S),
        ("contem_texto_plataforma_ascii", "contem_texto_plataforma_ascii", S),
        ("Slugify_nome_loja_final", "slug", S),
        ("certificado_CommonName", "certificado_common_name", S), ("certificado_Organization", "certificado_organization", S),
        ("certificado_OrganizationalUnit", "certificado_organizational_unit", S),
        ("certificado_Locality", "certificado_locality", S),
        ("certificado_StateOrProvinceName_Locality", "certificado_state", S),
        ("certificado_CountryName", "certificado_country", S), ("certificado_ExpirationDate", "certificado_expiration", T),
        ("CAST(certificado_error AS nvarchar(400))", "certificado_error", S),
        ("buscouTopicosOpenIA", "buscou_topicos_openai", B),
    ], block=100_000),
    Table("lojas_textos_gpt", "lojas.dbo.lojas", [
        ("id", "id", I), ("CAST(text AS nvarchar(max))", "texto", S), ("CAST(topicos AS nvarchar(max))", "topicos", S),
    ], block=20_000),
    Table("lojas_textos_backup", "lojas.dbo.temp_apagar_backup_text_posts", [
        ("id", "id", I), ("CAST(text AS nvarchar(max))", "texto", S)], block=20_000),
    Table("posts_lojas", "nlp_data_lake.dbo.SourcePost", [
        ("id", "id", I), ("chave", "chave", S), ("title", "title", S), ("slug", "slug", S),
        ("meta_description", "meta_description", S), ("CAST(text AS nvarchar(max))", "texto", S),
        ("creationDate", "creation_date", T), ("versao_gpt", "versao_gpt", S), ("idCategory", "id_category", I),
        ("imagem", "imagem", S), ("imagem_hash_longo_colorido", "imagem_hash", S),
    ], block=20_000, where="sourceId = 82"),
    Table("lojas_rel_source", "lojas.dbo.lojas_rel_Source", [
        ("id", "id", I), ("idLoja", "id_loja", I), ("sourceId", "source_id", I)]),
    Table("reclame_aqui", "lojas.dbo.lojas_reclame_aqui", [
        ("id", "id", I), ("idLoja", "id_loja", I), ("finalScore", "final_score", S), ("name", "name", S),
        ("fantasyName", "fantasy_name", S), ("companyName", "company_name", S), ("shortname", "shortname", S),
        ("url", "url", S), ("logo", "logo", S), ("acronym", "acronym", S), ("count", "count", I),
        ("solvedPercentual", "solved_percentual", S), ("status", "status", S), ("segment", "segment", S),
        ("ra_id", "ra_id", S), ("marcas", "marcas", S), ("previousNames", "previous_names", S), ("principal", "principal", B),
    ]),
    Table("reclame_aqui_candidatos", "lojas.dbo.lojas_reclame_aqui_raw", [
        ("id", "id", I), ("idLoja", "id_loja", I), ("finalScore", "final_score", S), ("name", "name", S),
        ("fantasyName", "fantasy_name", S), ("companyName", "company_name", S), ("shortname", "shortname", S),
        ("url", "url", S), ("count", "count", S), ("solvedPercentual", "solved_percentual", S), ("status", "status", S),
        ("segment", "segment", S), ("ra_id", "ra_id", S), ("relacionou", "relacionou", B), ("principal", "principal", B),
        ("urlLimpa", "url_limpa", S),
    ]),
    Table("censo_2022", "nlp_management.dbo.Temp_Sources_para_importar_players_ecommerce", [
        ("id", "id", I), ("protocolo", "protocolo", S), ("dominio", "dominio", S), ("plataforma", "plataforma", S),
        ("plataforma_verificada", "plataforma_verificada", S), ("online", "online", S), ("online_msg", "online_msg", S),
        ("redirecionado_para", "redirecionado_para", S), ("online_check_2", "online_check_2", S),
        ("online_msg_check_2", "online_msg_check_2", S), ("redirecionado_para_check_2", "redirecionado_para_check_2", S),
        ("protocolo_check_2", "protocolo_check_2", S), ("url_feed", "url_feed", S), ("plataforma_feed", "plataforma_feed", S),
        ("contem_texto_plataforma", "contem_texto_plataforma", S), ("id_mercado_shops", "id_mercado_shops", S),
    ]),
    Table("censo_2022_feeds", "nlp_management.dbo.Temp_Sources_para_importar_players_ecommerce_feeds", [
        ("id", "id", I), ("idTabelaPai", "id_censo", I), ("url", "url", S), ("plataforma", "plataforma", S),
        ("produtos", "produtos", I), ("checado", "checado", B), ("status", "status", S),
        ("LEFT(msg_erro, 400)", "msg_erro", S), ("paginas", "paginas", I),
    ]),
    Table("feeds_para_importar", "temporario.dbo.feeds_para_importar", [
        ("ID", "id", I), ("plataforma", "plataforma", S), ("idPlataforma", "id_plataforma", I), ("dominio", "dominio", S),
        ("url", "url", S), ("produtos", "produtos", I)], key="ID"),
]
BY_NAME = {t.name: t for t in TABLES}


BROKEN_TEXT = {"values": 0}


def decode_utf16(raw: bytes | None) -> str | None:
    """nvarchar comes as UTF-16. Some scraped texts hold half of an emoji (a lone surrogate), which
    is invalid UTF-16 and makes pyodbc fail; those characters become U+FFFD and are counted."""
    if raw is None:
        return None
    try:
        return raw.decode("utf-16-le")
    except UnicodeDecodeError:
        BROKEN_TEXT["values"] += 1
        return raw.decode("utf-16-le", errors="replace")


def connect(server: str):
    import pyodbc

    connection = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};Trusted_Connection=yes",
        autocommit=True,
    )
    for sql_type in (pyodbc.SQL_WVARCHAR, pyodbc.SQL_WCHAR, pyodbc.SQL_WLONGVARCHAR):
        connection.add_output_converter(sql_type, decode_utf16)
    return connection


def last_id(folder: Path) -> int:
    """Highest id already exported, read from the file names (part-<first>-<last>.parquet)."""
    ends = [int(p.stem.rsplit("-", 1)[1]) for p in folder.glob("part-*.parquet") if p.stem != "part-all"]
    return max(ends, default=0)


def estimated_rows(cursor, table: Table) -> int:
    """Row count from catalog metadata: instant, unlike COUNT(*) on hundreds of millions of rows."""
    db, schema, name = table.source.split(".")
    cursor.execute(
        f"SELECT SUM(p.rows) FROM {db}.sys.partitions p JOIN {db}.sys.objects o ON o.object_id = p.object_id "
        f"WHERE o.name = ? AND p.index_id IN (0, 1)", name)
    return int(cursor.fetchone()[0] or 0)


def to_arrow(rows: list, table: Table) -> pa.Table:
    columns = list(zip(*rows)) if rows else [[] for _ in table.columns]
    arrays = [pa.array(list(values), type=kind) for values, (_, _, kind) in zip(columns, table.columns)]
    return pa.Table.from_arrays(arrays, schema=table.schema)


def export(cursor, table: Table, out: Path) -> None:
    folder = out / table.name
    folder.mkdir(parents=True, exist_ok=True)
    if table.small:
        cursor.execute(f"SELECT {table.select} FROM {table.source} WITH (NOLOCK)" + (f" WHERE {table.where}" if table.where else ""))
        rows = cursor.fetchall()
        pq.write_table(to_arrow(rows, table), folder / "part-all.parquet", compression="zstd")
        print(f"== {table.name}: {len(rows):,} rows")
        return
    start = last_id(folder)
    total = estimated_rows(cursor, table)
    done = sum(pq.ParquetFile(p).metadata.num_rows for p in folder.glob("part-*.parquet"))
    print(f"== {table.name}: about {total:,} rows, {done:,} already exported, resuming after id {start:,}")
    query = (f"SELECT TOP ({table.block}) {table.select} FROM {table.source} WITH (NOLOCK) "
             f"WHERE {table.key} > ? {('AND ' + table.where) if table.where else ''} ORDER BY {table.key}")
    began = time.time()
    exported = 0
    while True:
        cursor.execute(query, start)
        rows = cursor.fetchall()
        if not rows:
            break
        first, last = rows[0][0], rows[-1][0]  # the key is the first column
        target = folder / f"part-{first:012d}-{last:012d}.parquet"
        temporary = target.with_suffix(".tmp")
        pq.write_table(to_arrow(rows, table), temporary, compression="zstd")
        temporary.replace(target)  # a block is either fully written or absent
        start = last
        exported += len(rows)
        done += len(rows)
        rate = exported / max(time.time() - began, 1)
        left = max(total - done, 0) / rate if rate else 0
        print(f"   {done:,}/{total:,} rows  ({rate:,.0f}/s, about {left / 60:,.0f} min left)", flush=True)
        if len(rows) < table.block:
            break
    print(f"   {table.name} finished: {done:,} rows in {folder}")
    if BROKEN_TEXT["values"]:
        print(f"   {BROKEN_TEXT['values']:,} text values had broken characters (half emojis), replaced by U+FFFD")
        BROKEN_TEXT["values"] = 0


def status(out: Path) -> None:
    for table in TABLES:
        files = list((out / table.name).glob("part-*.parquet"))
        rows = sum(pq.ParquetFile(p).metadata.num_rows for p in files)
        size = sum(p.stat().st_size for p in files) / 1e9
        print(f"{table.name:16} {len(files):5} files {rows:15,} rows {size:8.2f} GB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path, help="folder for the Parquet files (needs ~2 GB free)")
    parser.add_argument("--tables", nargs="*", default=[t.name for t in TABLES], choices=list(BY_NAME))
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--status", action="store_true", help="show what was exported and stop")
    args = parser.parse_args()
    if args.status:
        status(args.out)
        return
    cursor = connect(args.server).cursor()
    try:
        for name in args.tables:
            export(cursor, BY_NAME[name], args.out)
    except KeyboardInterrupt:
        print("\nStopped. Run the same command again to resume.", file=sys.stderr)


if __name__ == "__main__":
    main()
