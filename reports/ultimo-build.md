# Relatório do build (23/11/2026 18:53 UTC)

## ⚠️ Publicação recusada (trava de regressão)

- `sp/capital`: 6775 → 2396 linhas (-65%)
- `sp/metropolitana`: 2637 → 315 linhas (-88%)
- `sp/campinas`: 1480 → 81 linhas (-95%)
- `sp/litoral`: 875 → 36 linhas (-96%)
- `sp/jundiai`: 685 → 40 linhas (-94%)
- `sp/sorocaba`: 676 → 38 linhas (-94%)
- `sp/vale-do-paraiba`: 856 → 51 linhas (-94%)
- `sp/piracicaba`: 725 → 42 linhas (-94%)
- `sp/ribeirao-preto`: 745 → 41 linhas (-94%)
- `sp/araraquara`: 418 → 24 linhas (-94%)
- `sp/bauru`: 417 → 20 linhas (-95%)
- `sp/marilia`: 294 → 11 linhas (-96%)
- `sp/presidente-prudente`: 150 → 6 linhas (-96%)
- `sp/aracatuba`: 241 → 5 linhas (-98%)
- `sp/sao-jose-do-rio-preto`: 464 → 27 linhas (-94%)
- `sp/vale-do-ribeira`: 137 → 8 linhas (-94%)

## Regiões

| Região | Linhas antes | Linhas agora | Restaurantes | Entraram | Saíram | Tamanho |
|---|---:|---:|---:|---:|---:|---:|
| `sp/grande-sp` | 2460 | 2434 | 2430 | 5 | 31 | 719 KB |
| `sp/capital` | 6775 | 2396 | 2392 | 10 | 4379 | 708 KB |
| `sp/metropolitana` | 2637 | 315 | 315 | 2 | 2318 | 94 KB |
| `sp/campinas` | 1480 | 81 | 81 | 2 | 1398 | 24 KB |
| `sp/litoral` | 875 | 36 | 36 | 0 | 837 | 11 KB |
| `sp/jundiai` | 685 | 40 | 40 | 0 | 644 | 12 KB |
| `sp/sorocaba` | 676 | 38 | 38 | 0 | 630 | 11 KB |
| `sp/vale-do-paraiba` | 856 | 51 | 51 | 1 | 801 | 16 KB |
| `sp/piracicaba` | 725 | 42 | 42 | 1 | 680 | 13 KB |
| `sp/ribeirao-preto` | 745 | 41 | 41 | 1 | 699 | 12 KB |
| `sp/araraquara` | 418 | 24 | 24 | 0 | 391 | 8 KB |
| `sp/bauru` | 417 | 20 | 20 | 0 | 394 | 6 KB |
| `sp/marilia` | 294 | 11 | 11 | 0 | 280 | 3 KB |
| `sp/presidente-prudente` | 150 | 6 | 6 | 0 | 144 | 2 KB |
| `sp/aracatuba` | 241 | 5 | 5 | 1 | 237 | 2 KB |
| `sp/sao-jose-do-rio-preto` | 464 | 27 | 27 | 0 | 434 | 8 KB |
| `sp/vale-do-ribeira` | 137 | 8 | 8 | 0 | 129 | 2 KB |

## Links

| Origem:status | Linhas |
|---|---:|
| overture:incerto | 216 |
| overture:ok | 658 |
| overture:omitidas | 2540 |
| overture:pendente | 1841 |
| overture:quebrado | 532 |
| overture:reparadas | 171 |
| planilha:incerto | 137 |
| planilha:ok | 2273 |
| planilha:omitidas | 44 |
| planilha:pendente | 24 |
| planilha:quebrado | 44 |
| planilha:reparadas | 75 |

## Merge

```
sheet_rows: 6841
sheet_available_rows: 2478
sheet_restaurants: 2474
blacklisted_keys: 4363
sp-estado: {'overture_release': '2026-11-18.0', 'overture_records': 3439, 'after_internal_dedupe': 3435, 'matched_sheet': 62, 'duplicates_absorbed': 0, 'blacklisted': 126, 'new_places': 3247}
```

## Linhas da planilha fora da publicação por link quebrado (44)

Corrija o `menu_link` na planilha ou marque `travar_link=TRUE` se o link estiver certo.

