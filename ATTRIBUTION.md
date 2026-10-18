# Atribuição das fontes de dados

Os arquivos publicados (`sp/*.csv`, `index.json`) combinam estas fontes:

## Planilha Cardápios
Base mantida manualmente pela DocPocket Ltda. (camada de correção que ganha das fontes automáticas).

## Overture Maps Foundation — Places
Dados de lugares © Overture Maps Foundation e contribuidores, https://overturemaps.org.
O tema Places é multi-licenciado (https://docs.overturemaps.org/attribution/):

- **CDLA-Permissive-2.0** (https://cdla.dev/permissive-2-0/): dados da Meta, Microsoft e outros.
- **Apache License 2.0** (https://www.apache.org/licenses/LICENSE-2.0): dados da Foursquare (Foursquare Open Source Places).
  NOTICE: "This product includes data from Foursquare Open Source Places (FSQ OS Places),
  © Foursquare Labs, Inc., licensed under the Apache License, Version 2.0."
- **CDLA-Permissive-2.0 / CC0** para AllThePlaces e demais fontes indicadas em `sources` de cada registro.

Linha sugerida no app ("Sobre"):
> Dados: planilha Cardápios; Overture Maps Foundation (CDLA-Permissive-2.0; Apache-2.0 — Foursquare).

## OpenStreetMap (ainda não usado)
Quando o enriquecimento OSM (`cardapios_dados/osm.py`) for ativado:
> © colaboradores do OpenStreetMap, dados sob ODbL 1.0 — https://www.openstreetmap.org/copyright

e a base publicada passa a ser distribuída sob ODbL (share-alike), ver `LICENSE-DATA.md`.
