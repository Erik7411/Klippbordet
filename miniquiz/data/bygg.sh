#!/usr/bin/env bash
# Bygger om miniquiz/kartdata.js från Natural Earth (public domain).
# Kräver python3, curl och node. Kör från miniquiz/data: ./bygg.sh
set -euo pipefail
cd "$(dirname "$0")"
T=$(mktemp -d)
NE=https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson
curl -sSL -o "$T/admin1.geojson" "$NE/ne_10m_admin_1_states_provinces.geojson"
curl -sSL -o "$T/countries50.geojson" "$NE/ne_50m_admin_0_countries.geojson"
mkdir -p "$T/split" "$T/out15"
python3 dela.py "$T/admin1.geojson" "$T/split" "$T/countries50.geojson"
MS="npx --yes mapshaper@0.6"
for f in "$T"/split/*.geojson; do
  a=$(basename "$f" .geojson)
  $MS "$f" -simplify 18% keep-shapes -o "$T/out15/$a.json" format=topojson quantization=10000 >/dev/null
done
$MS "$T/countries50.geojson" -filter-fields ADM0_A3,NAME_SV,NAME,CONTINENT,SUBREGION,TYPE \
  -rename-fields a=ADM0_A3,n=NAME_SV,e=NAME,k=CONTINENT,s=SUBREGION,y=TYPE \
  -simplify 25% keep-shapes -o "$T/countries.json" format=topojson quantization=20000 >/dev/null
python3 sla-ihop.py "$T" ../kartdata.js
echo "Klart: ../kartdata.js"
