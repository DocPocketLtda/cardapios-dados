# cardapios-dados

Base de restaurantes e links de cardápio do app **Cardápios** (iOS), atualizada sozinha pelo GitHub Actions e publicada no GitHub Pages:

- **Índice:** `https://docpocketltda.github.io/cardapios-dados/index.json`
- **Fase 0 (o que o app usa hoje):** `https://docpocketltda.github.io/cardapios-dados/sp/grande-sp.csv`

A arquitetura segue o relatório `output/dados/pesquisa-base-restaurantes.md` do repositório do app (seções 3 e 4).

## Como funciona

```
[Planilha do Google] ──┐
[Overture Maps (S3)] ──┼─► merge (dedupe, ids congelados, blacklist) ─► check-links ─► repair-links ─► publish ─► Pages
[OSM: TODO]          ──┘                                              (cache incremental)                (trava de regressão)
```

1. **`fetch-sheet`**: baixa o CSV da planilha (camada manual). Uma resposta HTML conta como falha.
2. **`fetch-overture --region sp-estado`**: descobre a release mais recente listando `s3://overturemaps-us-west-2/release/` e lê o Places com DuckDB, sem credencial. Filtros: `basic_category` de restaurante/café/lanchonete, sem sorveteria, doceria, bar etc. (`config/regions.json`), país BR, UF SP, bbox do estado, e confiança ≥ 0,8 (ou ≥ 0,7 com site). O comando confere o schema e falha sem publicar se as colunas mudarem. O Parquet fica em `work/`, fora do git.
3. **`merge`**: casa cada lugar do Overture com a planilha. O bloqueio usa uma grade de ~1 km com raio de 1,2 km quando a coordenada da planilha tem 2 casas decimais e de 300 m quando é precisa. Um par casa quando o nome normalizado é parecido (Jaro-Winkler ≥ 0,88 ou token-set ≥ 0,8) e há um segundo sinal: telefone igual, domínio próprio igual, mesmo número na mesma rua ou distância muito pequena.
   - **A planilha ganha em todo campo que preenche.** O Overture só preenche campos vazios: telefone, site, `cuisine` (quando o nome não diz nada) e coordenada precisa no lugar da aproximada, mas só com casamento forte.
   - `name` e `address` das linhas da planilha ficam **idênticos byte a byte**. O `Menu.id` do app é `name|address`, e os favoritos e o diário dependem dele.
   - Um restaurante da planilha que só tem linhas `available=FALSE` vira **blacklist**: o lugar do Overture que casa com ele não entra. Para desligar isso, use `merge.sheet_false_is_blacklist`.
   - Os lugares novos ganham `name|address` gerados uma vez e **congelados em `data/ids.csv`** na primeira publicação. Se a fonte reescrever o endereço depois, o id não muda.
   - Colunas opcionais da planilha: `id_fonte`, que amarra a linha a um registro (`ovt:<id>`), e `travar_link=TRUE`, que impede o validador de mexer no link.
4. **`check-links`**: checagem incremental com cache em `data/links-cache.csv`, que também serve de fila.
   - Cortesia: User-Agent `CardapiosBot/1.0 (+repo)`, respeito ao `robots.txt` (com `*` e `$`), 1 requisição a cada 2 s por domínio (3 s no iFood), GET limitado a 300 KB, HEAD para PDF e timeout de 12 s.
   - Classificação: estacionado (texto ou redirect para revendedor), soft 404 (título ou `<h1>` "não encontrada", título genérico da plataforma, ou página igual à de um caminho aleatório do mesmo host), redirect da loja para a home, e reconhecimento de plataformas (goomer, anota.ai, menudino, cardapioweb, loja do iFood, whatsmenu, instadelivery, pedir.delivery, livemenu, ola.click...).
   - **401/403/429 e bloqueio por robots = `incerto`, nunca quebrado.** Uma loja do iFood com 403 conta como válida.
   - **Quebrado só depois de falhas em dias diferentes:** 2 dias para 404, DNS, estacionado, soft 404 ou redirect; 3 dias para 5xx ou timeout. Um ok zera a contagem.
   - Rechecagem: `ok` a cada 30 dias, `falhando` no dia seguinte, `incerto` a cada 7 dias. A ordem é falhando, depois novos (planilha antes do Overture), depois vencidos.
