# Dicionário de dados: Lojas virtuais do Brasil: plataforma, Reclame Aqui e o censo de e-commerce de 2022

Gerado por `scripts/docs.py` a partir de `schema/columns.json`. Nulos e exemplos vêm da amostra em `sample/`.

## `lojas`

63.974 lojas virtuais brasileiras com nome confirmado (abril de 2023): plataforma, tamanho do catálogo, certificado SSL, resumo do Reclame Aqui.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id_loja` | integer | 0,0% | `49358` | Id da loja no banco do autor. Chave primária. |
| `dominio` | string | 0,0% | `alet.com.br` | Domínio sem www, em minúsculas. |
| `nome` | string | 0,0% | `Alet Store` | Nome da loja inferido da página (title e metatags), com entidades HTML e mojibake corrigidos. |
| `slug` | string | 0,0% | `aletstore` | Slug da página da loja no site Tudo Sobre Lojas, do autor. |
| `plataforma` | string | 14,2% | `Loja Integrada` | Plataforma de e-commerce, com grafias unificadas (Nuvem Shop e NuvemShop -> NuvemShop; Loja Integrada PRO -> Loja Integrada). Vazio quando não detectada. |
| `plataforma_original` | string | 14,2% | `Loja Integrada PRO` | Plataforma como o crawler gravou. |
| `sinais_no_html` | string | 32,4% | `Loja Integrada, Lynx` | Nomes de plataforma achados como texto no HTML da página (um dos três testes). 'Jet' costuma ser falso positivo (a substring 'jet'). |
| `protocolo` | string | 0,0% | `https` | http ou https. |
| `tld` | string | 0,0% | `.com.br` | Domínio de topo (.com.br, .com...). |
| `total_produtos` | integer | 71,6% | `0` | Produtos achados no feed da loja; vazio quando nenhum feed foi lido. |
| `titulo_pagina` | string | 34,8% | `Menskin` | Título da página inicial. |
| `og_site_name` | string | 62,2% | `Men.Skin` | Metatag og:site_name. |
| `certificado_dominio` | string | 16,6% | `pequenosecuriosos.com.br` | Domínio para o qual o certificado SSL foi emitido (pode ser outro: hospedagem compartilhada). |
| `certificado_emissor` | string | 16,6% | `Let's Encrypt` | Autoridade certificadora (Let's Encrypt, GlobalSign...). |
| `certificado_validade` | string | 16,6% | `2023-06-17` | Validade do certificado na coleta (abril de 2023). |
| `certificado_com_erro` | boolean | 0,0% | `false` | Verdadeiro quando a leitura do certificado falhou (sem HTTPS, timeout...). |
| `fontes_no_crawler` | integer | 0,0% | `0` | Quantas fontes (lojas) do crawler de produtos do autor apontam para o domínio; 0 = a loja não é uma delas. |
| `reclame_aqui_status` | string | 71,6% | `NO_INDEX` | Reputação no Reclame Aqui do perfil ligado: RA1000, GREAT, GOOD, REGULAR, BAD, NOT_RECOMMENDED, NO_INDEX (poucas reclamações), UNDER_REVIEW. Vazio: perfil não achado. |
| `reclame_aqui_nota` | float | 97,4% | `8.8` | Nota do Reclame Aqui (0-10) do perfil ligado. |
| `reclame_aqui_perfil` | string | 71,6% | `toy-store-brasil_745422` | Slug do perfil no Reclame Aqui (reclameaqui.com.br/empresa/<slug>). |
| `tem_texto_gpt` | boolean | 0,0% | `true` | Verdadeiro quando há página escrita pelo GPT sobre a loja (tabela textos_gpt). |

## `plataformas`

