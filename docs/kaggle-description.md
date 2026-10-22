**Lojas virtuais do Brasil**: 63.974 lojas virtuais brasileiras com plataforma, certificado SSL e reputação no Reclame Aqui, o censo de e-commerce de 2022 e 63.933 páginas escritas pelo GPT-3.5. **Brazilian online stores**: platform, SSL, Reclame Aqui and the 2022 e-commerce census.

![Brazilian online stores](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/cover.png)

63,974 Brazilian online stores found and checked in April 2023, with three tests of the e-commerce platform (declared, names in the HTML, a feed path that answered), catalog size from the feed, SSL certificate and the Reclame Aqui profile chosen among the search results. With them, the 2022 census of 81,018 e-commerce domains and their product feeds.

![Stores per platform](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/platforms.png)

**About `textos_gpt`.** The author's site had one page per store, "A loja X é confiável?", written by GPT-3.5 from the store name alone. 63,538 of the 63,542 pages with a readable answer say the store is reliable, including all 360 about stores Reclame Aqui does not recommend, and most invent a founding year, a city or a reputation. They are published as a record of model output next to real reputation data, **not as facts about the stores**.

![GPT x Reclame Aqui](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/gpt-vs-reclame-aqui.png)

## Files

- `lojas.parquet`: 63,974 stores: domain, name, platform, HTML signs, products in the feed, SSL, Reclame Aqui status and score.
- `plataformas.parquet`: 13 platforms of the author's feed reader.
- `reclame_aqui.parquet`: the Reclame Aqui profile linked to each store.
- `reclame_aqui_candidatos.parquet`: every profile the search returned, with the one chosen.
- `textos_gpt.parquet`: 63,933 synthetic pages by GPT-3.5 (12 April 2023).
- `censo_2022.parquet`: 81,018 domains, declared platform, two online checks, feed, Mercado Shops id.
- `censo_2022_feeds.parquet`: feeds tested and products read.
- `feeds_importados.parquet`: 13,804 feeds imported into the author's crawler.

## How it was collected

![Sources and tables](https://raw.githubusercontent.com/CaiqueDourado/lojas-virtuais-brasil/main/docs/img/flow.png)

Partners, contact lists, raw WHOIS, the CNPJ/CPF field of Reclame Aqui profiles and author meta tags were never exported. The data quality report lists every fix and every known limit, including how to check a Reclame Aqui match.

Methodology, data quality report, data dictionary (EN and PT), scripts and a sample: **https://github.com/CaiqueDourado/lojas-virtuais-brasil**

## Related

- [Catálogo de produtos do e-commerce brasileiro](https://www.kaggle.com/datasets/caiquedourado/catalogo-produtos-ecommerce-brasil)
- [Reviews de produtos (pt-BR)](https://www.kaggle.com/datasets/caiquedourado/reviews-produtos-ptbr)
- [BrCommerceKit](https://github.com/CaiqueDourado/BrCommerceKit): platform detection and feed reading

License: CC BY 4.0 for the compilation and derived columns; Reclame Aqui data from reclameaqui.com.br; GPT texts are synthetic. Version 1.0.0. Author: Caique Dourado.