5. **`repair-links`**: procura substituto para link quebrado na ordem do relatório (3.2). Primeiro, link de plataforma em outra fonte, na home do site ou numa página Linktree/beacons. Depois, página "cardápio/menu" ou PDF achado no HTML, ou `/cardapio`, `/menu` e `/cardapio.pdf`. Depois, a home do site, se estiver no ar. Por último, rede social (só para linhas da planilha). Lugares novos que só têm a home também recebem um link de cardápio melhor. O resultado fica em `data/repairs.csv`.
6. **`publish`**: gera um CSV por região no formato do app, `index.json` (id, nome, fase, `app_default`, bbox sem os 1% de pontos extremos, centro, `cells`, url, linhas, restaurantes, bytes, sha256, updated_at). `cells` lista as células de 0,1° (~11 km, chave `"floor(lat*10),floor(lon*10)"`) que têm restaurantes da região. O app escolhe as regiões cujas células tocam a célula do usuário ou uma vizinha. Sem localização, ou fora da cobertura, usa as regiões com `app_default` (capital e metropolitana)., `index.html` e as atribuições.
   - Linhas da planilha saem, salvo link **confirmado** quebrado e sem substituto. Essas linhas aparecem no relatório para você corrigir a planilha.
   - Lugares novos só saem com **link de cardápio validado ou site válido**. Rede social, encurtador e link ainda não verificado não bastam.
   - **Trava de regressão:** se uma região com 50 linhas ou mais perder mais de 20%, nada é publicado e o comando sai com código 2. O workflow abre uma issue. Para publicar mesmo assim, use `--force` (no workflow, a opção `force_publish`).
   - O relatório de diff vai para `reports/ultimo-build.md` e para o resumo do Actions.

### Regiões (estado de SP)

| Arquivo | Conteúdo | Fase |
|---|---|---|
| `sp/grande-sp.csv` | as linhas disponíveis da planilha, com links validados e reparados, nas mesmas colunas e na mesma ordem. **Substitui direto** o CSV da planilha que o app baixa hoje | 0 |
| `sp/capital.csv` | município de São Paulo (planilha + Overture) | 1 |
| `sp/metropolitana.csv` | os outros 38 municípios da RMSP | 1 |
| `sp/campinas.csv` | os 20 municípios da RM de Campinas | 1 |
| `sp/litoral.csv` | Baixada Santista (9) e Litoral Norte (4) | 1 |
| `sp/jundiai.csv`, `sp/sorocaba.csv`, `sp/vale-do-paraiba.csv`, `sp/piracicaba.csv`, `sp/ribeirao-preto.csv`, `sp/araraquara.csv`, `sp/bauru.csv`, `sp/marilia.csv`, `sp/presidente-prudente.csv`, `sp/aracatuba.csv`, `sp/sao-jose-do-rio-preto.csv`, `sp/vale-do-ribeira.csv` | o resto do estado (o arquivo `default` com `split`), cada restaurante no polo mais perto, parecido com as regiões intermediárias do IBGE | 1 |

A região sai do município do endereço, com a mesma regra do `AddressParser` do app, ou da `locality` do Overture. Se o município do endereço não está em nenhuma lista, uma linha do Overture usa a coluna `city` (a da planilha às vezes está errada). O que sobra vai para o polo do `split` mais perto pelas coordenadas. A divisão mantém cada arquivo pequeno para o app baixar só a região do usuário. As capitais (fase 2) entram como novas `areas` em `config/regions.json`, com bbox, UF e `overture.localities` (há um exemplo em `future_areas_example`), sem mudar código.