As 13 plataformas do leitor de feeds de produtos do autor.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id_plataforma` | integer | 0,0% | `7` | Id da plataforma no leitor de feeds do autor. |
| `nome` | string | 0,0% | `Magento` | Nome da plataforma. |

## `reclame_aqui`

Perfil(is) do Reclame Aqui ligados a cada loja: status, nota, reclamações, percentual resolvido.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id` | integer | 0,0% | `91837` | Id da linha. Chave primária. |
| `id_loja` | integer | 0,0% | `41426` | Loja (lojas.id_loja). |
| `nome` | string | 0,0% | `FullBox ` | Nome do perfil no Reclame Aqui. |
| `nome_fantasia` | string | 0,0% | `FullBox ` | Nome fantasia. |
| `razao_social` | string | 0,0% | `FullBox ` | Razão social como cadastrada no Reclame Aqui. |
| `shortname` | string | 0,0% | `fullbox` | Slug do perfil. |
| `url` | string | 9,2% | `http://spplotter.com.br` | Site cadastrado no perfil do Reclame Aqui (como a empresa digitou). |
| `logo` | string | 77,0% | `https://raichu-uploads.s3.amazonaws.c…` | URL do logo no Reclame Aqui. |
| `acronym` | string | 100,0% |  | Sigla. |
| `nota` | float | 88,8% | `8.8` | Nota 0-10 (vazia em NO_INDEX). |
| `reclamacoes` | integer | 0,0% | `0` | Quantidade de reclamações mostrada na busca. |
| `percentual_resolvido` | float | 88,8% | `90.9` | Percentual de reclamações resolvidas. |
| `status` | string | 0,0% | `NO_INDEX` | Status de reputação (ver lojas.reclame_aqui_status). |
| `segmento` | string | 100,0% |  | Segmento. |
| `ra_id` | string | 0,0% | `gsa8zb5iKIx5KeRO` | Id da empresa no Reclame Aqui. |
| `marcas` | string | 100,0% |  | Marcas listadas no perfil. |
| `nomes_anteriores` | string | 100,0% |  | Nomes anteriores. |
| `principal` | boolean | 0,0% | `true` | O perfil escolhido para a loja quando há mais de um. |

## `reclame_aqui_candidatos`

Todos os perfis que a busca do Reclame Aqui devolveu para cada loja, com o escolhido.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id` | integer | 0,0% | `223264` | Id da linha. Chave primária. |
| `id_loja` | integer | 0,0% | `44335` | Loja buscada (lojas.id_loja). |
| `nome` | string | 0,0% | `Detona Shop` | Nome do perfil devolvido pela busca. |
| `razao_social` | string | 0,0% | `Detona Shop` | Razão social. |
| `shortname` | string | 0,0% | `detona-shop` | Slug do perfil. |
| `url` | string | 9,9% | `http://diocollection.com` | Site cadastrado no perfil do Reclame Aqui (como a empresa digitou). |
| `nota` | float | 85,6% | `6.8` | Nota 0-10. |
| `reclamacoes` | integer | 0,0% | `10` | Quantidade de reclamações. |
| `status` | string | 0,0% | `NO_INDEX` | Status de reputação. |
| `segmento` | string | 100,0% |  | Segmento. |
| `ra_id` | string | 0,0% | `18795` | Id da empresa no Reclame Aqui. |
| `escolhido` | boolean | 0,0% | `true` | Verdadeiro quando este candidato virou o perfil da loja em reclame_aqui. |

## `textos_gpt`

