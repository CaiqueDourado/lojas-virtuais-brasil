# Lojas virtuais do Brasil

[![validate](https://github.com/CaiqueDourado/lojas-virtuais-brasil/actions/workflows/validate.yml/badge.svg)](https://github.com/CaiqueDourado/lojas-virtuais-brasil/actions/workflows/validate.yml)
[![Dados: CC BY 4.0](https://img.shields.io/badge/dados-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA.md)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-blue.svg)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-dataset-20BEFF.svg)](https://www.kaggle.com/datasets/caiquedourado/lojas-virtuais-brasil)

[Read in English](README.md)

![Lojas virtuais do Brasil](docs/img/cover.pt-BR.png)

São **63.974 lojas virtuais brasileiras**, encontradas e checadas em abril de 2023. De cada uma, a base traz
domínio, plataforma de e-commerce, tamanho do catálogo, certificado SSL e reputação no Reclame Aqui.

A base também traz:

- o **censo de e-commerce de 2022**, com 81.018 domínios e os feeds de produtos deles;
- as **63.933 páginas que o GPT-3.5 escreveu** sobre as lojas. Elas registram o que um modelo de linguagem diz
  quando não sabe nada sobre o assunto.

| Arquivo | Linhas | O que tem |
|---|---:|---|
| `lojas` | 63.974 | domínio, nome, plataforma, sinais da plataforma no HTML, produtos no feed, SSL, status e nota no Reclame Aqui |
| `plataformas` | 13 | plataformas do leitor de feeds de produtos do autor |
| `reclame_aqui` | 19.335 | o perfil do Reclame Aqui ligado a cada loja: status, nota, reclamações, percentual resolvido |
| `reclame_aqui_candidatos` | 217.507 | todos os perfis que a busca do Reclame Aqui devolveu, com o escolhido |
| `textos_gpt` | 63.933 | páginas "A loja X é confiável?" do GPT-3.5, de 12/04/2023: **sintéticas, não são fatos** |
| `censo_2022` | 81.018 | censo de 2022: plataforma declarada, duas checagens de online, URL do feed, id do Mercado Shops |
| `censo_2022_feeds` | 20.284 | feeds testados nos domínios do censo e produtos lidos |
| `feeds_importados` | 13.804 | feeds de lojas importados no crawler de produtos do autor |

Os arquivos completos (Parquet) estão no [Kaggle](https://www.kaggle.com/datasets/caiquedourado/lojas-virtuais-brasil).
Este repositório tem os scripts, a documentação e a pasta `sample/`, com todas as linhas de 500 lojas sorteadas
e amostras do censo e dos feeds.

## Plataformas

![Lojas por plataforma](docs/img/platforms.pt-BR.png)

WooCommerce, Loja Integrada e NuvemShop rodam mais da metade das lojas com plataforma conhecida.

A plataforma foi lida de três jeitos:

1. a declarada nas listas de origem;
2. nomes de plataforma achados no HTML (`sinais_no_html`);
3. um caminho de feed conhecido que respondeu (`fb_catalog.xml` da NuvemShop, `products.json` da Shopify,
   `/darwin/rss/{id}/gshopping` do Mercado Shops…).

Esses testes viraram o `PlatformDetector` da [BrCommerceKit](https://github.com/CaiqueDourado/BrCommerceKit).

## Reclame Aqui

Para cada loja com página no site do autor, um navegador buscou o nome dela no Reclame Aqui, o principal site
de reclamações de consumidores do Brasil, e guardou todos os perfis devolvidos. Regras de casamento por nome e
site escolheram o perfil da loja.

18.676 lojas ganharam um perfil, mas 17.320 delas são NO_INDEX: pequenas demais para ter nota. Nas 1.337 lojas
com nota, a média vai de 3,98 (NOT_RECOMMENDED) a 8,95 (RA1000).

O casamento pode errar em nomes comuns. O [relatório de qualidade](docs/data-quality.md) explica como conferir.

## O que o GPT disse sobre elas

O site Tudo Sobre Lojas, do autor ([Web Archive](https://web.archive.org/web/20250618081809/https://tudosobrelojas.com/a-loja-saboreat-e-confavel-tudo-sobre-a-loja-saboreat/)),
tinha uma página por loja. Cada página foi escrita pelo GPT-3.5 só a partir do nome da loja, com os
intertítulos "A loja X é confiável?" e "A loja X é segura?".

Das 63.542 páginas com resposta legível, 63.538 dizem que sim. Isso inclui todas as 1.320 páginas sobre lojas
avaliadas pelo Reclame Aqui, até as 360 que ele não recomenda. A maioria inventa ano de fundação, cidade, percentual de avaliações
positivas ou reputação no Reclame Aqui.

Os textos estão publicados porque mostram, em escala e ao lado de dados reais de reputação, como um modelo
preenche uma lacuna com texto confiante. Use a tabela `textos_gpt` para isso, nunca como informação sobre uma
loja.

![GPT x Reclame Aqui](docs/img/gpt-vs-reclame-aqui.pt-BR.png)

## Como usar

```python
import pandas as pd

lojas = pd.read_csv("sample/lojas_sample.csv")
lojas.plataforma.value_counts().head(10)

# lojas com nota e sua plataforma
lojas.dropna(subset=["reclame_aqui_nota"]).groupby("plataforma").reclame_aqui_nota.agg(["count", "mean"])
```

```sql
-- DuckDB, arquivos completos do Kaggle: o que o GPT respondeu sobre lojas que o Reclame Aqui não recomenda
SELECT l.nome, l.reclame_aqui_nota, substr(t.texto, strpos(t.texto, 'confi'), 120) AS resposta
FROM 'lojas.parquet' l JOIN 'textos_gpt.parquet' t USING (id_loja)
WHERE l.reclame_aqui_status = 'NOT_RECOMMENDED' LIMIT 10;
```

Cada coluna está no [dicionário de dados](docs/data-dictionary.pt-BR.md) ([EN](docs/data-dictionary.md)). Como a
base foi montada está na [metodologia](docs/methodology.md), em inglês.

## Privacidade

Publicado: o que a loja mostra a qualquer pessoa (domínio, nome, plataforma, certificado) e a reputação pública
das empresas.

Não publicado:

- sócios das empresas;
- listas de contato;
- WHOIS bruto;
- o campo de CNPJ/CPF dos perfis do Reclame Aqui (o MEI usa o próprio CPF);
- as metatags de autor e copyright, que costumam trazer nome de pessoa.

Donos de loja podem pedir a remoção abrindo uma issue.

## Estrutura do repositório

```text
sample/        todas as linhas de 500 lojas sorteadas; amostras do censo e dos feeds (CSV)
schema/        definição das colunas e metadados
scripts/       exportar_lojas.py (SQL Server -> Parquet), perfil_lojas.py, perfil_textos.py, build_lojas.py,
               validate.py, make_figures.py, make_cover.py, docs.py
notebooks/     eda.ipynb
docs/          metodologia, qualidade, dicionário de dados, descrição do Kaggle, imagens
kaggle/        dataset-metadata.json
stats.json     contagens de cada etapa do build
```

## Relacionados

- [BrCommerceKit](https://github.com/CaiqueDourado/BrCommerceKit): detecção de plataforma e leitura de feeds de lojas brasileiras.
- [DomainCheck](https://github.com/CaiqueDourado/DomainCheck): se um domínio está livre (DNS, Registro.br, WHOIS).
- [catalogo-produtos-ecommerce-brasil](https://github.com/CaiqueDourado/catalogo-produtos-ecommerce-brasil): produtos e preços coletados de 17.899 lojas brasileiras.
- [reviews-produtos-ptbr](https://github.com/CaiqueDourado/reviews-produtos-ptbr): 2,87 milhões de reviews de produtos de lojas brasileiras.

## Licença

A compilação e as colunas derivadas estão em [CC BY 4.0](LICENSE-DATA.md). Código: [MIT](LICENSE).

## Autor

**Caique Dourado**: 20 anos construindo crawlers, pipelines de dados e SEO programático em .NET e SQL Server. Mais em [github.com/CaiqueDourado](https://github.com/CaiqueDourado).