Colunas: `name, logo, address, latitude, longitude, city, state, country, available, phone, email, website, type, menu_link, cuisine, neighborhood, opening_hours`, mais as informativas `id_fonte, fonte, confianca, link_status, link_verificado_em`, que o app ignora. Lugares novos com site sem sinal de cardápio saem com `type=Site`.

## Remote Config (fase 0)

No Firebase Remote Config do app, troque `sourceURL` para:

```
https://docpocketltda.github.io/cardapios-dados/sp/grande-sp.csv
```

O app já aceita CSV, ignora colunas extras e cai no `defaultSourceURL` (a planilha) se o Pages falhar. A partir da 1.1.0, o app lê o `index.json` (chave `indexURL` do Remote Config) e baixa as regiões da fase 1. Versões antigas continuam no `sourceURL`.

## Rodar localmente

Requer Python 3.12 ou mais novo. Só o `fetch-overture` precisa do `duckdb`.

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m cardapios_dados fetch-sheet
.venv/bin/python -m cardapios_dados fetch-overture --region sp-estado     # ~3 min, ~65 mil lugares
.venv/bin/python -m cardapios_dados merge --region sp-estado              # ~2 min
.venv/bin/python -m cardapios_dados check-links --limit 300               # amostra; sem --limit verifica tudo o que está vencido
.venv/bin/python -m cardapios_dados check-links --origin overture --limit 300
.venv/bin/python -m cardapios_dados repair-links --limit 300
.venv/bin/python -m cardapios_dados publish                               # public/ + reports/ultimo-build.md
python3 -m unittest discover -s tests                                      # testes
```

`all` roda tudo em sequência. Uma checagem completa de links (~25 mil URLs) leva mais de uma hora, então deixe isso para o Actions.

## GitHub Actions

- **`build.yml`**: toda segunda às 06:17 UTC e também à mão (`workflow_dispatch`). Roda testes, coleta, merge, links (até 90 min), reparo e publicação. Commita `data/` e `reports/`, mesmo quando a trava recusa a publicação, e faz o deploy de `public/` com `actions/deploy-pages`. Se falhar, abre uma issue.
- **`links.yml`**: todo dia às 09:43 UTC. Faz a checagem incremental do cache (25 min) e o commit do cache. Também falha e abre uma issue se o último `build` com sucesso tiver mais de 14 dias.
- Os dois usam o mesmo grupo de `concurrency`, então nunca fazem push ao mesmo tempo.
- **Regra dos 60 dias:** em repositório público, o GitHub **desativa workflows agendados depois de 60 dias sem atividade no repositório**. Os commits diários de cache contam como atividade, e o alerta de 14 dias avisa antes. Se os workflows forem desativados, reative em Actions > workflow > "Enable workflow".
- O primeiro build verifica primeiro os links da planilha. Os ~23 mil links do Overture vão sendo validados nos dias seguintes, então os arquivos da fase 1 crescem a cada semana.

## Limitações conhecidas

- **OSM ainda não entra** (`website:menu`, horário, culinária). O gancho e o plano estão em `cardapios_dados/osm.py` (Geofabrik + osmium). Quando entrar, os CSVs passam a ser ODbL.
- Plataformas SPA (goomer, anota.ai) devolvem a mesma página para lojas que existem e que não existem. Nesses casos, sem redirect ou título próprio, o link conta como ok.
- Muitos sites bloqueiam robôs (Cloudflare, robots.txt `Disallow: /`, inclusive o Linktree). Eles ficam `incerto`: continuam publicados se vêm da planilha e ficam de fora se são lugares novos.
- Os logos ainda não são buscados (o `cmd_logos` do repositório do app pode ser portado).

## Licenças

Código: MIT (`LICENSE`). Dados: veja `LICENSE-DATA.md` e `ATTRIBUTION.md`.
