# Data quality report

What is reliable, what was fixed, and what is still wrong. Counts are in `stats.json`.

## Know before using

- **`textos_gpt` is not information about the stores.** GPT-3.5 wrote the 63,933 pages from the store name
  alone. Every page answers "yes" to "A loja X é confiável?" and "A loja X é segura?", including the stores
  Reclame Aqui marks NOT_RECOMMENDED, and most invent a founding year, a city, a share of positive reviews or
  a Reclame Aqui reputation. Over the full table, 63,538 pages answer yes, 4 answer no and 391 have no answer
  the parser could read (`scripts/make_figures.py`); all 1,320 pages about stores with a Reclame Aqui status answer
  yes, the 360 NOT_RECOMMENDED included. In a hand-read sample of 60 pages, 38 gave a founding year or age. Use them to study model output (hallucination, sycophancy, boilerplate), not stores.
  The page title repeats the typo "confável" from the site's template.
- **A snapshot of April 2023.** Stores close, change platform and renew certificates. `certificado_validade`
  is the date on the certificate read then, not today's.
- **Platform is the declared one.** `plataforma` comes from the source lists and is empty for 9,556 stores;
  `sinais_no_html` is a separate, noisier test. "Jet" appears in it for many stores that are not on Jet
  Commerce, because the test looked for the substring "jet" (it is in words like "objeto"); "Tray" and "Wix"
  have the same risk.
- **The Reclame Aqui link can be wrong.** The profile was chosen by name and website among the search results.
  A common store name can point to a different company with the same name; compare `reclame_aqui.url` (the website the
  company registered) with `lojas.dominio` before trusting a pair. `reclame_aqui_candidatos` keeps every
  result, so other choices can be made.
- **Most linked profiles have no score.** 17,320 of the 18,676 stores with a profile are NO_INDEX (too few
  complaints to be rated). Scores exist for 1,337 stores.
- **`total_produtos` is filled for 6,749 stores**, the ones whose feed was read; empty does not mean zero.

## Fixed in this release

| # | Problem in the source | Rows | Fix |
|---|---|---:|---|
| 1 | Same platform spelled several ways (Nuvem Shop / NuvemShop, xTech / Xtech, EzCommerce / Ezcommerce, Loja Integrada PRO) | 63,974 | Unified in `plataforma`; original kept |
| 2 | HTML entities and UTF-8 read as Latin-1 in store names ("TechAudio &#8211", "PeÃ§as") | 3,034 | Fixed |
| 3 | Platform names repeated in the HTML test (", Woocommerce, Wordpress, Woocommerce, Wordpress") | most | Listed once, cased |
| 4 | Certificate authority stored with quotes and repeated ('"Cloudflare, Inc.", "Cloudflare, Inc."') | about 4,800 | First name, no quotes |
| 5 | Domains with and without www | all | Without www, lower case |
| 6 | Reclame Aqui score and share solved as text ("7,45", "--") | all | Numbers; "--" empty |
| 7 | GPT pages only in a table of posts, not linked to the store | 63,933 | Linked by name (3 pages without a store) |
| 8 | Another version of the pages kept in a backup table | 63,974 | Left out (only 54 equal to the published ones) |

## Left out on purpose

| Data | Why |
|---|---|
| Partners of the companies | Names of people |
| The third-party domain list's fields: e-mails, phones, Instagram, client flags, company data | Contacts and a third party's commercial data |
| Raw WHOIS | Registrant data of people |
| Reclame Aqui `documents` | CNPJ, and CPF for individual micro-entrepreneurs |
| Meta author and copyright tags | Often a person's name |
| 49,952 domains without a confirmed name | Offline, parked, generic title or repeated name |
| DataForSEO keywords per store | Licensed data |

## Known limitations

- 25 stores have no recognizable top-level domain, and a few hundred use foreign ones (.ar, .cl, .co, .mx…):
  they were on the source lists, but not all of them sell in Brazil.
- `fontes_no_crawler` counts links to the author's crawler, not how big a store is.
- In the census, `online = OK` means the domain answered in 2022, not that it sold anything; 2,406 failed both
  checks.
- If you are a store owner and want your store removed, open an issue: it will be removed in the next
  version.
