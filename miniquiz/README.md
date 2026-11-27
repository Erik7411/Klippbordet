# Miniquiz

Gör nio bilder i 16:9 till en Miniquiz, med frågebilder, svarsbilder och en svarslista.

Öppna `index.html` i webbläsaren. Den behöver `kartdata.js` i samma mapp.

## Teman

- **Regioner i ett land:** landets regioner visas med gränser och en region är markerad, till exempel "Vilken är delstaten?". För vissa länder, som Frankrike och Italien, kan man välja större regioner i stället för departement och provinser.
- **Länder i en världsdel:** en världsdel visas och ett land är markerat.
- **Egna bilder:** man lägger in egna bilder. De beskärs till 16:9, och man kan flytta och zooma utsnittet.

Valet i varje ruta och svarstexten kan ändras för hand. "Ladda ner zip" sparar `fraga-1..9.png`, `svar-1..9.png` och `svar.txt` i 1920 × 1080 eller 3840 × 2160.

## Kartdata och förbehåll

Gränser och namn kommer från [Natural Earth](https://www.naturalearthdata.com/), version 5.2.0-pre. Data är public domain ([villkor](https://www.naturalearthdata.com/about/terms-of-use/)). Admin-0 är i skala 1:50m och admin-1 i 1:10m, förenklade med mapshaper.

- Indelningen kan vara inaktuell. Natural Earth visar till exempel Norges 19 fylken från före 2020, men Norge har 15 fylken sedan 2024.
- De svenska namnen (`name_sv`) är ojämna, till exempel "Opole vojvodskap" och "Iwate" utan "prefektur". Kontrollera varje svar innan sändning.
- Gränser i omstridda områden följer Natural Earths standardval.

Bygg om datan med `data/bygg.sh`.
