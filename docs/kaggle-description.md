**Lojas virtuais do Brasil**: 63.974 lojas virtuais brasileiras com plataforma, certificado SSL e reputação no Reclame Aqui, o censo de e-commerce de 2022 e 63.933 páginas escritas pelo GPT-3.5. **Brazilian online stores**: platform, SSL, Reclame Aqui and the 2022 e-commerce census.

![Brazilian online stores](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/cover.png)

## The site: tudosobrelojas.com (2023)

[![tudosobrelojas.com](https://raw.githubusercontent.com/CaiqueDourado/CaiqueDourado/main/assets/tudosobrelojas.com_screenshot.png)](https://web.archive.org/web/20250618081809/https://tudosobrelojas.com/a-loja-saboreat-e-confavel-tudo-sobre-a-loja-saboreat/)

*Tudo Sobre Lojas, [archived on the Wayback Machine](https://web.archive.org/web/20250618081809/https://tudosobrelojas.com/a-loja-saboreat-e-confavel-tudo-sobre-a-loja-saboreat/).*

In 2023 the author ran **Tudo Sobre Lojas**, a site with one page per Brazilian online store, each answering
"A loja X é confiável?" ("Is store X reliable?"). This dataset is the database behind it.

| Part | How it worked | In this dataset |
|---|---|---|
| Pages | One per store: is it reliable, is it safe, benefits, payment and shipping, coupons, order tracking, customer service | Text in `textos_gpt` |
| Platform | Fingerprinting of the e-commerce platform (Shopify, VTEX, WooCommerce, NuvemShop…) by three tests | `lojas.plataforma`, `sinais_no_html`, census feeds |
| Security | SSL certificate checked for every store | `certificado_*` |
| Reputation | Reclame Aqui profile found by a Selenium-driven search, plus links to search the store on Consumidor.gov.br, Jusbrasil and Reclame Aqui | `reclame_aqui`, `reclame_aqui_candidatos` |
| Visual evidence | Screenshots of the store's home page and of its Reclame Aqui page, taken with C# and Selenium | No (images) |
| Company data | CNPJ read from WHOIS and crossed with the Receita Federal register (legal name, CNAE, address, partners, contacts) | No (personal data) |
| Text | Written by GPT-3.5 from the store name | Yes, marked synthetic |

63,974 Brazilian online stores found and checked in April 2023, with three tests of the e-commerce platform (declared, names in the HTML, a feed path that answered), catalog size from the feed, SSL certificate and the Reclame Aqui profile chosen among the search results. With them, the 2022 census of 81,018 e-commerce domains and their product feeds.

![Stores per platform](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/platforms.png)

**About `textos_gpt`.** The author's site had one page per store, "A loja X é confiável?", written by GPT-3.5 from the store name alone. 63,538 of the 63,542 pages with a readable answer say the store is reliable, including all 360 about stores Reclame Aqui does not recommend, and most invent a founding year, a city or a reputation. They are published as a record of model output next to real reputation data, **not as facts about the stores**.

![GPT x Reclame Aqui](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/gpt-vs-reclame-aqui.png)

## A look at the data

**One store across the tables**, `estrela10.com.br` (`id_loja` 11187):

| Table | What it has for this store |
|---|---|
| `lojas` | name "Estrela 10", platform Linx, 5,178 products in the feed, Let's Encrypt certificate valid until 2023-07-03, Reclame Aqui RA1000 with score 8.8, profile `estrela10` |
| `reclame_aqui` | profile `estrela10`: 866 complaints, 95.4% solved, status RA1000 |
| `reclame_aqui_candidatos` | every profile the search for "Estrela 10" returned, with `escolhido = true` on the one kept |
| `textos_gpt` | the page GPT-3.5 wrote on 12 April 2023 (excerpt below) |

> **A loja Estrela 10 é confiável?**
> Sim, a loja Estrela 10 é confiável. A loja tem um alto índice de avaliações positivas por parte de seus
> clientes. […]
>
> *("Is Estrela 10 reliable? Yes, Estrela 10 is reliable. The store has a high rate of positive reviews from
> its customers.")*

The model got only the store name. The founding year the page gives (2008) and the "high rate of positive
reviews" come from no source. Here Reclame Aqui happens to agree; the model says the same about the 360 stores
Reclame Aqui does not recommend.

**Feeds found by the 2022 census** (`censo_2022` + `censo_2022_feeds`):

| Domain | Declared platform | Feed that answered | Products |
|---|---|---|---:|
| uniformes25.com.br | NuvemShop | `…/tiendanube/stores/…/fb_catalog.xml` | 111 |
| solshine.com.br | Shopify | `/products.json` | 362 |
| obeleza.com.br | Mercado Shops | `mercadoshops.com.br/darwin/rss/150043409/gshopping` | 919 |
| cyclone.com.br | Vtex | `/XMLData/googleshopping.xml` | 582 |

## In numbers

| Reclame Aqui status | Stores | Mean score |
|---|---:|---:|
| RA1000 | 88 | 8.95 |
| GREAT | 309 | 8.52 |
| GOOD | 325 | 7.45 |
| REGULAR | 182 | 6.53 |
| BAD | 67 | 5.49 |
| NOT_RECOMMENDED | 366 | 3.98 |
| UNDER_REVIEW | 19 | |
| NO_INDEX (too few complaints to rate) | 17,320 | |
| no profile found | 45,298 | |

- **Domains:** 61,129 stores on `.com.br`, 2,250 on `.com`, a few hundred on other endings.
- **Certificates:** 53,668 stores had an SSL certificate in April 2023.
- **Catalog size:** 6,749 stores have the number of products read from their feed.
- **2022 census:** 81,018 domains; 78,295 answered both online checks and 2,406 failed both; 55,707 are also in
  `lojas`.
- **Products read from census feeds:** 14.6 million, most from Mercado Shops (8.5 million), NuvemShop (3.1
  million), Vtex (1.2 million) and Shopify (1.0 million).
- **GPT pages:** 63,933 pages; 63,538 answer "yes, reliable", 4 answer no, 391 have no readable answer.

## Files

- `lojas.parquet`: 63,974 stores: domain, name, platform, HTML signs, products in the feed, SSL, Reclame Aqui status and score.
- `plataformas.parquet`: 13 platforms of the author's feed reader.
- `reclame_aqui.parquet`: the Reclame Aqui profile linked to each store.
- `reclame_aqui_candidatos.parquet`: every profile the search returned, with the one chosen.
- `textos_gpt.parquet`: 63,933 synthetic pages by GPT-3.5 (12 April 2023).
- `censo_2022.parquet`: 81,018 domains, declared platform, two online checks, feed, Mercado Shops id.
- `censo_2022_feeds.parquet`: feeds tested and products read.
- `feeds_importados.parquet`: 13,804 feeds imported into the author's crawler.

## How a store is structured

![One store as nested JSON](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/store-json.png)

One store, `estrela10.com.br`, with its rows from the other tables nested under it by `id_loja`: platform Linx, 5,178 products in the feed, a Let's Encrypt certificate, and the Reclame Aqui profile `estrela10` (RA1000, score 8.8, 866 complaints, 95.4% solved) chosen as the only candidate the search returned. Full record: [`docs/example-store.json`](https://github.com/CaiqueDourado/lojas-virtuais-brasil/blob/main/docs/example-store.json), built by [`scripts/make_json.py`](https://github.com/CaiqueDourado/lojas-virtuais-brasil/blob/main/scripts/make_json.py).

## How it was collected

![Sources and tables](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/flow.png)

What happened to each store in April 2023:

![Per store](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/flow-store.png)

Partners, contact lists, raw WHOIS, the CNPJ/CPF field of Reclame Aqui profiles and author meta tags were never exported. The data quality report lists every fix and every known limit, including how to check a Reclame Aqui match.

Methodology, data quality report, data dictionary (EN and PT), scripts and a sample: **https://github.com/CaiqueDourado/lojas-virtuais-brasil**

## Related

- [Catálogo de produtos do e-commerce brasileiro](https://www.kaggle.com/datasets/caiquedourado/catalogo-produtos-ecommerce-brasil)
- [Reviews de produtos (pt-BR)](https://www.kaggle.com/datasets/caiquedourado/reviews-produtos-ptbr)
- [BrCommerceKit](https://github.com/CaiqueDourado/BrCommerceKit): platform detection and feed reading

License: CC BY 4.0 for the compilation and derived columns; Reclame Aqui data from reclameaqui.com.br; GPT texts are synthetic. Version 1.0.0. Author: Caique Dourado.