| Linha | Nome | Link |
|---:|---|---|
| 219 | Restaurante China Imperial | http://chinaimperial.com.br/ |
| 249 | Cuordicrema Adolfo Tabacow | http://cuordicrema.com/ |
| 366 | Garage Burger | http://garageburger.com.br/ |
| 396 | Hirota Food Express | http://hirotafoodexpress.com.br/lojas |
| 571 | Mimo Restaurante | http://mimorestaurante.com.br/ |
| 763 | Restaurante Angor | http://restauranteangor.ulcraft.com/ |
| 997 | Subway Perdizes | http://w.subway.com/pt-BR |
| 1089 | Allez Allez | http://www.allezallez.com.br/ |
| 1209 | Baiao Cozinha Nordestina | http://www.baiaocozinhanordestina.com.br/ |
| 1355 | Betones Bbq - Pinheiros | http://www.betonesbbq.com.br/ |
| 1438 | Boragó Jardins | http://www.borago.com.br/ |
| 1715 | Casa Do Churrasqueiro | http://www.casadochurrasqueiro.com/ |
| 1795 | Cervejaria Madalena | http://www.cervejamadalena.com/ |
| 1842 | Chiquinho Sorvetes | http://www.chiquinho.com.br/ |
| 1940 | Costela & Cia | http://www.costelaecia.com.br/ |
| 1970 | Cuordicrema | http://www.cuordicrema.com/ |
| 1971 | Cuordicrema | http://www.cuordicrema.com/ |
| 1972 | Cuor di Crema | http://www.cuordicrema.com/loja/tatuape/ |
| 2024 | Dinner In The Sky, Sao Paulo | http://www.dinnerinthesky.com.br/ |
| 3150 | Fitó | http://www.fitocozinha.com.br/ |
| 3175 | Fortunato Bar e Gastronomia | http://www.fortunatobar.com.br/ |
| 3248 | Osteria Generale | http://www.generale.com.br/ |
| 3366 | Hajime Sushi | http://www.hajimesushi.com.br/ |
| 3391 | Hidden by 2nd Floor | http://www.hiddenby2ndfloor.com/contato |
| 3578 | Jazz Resto & Burgueria | http://www.jazzrestaurante.com.br/ |
| 3897 | Mandacaru Cachaçaria | http://www.mandacarucachacaria.com.br/ |
| 3964 | Masaki Sushi | http://www.masaki.com.br/ |
| 4127 | Restaurante Nação Nordestina | http://www.nacaonordestina.com.br/ |
| 4216 | O Burguer | http://www.oburguer.com.br/ |
| 4360 | Paribar | http://www.paribar.com.br/ |
| 4470 | Pizza Crek | http://www.pizzacrek.com.br/ |
| 4471 | Pizza Crek | http://www.pizzacrek.com.br/ |
| 4566 | Tia Bela | http://www.pizzariatiabela.com.br/ |
| 4619 | Preta pitanga | http://www.pretapitanga.com.br/ |
| 4948 | Sabor Do Norteste | http://www.sabordonordeste.com.br/ |
| 5090 | Restaurante Sinhá Gomide | http://www.sinhagomide.com.br/ |
| 5125 | Solopasta Delivery | http://www.solopasta.com.br/ |
| 5267 | Taça Cheia | http://www.tacacheia.com/ |
| 5293 | TATÁ Sushi | http://www.tatasushi.com.br/ |
| 5482 | Vegas Burguer Beer | http://www.vegasburguerbeer.com.br/ |
| 5690 | Coracao Mineiro | https://coracaomineiro.com.br/ |
| 5772 | Piccini Cucina | https://restaurantepiccini.com/ |
| 5782 | Cervejaria Rivas Brewing Co | https://rivasbrewing.com.br/ |
| 6830 | Yug Sushi | https://eatyug.com.br/wp-content/uploads/2026/06/yug-menu-online.pdf |

## Links trocados automaticamente (246)