63.933 páginas SINTÉTICAS 'A loja X é confiável?' escritas pelo GPT-3.5 em 12/04/2023. Não são fatos.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id` | integer | 0,0% | `1220902` | Id do post no site do autor. Chave primária. |
| `id_loja` | integer | 0,0% | `81234` | Loja (lojas.id_loja), ligada pelo nome. |
| `nome_loja` | string | 0,0% | `Camisetas Joia` | Nome da loja usado no prompt. |
| `titulo` | string | 0,0% | `A loja Camisetas Joia é confável? ✔️ …` | Título da página como publicado, com o erro 'confável'. |
| `meta_description` | string | 0,0% | `✔️ Camisetas Joia é Segura? ✔️ Centra…` | Meta description da página. |
| `texto` | string | 0,0% | `<h2>Introdução: História e Reputação …` | Texto HTML escrito pelo modelo. SINTÉTICO: diz que toda loja é confiável e inventa ano de fundação, cidade e reputação. |
| `data` | string | 0,0% | `2023-04-12` | Data da geração. |
| `modelo` | string | 0,0% | `gpt-3.5` | Modelo que escreveu o texto. |

## `censo_2022`

Censo de 2022 com 81.018 domínios de e-commerce brasileiros: plataforma, duas checagens de online, feed e id do Mercado Shops.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id` | integer | 0,0% | `50831` | Id da linha do censo. Chave primária. |
| `dominio` | string | 0,0% | `bluelov.com.br` | Domínio sem www. |
| `protocolo` | string | 0,0% | `https` | Protocolo da primeira checagem. |
| `plataforma` | string | 2,9% | `Loja Integrada` | Plataforma da lista de origem, com grafias unificadas. |
| `plataforma_verificada` | string | 100,0% |  | Plataforma confirmada pelas checagens, quando preenchida. |
| `online` | string | 0,0% | `OK` | Resultado da primeira checagem (OK, Erro, códigos de redirecionamento). |
| `online_msg` | string | 97,1% | `O nome remoto não pôde ser resolvido:…` | Mensagem de erro da primeira checagem. |
| `redirecionado_para` | string | 100,0% |  | Para onde o domínio redirecionou na primeira checagem. |
| `online_check_2` | string | 0,0% | `OK` | Resultado da segunda checagem. |
| `online_msg_check_2` | string | 97,1% | `O nome remoto não pôde ser resolvido:…` | Mensagem de erro da segunda checagem. |
| `redirecionado_para_check_2` | string | 100,0% |  | Redirecionamento na segunda checagem. |
| `url_feed` | string | 79,7% | `https://s3-sa-east-1.amazonaws.com/ti…` | URL(s) de feed de produtos achadas, separadas por vírgula. |
| `plataforma_feed` | string | 79,7% | `NuvemShop` | Plataforma indicada pelo caminho do feed. |
| `texto_plataforma` | string | 3,0% | `Não identificada` | Nome de plataforma achado no HTML. |
| `id_mercado_shops` | string | 95,6% | `5043218` | Id da loja no Mercado Shops extraído do HTML. |
| `id_loja` | integer | 31,6% | `41768` | Loja (lojas.id_loja) com o mesmo domínio, quando está entre as 63.974. |

## `censo_2022_feeds`

Feeds de produtos testados nos domínios do censo, com os produtos lidos.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id` | integer | 0,0% | `31176` | Id da linha. Chave primária. |
| `id_censo` | integer | 0,0% | `63072` | Domínio do censo (censo_2022.id). |
| `url` | string | 0,0% | `https://s3-sa-east-1.amazonaws.com/ti…` | URL do feed testada. |
| `plataformas_testadas` | string | 0,0% | `NuvemShop` | Caminhos de feed de plataforma testados para o domínio. |
| `produtos` | integer | 0,0% | `113` | Produtos lidos do feed. |
| `paginas` | integer | 0,0% | `0` | Páginas lidas. |
| `checado` | boolean | 0,0% | `true` | Feed foi checado. |
| `status` | string | 0,0% | `sucesso` | sucesso ou erro. |
| `erro` | string | 77,5% | `Elemento raiz inexistente.` | Mensagem de erro (primeiros 400 caracteres). |

## `feeds_importados`

13.804 feeds de lojas importados no crawler de produtos do autor, por plataforma.

| Coluna | Tipo | Nulos | Exemplo | Descrição |
|---|---|---|---|---|
| `id` | integer | 0,0% | `6651` | Id da linha. Chave primária. |
| `plataforma` | string | 0,0% | `NuvemShop` | Plataforma do feed. |
| `id_plataforma` | integer | 0,0% | `3` | plataformas.id_plataforma. |
| `dominio` | string | 0,0% | `fantibaby.com.br` | Domínio da loja. |
| `url` | string | 0,0% | `https://s3-sa-east-1.amazonaws.com/ti…` | URL do feed. |
| `produtos` | integer | 0,0% | `132` | Produtos no feed na importação. |
| `id_loja` | integer | 4,9% | `51344` | Loja (lojas.id_loja) com o mesmo domínio, quando existe. |