| Nome | Antes | Depois | Como |
|---|---|---|---|
| VASTO HADDOCK LOBO | https://cardapio.cocobambu.com/cardapio/237/5bda66ed-9038-420e-a30f-4a99e3d27cad | https://www.vastorestaurante.com/ | site |
| VASTO HADDOCK LOBO | https://cardapio.cocobambu.com/cardapio/237/c436dfc4-fded-4690-96a4-b23e8c5eea0b | https://www.vastorestaurante.com/ | site |
| VASTO HADDOCK LOBO | https://cardapio.cocobambu.com/cardapio/237/53e40101-dcce-4a28-a9cf-f4f73c96b790 | https://www.vastorestaurante.com/ | site |
| Coco bambu - JK | https://cardapio.cocobambu.com/cardapio/40/fbf0552b-4d08-4fb9-b22a-88c627acd1f3 | https://cocobambu.com/ | site |
| Coco bambu - JK | https://cardapio.cocobambu.com/cardapio/40/2da73d36-f894-4980-9d30-6366b7ae47cf | https://cocobambu.com/ | site |
| Coco bambu - JK | https://cardapio.cocobambu.com/cardapio/40/7c03b71b-fb5d-48e3-b495-4e61a8b22812 | https://cocobambu.com/ | site |
| Bullguer | http://bullguer.com/berrini/ | https://bullguer.com/cardapio | pagina-cardapio |
| Burger Lab Experience Itaim | http://burgerlab.com.br/experience | http://burgerlab.com.br/ | site |
| Forneria Capannone | http://capannone.com.br/ | https://www.facebook.com/123275121114732 | rede social |
| Fry's | http://centernorte.com.br/gourmet.asp | http://centernorte.com.br/cardapio.pdf | pagina-cardapio |
| Coffee and Co. | http://coffeeandco.com.br/ | https://fillmorebr.com/menu.pdf | pagina-cardapio |
| Dalva E Dito | https://dalvaedito.com.br/wp-content/uploads/2025/05/cardapio-mobile-dalva-dito.pdf | https://dalvaedito.com.br/wp-content/uploads/2026/11/cardapio-ptbr.pdf | pagina-cardapio |
| Casa Garabed Esfihas Especiais | http://dire.to/garabed | https://www.facebook.com/116473104807058 | rede social |
| Frangaria | http://frangaria.com.br/frangaria.php | http://frangaria.com.br/ | site |
| Lamen The Bowl | http://lamenthebowl.com/ | https://www.facebook.com/104497068513887 | rede social |
| Mocotó | https://mocoto.com.br/wp-content/uploads/Cardapio-Mocoto-Vila-Medeiros.pdf | https://mocoto.com.br/wp-content/uploads/2020/05/Menu-Pra-Viagem.pdf | pagina-cardapio |
| Sorry Mama Pizza | http://sorrymama.com.br/ | https://www.facebook.com/110624700788430 | rede social |
| Subway | http://w.subway.com/ | https://www.twitter.com/subwaybrasil | rede social |
| Água Doce Cachaçaria | http://www.aguadoce.com.br/nossas-casas-agua-doce/guarulhos/ | https://www.aguadoce.com.br/cardapio.html | pagina-cardapio |
| Bar do Juarez - Itaim | https://www.bardojuarez.com.br/cardapio | https://www.bardojuarez.com.br/cardapio.html | pagina-cardapio |
| Casa Bauducco | http://www.bauducco.com.br/casabauducco | http://www.bauducco.com.br/cardapio.pdf | pagina-cardapio |
| Casa Bauducco Shopping Morumbi | http://www.bauducco.com.br/casabauducco | http://www.bauducco.com.br/cardapio.pdf | pagina-cardapio |
| Blooming Burger | http://www.bloomingburger.com.br/ | https://www.facebook.com/207134085985932 | rede social |
| Boteco São Bento | https://www.dguests.com.br/cardapio/saobentovilamadalena | https://www.dguests.com.br/cardapio.pdf | pagina-cardapio |
| By Koji | https://bykojirestaurante.com.br/wp-content/uploads/2023/03/cardapio_koji_morumbi.pdf | https://bykojirestaurante.com.br/menu | pagina-cardapio |
| Natural Das Anas | http://www.cachoeiratropical.com.br/site2/ | http://www.cachoeiratropical.com.br/ | site |
| Casa Porteña Patio Higienópolis Shopping Mall | http://www.casaportena.com.br/ | https://www.facebook.com/107796204100481 | rede social |
| Casa Rios Restaurante | https://www.casariosrestaurante.com.br/menu | https://www.casariosrestaurante.com.br/cardapio/ | pagina-cardapio |
| Axé | http://www.centernorte.com.br/alimentacao/axe | http://www.centernorte.com.br/cardapio.pdf | pagina-cardapio |
| China In Box | http://www.chinainbox.com.br/cep/ | http://www.chinainbox.com.br/cardapio.pdf | pagina-cardapio |
| China in Box | http://www.chinainbox.com.br/lojasdetalhe/131 | http://www.chinainbox.com.br/cardapio.pdf | pagina-cardapio |
| China in Box - Higienopolis | http://www.chinainbox.com.br/lojasdetalhe/34 | http://www.chinainbox.com.br/cardapio.pdf | pagina-cardapio |
| Deveras Pizza | https://menu.getinapp.com.br/pt-br/e63Rd91v/menus/g6GDvdk0 | https://menu.getinapp.com.br/cardapio.pdf | pagina-cardapio |
| Dialetto Ristorante | http://www.dialettoristorante.com.br/ | https://www.facebook.com/105738107916601 | rede social |
| Dona Doceira | http://www.donadoceira.com.br/ | https://www.facebook.com/646134358815584 | rede social |
| Estação Parrilla São Caetano | http://www.estacaoparrilla.com.br/novo/ | http://www.estacaoparrilla.com.br/ | site |
| Bar dos Arcos | https://bardosarcos.com.br/cardapio-salao-dos-arcos/ | https://bardosarcos.com.br/ | site |
| Sorvetes Lips | http://www.franquiasorveterialips.com.br/franquias-sorveterias/sorveteria-sao-paulo-mooca | http://www.franquiasorveterialips.com.br/ | site |
| Garage Burger | http://www.garageburger.com.br/ | https://www.facebook.com/312063958899410 | rede social |
| Gendai | http://www.gendai.com.br/lojas | http://www.gendai.com.br/cardapio.pdf | pagina-cardapio |
| Gendai | http://www.gendai.com.br/lojas | http://www.gendai.com.br/cardapio.pdf | pagina-cardapio |
| Babilo | http://www.iguatemi.com.br/marketplace/alimentacao/#babil%C3%83%C2%B3 | http://www.iguatemi.com.br/cardapio.pdf | pagina-cardapio |
| Kazuo Restaurante | https://kazuorestaurante.com.br/ | https://www.facebook.com/103065735475077 | rede social |
| Marach Cozinha Armenia | http://www.marach.com.br/ | https://www.facebook.com/623927094768045 | rede social |
| Marach Cozinha Armênia | http://www.marach.com.br/ | https://www.facebook.com/139394019463230 | rede social |
| Marakuthai Itaim | http://www.marakuthai.com.br/ | https://www.facebook.com/108825081393552 | rede social |
| Montana Grill Express | http://www.montanagrill.com.br/nossas-lojas | https://montanagrill.com.br/cardapio | pagina-cardapio |
| Mourisco Pizzaria | http://www.mouriscopizzeria.com.br/ | https://www.facebook.com/200392019987006 | rede social |
| Pandaréu | http://www.pandareu.com.br/ | https://www.facebook.com/168692080287941 | rede social |
| Pizzaria E Grelhados Berlim | http://www.pizzariaberlim.com.br/ | https://www.facebook.com/616178081789090 | rede social |
| Sao paulo Rascal restaurante | http://www.rascal.com.br/home.html | https://www.rascal.com.br/restaurante/cardapio-e-bebidas-rascal-sao-paulo/ | pagina-cardapio |
| Aya Japanese Cuisine | https://menu.getinapp.com.br/pt-br/3Y6xBPv2/menus/Re63zx1v/categories/ljkvaZ62 | https://menu.getinapp.com.br/cardapio.pdf | pagina-cardapio |
| Rubaiyat Faria Lima | https://gruporubaiyat.com/api/uploads/040926-mp-fl-pt-09_26.pdf | https://gruporubaiyat.com/cardapio.pdf | pagina-cardapio |
| Figueira Rubayat | https://gruporubaiyat.com/pt/casas-menu/afigueira/ | https://gruporubaiyat.com/cardapio.pdf | pagina-cardapio |
| Shihoma Pasta Fresca | https://menu.getin.app/pt-br/J6JMbj1X | https://menu.getin.app/cardapio.pdf | pagina-cardapio |
| Spoleto | http://www.spoleto.com.br/busca/lojas/json | https://www.spoleto.com.br:443/tabs/cardapio | pagina-cardapio |
| Spoleto | http://www.spoleto.com.br/lojas/detalhes/206/%3Floja%3DSpoleto%20Shopping%20Center%203 | https://www.spoleto.com.br:443/tabs/cardapio | pagina-cardapio |
| Spoleto | http://www.spoleto.com.br/lojas/detalhes/380/%3Floja%3DSpoleto%20Shopping%20Bosque%20Maia | https://www.spoleto.com.br:443/tabs/cardapio | pagina-cardapio |
| Spoleto | http://www.spoleto.com.br/unidade/spoleto-shopping-cidade-sao-paulo/ | https://www.spoleto.com.br:443/tabs/cardapio | pagina-cardapio |
| Spoleto | http://www.spoleto.com.br/unidade/spoleto-shopping-led-barra-funda/ | https://www.spoleto.com.br:443/tabs/cardapio | pagina-cardapio |
| Vegg's Restaurante Vegetariano e Vegano | http://www.spveg.com/blog/veggs/ | http://www.spveg.com/cardapio.pdf | pagina-cardapio |
| Genesis Alimentacao | http://www.subdelivery.com.br/loja/subway-av-g-edgar-faco/ | http://www.subdelivery.com.br/ | site |
| Restaurante Tantra | http://www.tantrarestaurante.com.br/v2/php/home.php | https://tantrarestaurante.com.br/cardapio | pagina-cardapio |
| Tuy Bar, Cocina | https://www.dguests.com.br/cardapio/tuybarcocinajardins | https://www.dguests.com.br/cardapio.pdf | pagina-cardapio |
| Zena Cucina | https://www.zenacaffe.com.br/cardapios-qr-code/ | https://www.facebook.com/91503159326 | rede social |
| Casa Porteña - ParkShopping São Caetano | https://www.casaportena.com.br/unidades/park-shopping-sao-caetano/ | https://www.facebook.com/107796204100481 | rede social |
| Paparoto Cucina | https://menu.getin.app/pt-br/46lezekZ/menus/O6ONKn1a | https://menu.getin.app/cardapio.pdf | pagina-cardapio |
| Camarada Camarão Santo André - Grand Plaza Shopping | https://www.ocamarada.com.br/restaurantes/grand-plaza-shopping-santo-andre | https://www.camaradacamarao.com.br/cardapios/ | pagina-cardapio |
| Camarada Camarão- Shopping Cidade São Paulo | https://www.ocamarada.com.br/restaurantes/shopping-cidade-sao-paulo-sao-paulo | https://www.camaradacamarao.com.br/cardapios/ | pagina-cardapio |
| Outback Steakhouse - Shopping Boulevard Bauru | https://www.outback.com.br/restaurantes/outback-boulevard-shopping-bauru | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| Outback Steakhouse - Shopping Anália Franco | https://www.outback.com.br/restaurantes/shopping-an%C3%A1lia-franco | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| Outback Steakhouse - Shopping Metrô Santa Cruz | https://www.outback.com.br/restaurantes/shopping-metr%C3%B4-santa-cruz | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| De Segunda | https://desegundarestaurante.com.br/cardapios/cardapio_01.pdf | https://www.facebook.com/100522222136330 | rede social |
| Conselheiro Listening Bar | https://menu.getin.app/pt-br/w6erGxk4/menus/J6J7AdkX | https://menu.getin.app/cardapio.pdf | pagina-cardapio |
| Les Deux Magots | https://lesdeuxmagots.com.br/novoscardapios | https://lesdeuxmagots.com.br/cardapios/ | pagina-cardapio |
| Outback Brasil | https://www.outback.com.br | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| Le Pain Quotidien | https://www.lepainquotidien.com/br/pt/locations/lorena/alameda-lorena,-1914 | https://www.lepainquotidien.com/us/en/menu | pagina-cardapio |
| General Prime | https://generalprimesteakeburger.com.br/ | https://generalprimesteakeburger.com.br/cardapio | pagina-cardapio |
| Restaurante das Aguas | http://www.restaurantedasaguas.com.br/ | https://restaurantedasaguas.com.br/cardapio-restaurante-das-aguas.pdf | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Hitô Itaim | http://www.hitosushi.com.br | https://deliverydireto.com.br/hito/hitosushi | plataforma-no-site |
| Vania Rotisserie | http://www.vaniarotisserie.com.br/ | https://vaniarotisserie.com.br/cardapio-delivery/ | pagina-cardapio |
| Restaurante Spoleto | http://spoleto.com.br/ | https://spoleto.com.br/tabs/cardapio | pagina-cardapio |
| Fogo de Chão Morumbi | https://fogodechao.com | https://fogodechao.com/menu/ | pagina-cardapio |
| Pizza Hut | https://www.pizzahut.com.br/ | https://www.pizzahut.com.br/guest/menu | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Boali | https://www.boali.com.br/ | https://www.boali.com.br/cardapio-saudavel/ | pagina-cardapio |
| Subway | https://restaurantes.subway.com/subway-vila-virginia-jundia-sp | https://restaurantes.subway.com/ | site |
| Restaurante Outback Steakhouse | http://www.outback.com.br | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| Capolino - Cucina italiana | http://www.capolino.com.br/ | https://www.capolino.com.br/cardapio | pagina-cardapio |
| Busger - Borges Lagoa | https://www.busger.com.br/ | https://www.busger.com.br/cardapio | pagina-cardapio |
| REI Do AÇAÍ Piracicaba | http://www.reidoacaipiracicaba.com.br/ | https://www.reidoacaipiracicaba.com.br/cardapio2025.pdf | pagina-cardapio |
| Restaurante Skinão Caseiro | https://l1nq.com/pedidoscaseirao | https://l1nq.com/ | site |
| Le Com Cre Buffet Infantil | http://www.lecomcre.com.br/ | http://lecomcre.com.br/wp-content/uploads/2024/06/buffet_le_com_cre_cardapio_1.jpg | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| McDonald's Sorvetes | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Nova Marotto | http://pizzarianovamarotto.com.br/ | https://pizzarianovamarotto.com.br/cardapio/ | pagina-cardapio |
| Si Senor | https://www.sisenor.com.br/ | https://www.sisenor.com.br/tex-menu | pagina-cardapio |
| Empório Dal Giardino | http://www.dalgiardino.com.br/ | https://dalgiardino.com.br/cardapio | pagina-cardapio |
| Pizzaria Augusta's | http://www.augustaspizzaria.com.br/ | https://augustaspizzaria.saipos.com/home | plataforma-no-site |
| Aline pizzaria | http://www.pizzariachaplin.com.br | https://www.restaurantechaplin.com.br/cardapio-restaurante | pagina-cardapio |
| Al Badah | http://www.albadah.com.br | https://albadah.com.br/cardapio/ | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Restaurante Rancho Português- Graal Barreirense | http://www.ranchoportugues.com.br/ | https://www.ranchoportugues.com.br/cardapio/ | pagina-cardapio |
| Greto´s Restaurante | http://app.gplustogo.com.br/gretosfastfood | http://app.gplustogo.com.br/cardapio.pdf | pagina-cardapio |
| Bob's | https://www.bobs.com.br/ | https://bobs.com.br/cardapio/ | pagina-cardapio |
| Pastificio Primo Sorocaba | http://www.pastificioprimo.com.br | https://www.pastificioprimo.com.br/cardapio/ | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Restaurante Italiano Spoleto - Norte Shopping | http://spoleto.com.br/ | https://spoleto.com.br/tabs/cardapio | pagina-cardapio |
| Cafeteria Cheirin Bao Praia Grande. | https://cheirinbao.com.br/ | https://cheirinbao.com.br/cardapio/ | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Paloma e Gordinho - Pedreira | https://gordinhoepaloma.bsfood.com.br/product | https://gordinhoepaloma.bsfood.com.br/cardapio.pdf | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Le Pain Quotidien | http://www.lepainquotidien.com.br?y_source=1_MTU0Njk1NjItNDQwLWxvY2F0aW9uLndlYnNpdGU%3D | https://www.lepainquotidien.com/us/en/menu | pagina-cardapio |
| Pizzaria Mais Sabor | https://pizzariamaissabor.mandarpedido.com/mobile/home | https://pizzariamaissabor.mandarpedido.com/ | site |
| Mineiro Franchising | http://mineirodelivery.com.br/franquias | https://mineirodelivery.com.br/cardapio/ | pagina-cardapio |
| Si Senor | https://www.sisenor.com.br/ | https://www.sisenor.com.br/tex-menu | pagina-cardapio |
| Frango Atropelado | http://www.frangoatropelado.com.br/ | https://frangoatropelado.com.br/cardapio/ | pagina-cardapio |
| Dona Chica na Floresta | https://go.tagme.com.br/pratodafloresta | https://tagme.com.br/produtos/menu-digital | pagina-cardapio |
| Restaurante CSD | http://www.restaurantebaruk.com.br/ | https://www.restaurantebaruk.com.br/cardapio | pagina-cardapio |
| Frutaria São Paulo | http://www.frutariasaopaulo.com.br | https://frutariasp.com.br/cardapio/ | pagina-cardapio |
| SushiFan Campinas Shopping | https://www.outback.com.br/ | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| McCafé | http://mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Buffet Planeta Kids | http://www.planetakids.com.br/unidades/unidade.php?UC=3 | https://planetakids.com.br/cardapio-buffet-infantil/ | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Cheiro Verde Gourmet Bistrô | http://www.edwigespizzaebistro.com.br/ | https://app.cardapioweb.com/edwiges_delivery_sbo_ltda?s=insta | plataforma-no-site |
| Padaria Belas Artes | https://www.padariabelasartes.com.br/ | https://padariabelasartes.com.br/cardapios/ | pagina-cardapio |
| Max Sushi | http://www.maxsushi.com.br/ | http://www.maxsushi.com.br/cardapios | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Sterna Cafe | http://www.sternacafe.com.br/ | http://www.sternacafe.com.br/menu-sterna-cafe-2.pdf | pagina-cardapio |
| Pizzaria California | http://www.pizzariacalifornia.com.br/ | http://pizzariacalifornia.com.br/menu/ | pagina-cardapio |
| Emporio e Cantina do Largo | Silveira SP | http://www.cantinadolargo.webnode.com/ | https://cantinadolargo.webnode.page/cardapio/ | pagina-cardapio |
| Outback Mogi Shopping | https://www.outback.com.br/ | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Outback Mauá Plaza Shopping | https://www.outback.com.br/ | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| Restaurante Canaã | http://restaurante-canaa.webnode.com/ | https://restaurante-canaa.webnode.page/cardapio/ | pagina-cardapio |
| Pizza Hut | http://www.pizzahut.com.br/ | http://www.pizzahut.com.br/guest/menu | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Jeronimo Smash Burger | http://jeronimoburger.com.br | https://jeronimoburger.com.br/cardapiodigital | pagina-cardapio |
| Outback Mogi Shopping | https://www.outback.com.br/ | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Restaurante daora | http://restaurantehassan.com.br/ | https://restaurantehassan.com.br/cardapio/ | pagina-cardapio |
| Jin Jin | http://www.jinjinwok.com.br | https://jinjin.com.br/cardapio | pagina-cardapio |
| Insano Burger - Melhor Hamburgueria Em Caieiras | https://biolinky.co/insanoburgercaieiras | https://biolinky.co/menu | pagina-cardapio |
| Luppi Steak House | http://pedecomida.com.br/luppishouse | http://pedecomida.com.br/ | site |
| Sabadin Padaria Artesanal | http://www.clickaracoiaba.com.br/guia/empresa/647/sabadin_padaria_artesanal.html | http://www.clickaracoiaba.com.br/ | site |
| Jin Jin Wok | http://www.jinjinwok.com.br | https://jinjin.com.br/cardapio | pagina-cardapio |
| Devoris Salgados | https://app.gplustogo.com.br/devorissalgados | https://app.gplustogo.com.br/cardapio.pdf | pagina-cardapio |
| Nonna Mimi | http://nonnamimi.com.br/cantina/ | http://nonnamimi.com.br/ | site |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Subway | https://restaurantes.subway.com/subway-ribeir-o-preto-sp | https://restaurantes.subway.com/ | site |
| Luz da Lua Burger | https://taplink.cc/luzdalua.burguerbar | https://luz-da-lua-burger-e-bar.goomer.app | plataforma-no-site |
| Panificadora e Confeitaria Pão Vivo | https://agenciahavah.com.br/roots-casa-do-pao-victoriano/ | https://agenciahavah.com.br/ | site |
| Coxinha Real Porto Feliz | http://www.coxinhareal.com.br/ | https://coxinhareal.com.br/menu/ | pagina-cardapio |
| Restaurante Spoleto | http://spoleto.com.br/ | https://spoleto.com.br/tabs/cardapio | pagina-cardapio |
| Ipo Sushi Granja | https://ippogranja.com.br/ | https://app.cardapioweb.com/ipo_sushi | plataforma-no-site |
| Bolo da Madre | https://bolodamadre.com.br/ | https://bolodamadre.com.br/menu | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Café Donuts | http://www.cafedonuts.com.br/ | https://cafedonuts.com.br/cardapio | pagina-cardapio |
| B de Bocaina Restaurante | http://caminhosdacorte.com.br/cidades/bananal/b-de-bocaina-restaurante/ | http://caminhosdacorte.com.br/cardapio.pdf | pagina-cardapio |
| Bob's Shakes | https://www.bobs.com.br/ | https://bobs.com.br/cardapio/ | pagina-cardapio |
| Restaurante Toulouse | http://www.hotelcazuza.com.br/restaurante.php | http://www.hotelcazuza.com.br/ | site |
| Japoneis Restaurante | https://japoneisrestaurante.bsfood.com.br/me | https://japoneisrestaurante.bsfood.com.br/cardapio.pdf | pagina-cardapio |
| Cantina da Nena | http://www.cantinadanena.com.br/ | https://www.cantinadanena.com.br/wp-content/uploads/2026/07/cardapio-valesul.pdf | pagina-cardapio |
| Vista Café Ibirapuera | http://vistacafe.vistasaopaulo.com.br/ | https://vistacafe.vistasaopaulo.com.br/menu/gastronomia/ | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Restaurante Tempero Aires | https://meulink.bio.br/temperoaires | https://meulink.bio.br/cardapio | pagina-cardapio |
| Água Doce Cachaçaria | http://www.aguadoce.com.br/ | https://www.aguadoce.com.br/cardapio.html | pagina-cardapio |
| Hamburgueria Seo Damasco | https://www.flashmenu.app/seo-damasco | https://www.flashmenu.app/cardapio.pdf | pagina-cardapio |
| Springland | https://hamburgueriaspringland.com.br/hamburgueria_springland | https://hamburgueriaspringland.com.br/cardapio.html | pagina-cardapio |
| Le Pain Quotidien | http://www.lepainquotidien.com.br | https://www.lepainquotidien.com/us/en/menu | pagina-cardapio |
| Casa das Massas São Pedro | http://www.pizzariasaopedro.com.br | https://pizzariasaopedro.com.br/wp-content/uploads/2024/04/cardapio-pizzas.pdf | pagina-cardapio |
| Mr. Cheney | http://www.mrcheney.com.br/ | https://www.mrcheneyoficial.com.br/_files/ugd/d324de_e4f1d17aaf904a998c495cd31bec02ff.pdf | pagina-cardapio |
| Capital Burguer | http://www.capitalburguer.com.br | https://capitalburguer.com.br/cardapio/ | pagina-cardapio |
| Chun-Li Chinese Food | https://pedir.chunli.com.br/chunli_food?s=cb | https://pedir.chunli.com.br/ | site |
| Bella Capri Franchising | https://www.bellacapri.com.br/franquia | https://www.bellacapri.com.br/ | site |
| Taishi Temakeria Nova Odessa | http://www.taishi.com.br | https://pedido.anota.ai/loja/taishi-americana?f=msa | plataforma-no-site |
| Pizzaria Fa Bene Ltda | http://www.fabenepizzaria.com.br/ | https://fabenepizzaria.com.br/cardapio/ | pagina-cardapio |
| A Casa da Esfiha- Indaiatuba | https://taplink.cc/a_casa_da_esfiha | https://pedido.anota.ai/loja/a-casa-da-esfiha-indaiatuba-3?f=ms | plataforma-no-site |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Restaurante e Petiscaria Arco Iris | http://www.restaurantearcoiris.com.br/ | http://www.restaurantearcoiris.com.br/cardapio/cardapio.pdf | pagina-cardapio |
| Alternativa Prêmios | https://rd.app/s/NMxL6j7xCS9 | https://rd.app/ | site |
| Amor aos Pedaços | http://amoraospedacos.com.br | https://www.amoraospedacos.com.br/wp-content/uploads/2026/11/CARDAPIO-DIGITAL-NATAL_SP.pdf | pagina-cardapio |
| Lanchao e Cia | http://lanchao.com.br/site/mobile/unidades.php?id=25 | http://lanchao.com.br/ | site |
| Pizzaria | https://eprajaonline.com/store/castelo-pizzaria | https://eprajaonline.com/cardapio.pdf | pagina-cardapio |
| Nova Grill churrascaria & Pizzaria São Miguel | http://www.novagrilldelivery.com.br | https://novagrill.com.br/cardapio/ | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Costazul Seafood | http://www.costazulseafood.com.br/ | https://pedido.anota.ai/loja/costazul-seafood-santos | plataforma-no-site |
| Restaurante Spoleto | http://spoleto.com.br/ | https://spoleto.com.br/tabs/cardapio | pagina-cardapio |
| Famiglia Mancini Trattoria | http://restaurantesantafe.com.br/ | http://www.redegourmet.com.br/cardapio/santafe-brooklin | pagina-cardapio |
| Império Mineiro | http://www.imperiomineiro.com.br | https://www.imperiomineiro.com.br/cardapio-comida-mineira-menu-imperio-mineiro-ac1021 | pagina-cardapio |
| Nakato Sushi Morumbi - Restaurante Japonês Rodízio  Delivery | http://nakato.com.br | https://www.nakato.com.br/cardapioalacart | pagina-cardapio |
| Oba Gourmet | https://www.outback.com.br/ | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| Croasonho | http://www.croasonho.com.br | https://croasonho.com.br/cardapio | pagina-cardapio |
| Empório Verace Jundiaí | https://veracejundiai.com.br/emporio | https://veracejundiai.com.br/wp-content/uploads/2026/06/MenuDellaCasa_A3_VeraceEmporio_compressed.pdf | pagina-cardapio |
| Cachaçaria Santo Mé | http://www.cachacariasantome.com.br/ | https://cachacariasantome.com.br/cardapio-virtual-2/ | pagina-cardapio |
| Pastelaria Jj | https://pastelariapapajapa.mandarpedido.com/facebook | https://pastelariapapajapa.mandarpedido.com/ | site |
| Pizza Hut | https://www.pizzahut.com.br/ | https://www.pizzahut.com.br/guest/menu | pagina-cardapio |
| Faveral Temakeria Fonte Araraquara | https://cardapio.datacaixa.com.br/faveralfonte | https://cardapio.datacaixa.com.br/cardapio.pdf | pagina-cardapio |
| Outback Araraquara | https://www.outback.com.br/ | https://www.outback.com.br/nossosprodutos/menu-principal | pagina-cardapio |
| Kiichi | http://www.kiichi.com.br/ | https://kiichi.com.br/cardapios/CARDAPIOS-KIICHI-2026-A-LA-CARTE.pdf | pagina-cardapio |
| Dídio Pizza | http://didio.com.br/unidades/campinas-castelo | https://didio.com.br/novo-cardapio-pizzas/ | pagina-cardapio |
| Kairós Chicken | https://youdelivery.com.br/c/kairoschicken/ | https://youdelivery.com.br/ | site |
| Fran's Café | http://www.franscafe.com.br | https://www.franscafe.com.br/cardapio | pagina-cardapio |
| Croasonho | http://www.croasonho.com.br | https://croasonho.com.br/cardapio | pagina-cardapio |
| Água Doce Cachaçaria | http://www.aguadoce.com.br | https://www.aguadoce.com.br/cardapio.html | pagina-cardapio |
| Dídio Pizza Campo Belo | http://www.didio.com.br | https://didio.com.br/novo-cardapio-pizzas/ | pagina-cardapio |
| Pizzaria Vicenzo | https://anella.com.br/ | https://anella.com.br/cardapio/ | pagina-cardapio |
| Parmeggio | http://www.parmeggio.com.br | https://parmeggio.com.br/cardapio/ | pagina-cardapio |
| Rei do Mate | https://lojas.reidomate.com.br/rei-do-mate-parque-viracopos-campinas-sp | https://lojas.reidomate.com.br/ | site |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Alameda Café | https://www.alamedacafe.com.br/ | https://www.alamedacafe.com.br/cardapio | pagina-cardapio |
| Jin Jin Wok | http://www.jinjin.com.br/ | https://jinjin.com.br/cardapio | pagina-cardapio |
| TR-3 | http://www.clicasorocaba.com.br/vemar | http://www.clicasorocaba.com.br/ | site |
| Café Donuts | http://www.cafedofeirante.com.br | https://cafedofeirante.com.br/cardapio/ | pagina-cardapio |
| rickscongelados | http://www.rickscongelados.com.br/ | https://ricksfoodservices.com/cardapio/ | pagina-cardapio |
| Restaurante Casarao | http://restaurante-canaa.webnode.com/ | https://restaurante-canaa.webnode.page/cardapio/ | pagina-cardapio |
| Fran's Café | http://www.franscafe.com.br | https://www.franscafe.com.br/cardapio | pagina-cardapio |
| Cheirin Bão | http://www.cheirinbao.com.br/ | https://cheirinbao.com.br/cardapio/ | pagina-cardapio |
| É de casa restaurante | https://instabio.cc/Edecasacampinas | https://instabio.cc/cardapio | pagina-cardapio |
| Spits | http://spoleto.com.br/ | https://spoleto.com.br/tabs/cardapio | pagina-cardapio |
| McDonald's | http://mcdonalds.com.br | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Vila Japi | http://www.vilajapi.com.br/ | https://www.vilajapi.com.br/cardapio | pagina-cardapio |
| Gulosão Pizza Frita e Restaurante | https://shop.beetech.com.br/sejagulosao | https://shop.beetech.com.br/cardapio | pagina-cardapio |
| Suzano Buffet Democrata | http://www.democratabuffet.com.br/ | http://www.democratabuffet.com.br/cardapio | pagina-cardapio |
| Oficina Burguer | https://app.gplustogo.com.br/dogzillalanches | https://app.gplustogo.com.br/cardapio.pdf | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| McDonald's | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Bella Capri Pizzaria | http://www.bellacapri.com.br/lojas/catanduva-quinze | http://www.bellacapri.com.br/ | site |
| Rinaffe Restaurante | https://app.gplustogo.com.br/restauranterinaffe | https://app.gplustogo.com.br/cardapio.pdf | pagina-cardapio |
| Dona Coelho | http://whats.link/donacoelho | http://whats.link/menu | pagina-cardapio |
| Padaria Padoka da Ká | https://padokadaka.com.br/ | https://padokadaka.com.br/cardapio/ | pagina-cardapio |
| Dona Catarina Restaurante | http://donacatarinarestaurante.com.br/ | https://donacatarinarestaurante.com.br/cardapio/ | pagina-cardapio |
| Ney Lanches | https://menu.infoluck.com.br/ney-lanches-amparo | https://menu.infoluck.com.br/cardapio.pdf | pagina-cardapio |
| La torre creperia e cafe | http://www.jccafe.com.br/ | https://jccafe.goomer.app | plataforma-no-site |
| Rei do Frango | http://oreidofrangoapassarinho.com.br/ | https://app.anota.ai/m/Lcvt9R_Gw | plataforma-no-site |
| Mc Donalds Maginal Pinheiros | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Pizzaria Primavera | https://pizzariaprimavera.creapp.com.br/app/?codigo=7115 | https://pizzariaprimavera.creapp.com.br/cardapio | pagina-cardapio |
| Cheirin Bão São José dos Campos | http://www.cheirinbao.com.br/ | https://cheirinbao.com.br/cardapio/ | pagina-cardapio |
| Lanchão Shopping Bandeiras | http://www.lanchao.com.br/lojas | http://www.lanchao.com.br/ | site |
| Leveat | https://menuprime.com.br/leveat | https://menuprime.com.br/cardapio.pdf | pagina-cardapio |
| McCafé | http://www.mcdonalds.com.br/ | https://www.mcdonalds.com.br/cardapio | pagina-cardapio |
| Spoleto Franca | http://www.spoleto.com.br/ | https://www.spoleto.com.br:443/tabs/cardapio | pagina-cardapio |
| Feira francisca Julia | http://www.jullia.com.br/home.html | https://jullia.com.br/cardapio/ | pagina-cardapio |
