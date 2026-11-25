# Listskapare

Tar fram listor från webbsidor, som underlag till momenten **Nämn en**, **Tidslinjen** och **Pingpong**.
Resultatet är alltid en `.txt`-fil med **en post per rad**, utan numrering, rubriker eller annan text.
Var listan kommer ifrån skrivs i `listor/KALLOR.md`, inte i själva listfilen.

## Standardrutin

1. **Välj källa.** Hellre en sida som har hela listan på ett ställe (Wikipedia-tabeller, officiella
   topplistor, organisationers egna förteckningar) än en artikel som räknar upp saker i löptext.
2. **Se vilka listor som finns på sidan:**
   ```bash
   python3 listskapare/listskapare.py "URL" --visa
   ```
   Skriptet letar i strukturerad data (JSON-LD), tabeller (en kandidat per kolumn), punktlistor och
   rubriker, och visar dem med flest poster först.
3. **Spara den kandidat som stämmer:**
   ```bash
   python3 listskapare/listskapare.py "URL" --kandidat 4 --ut listskapare/listor/namn.txt
   ```
   För Tidslinjen behövs ofta två kolumner, t.ex. namn och årtal:
   ```bash
   python3 listskapare/listskapare.py "URL" --tabell 1 --kolumner 2,3 --ut listskapare/listor/namn.txt
   ```
   Om ingen kandidat passar: ange en CSS-selektor, och vid behov länken till nästa sida:
   ```bash
   python3 listskapare/listskapare.py "URL" --selektor "h3.titel" --nasta "a.nasta" --ut lista.txt
   ```
4. **Kontrollera** innan listan används:
   - Stämmer antalet rader med det källan själv säger (t.ex. "1000 titlar")?
   - Stämmer första och sista posten med källan?
   - Har dubbletter, fotnotsrester eller rubrikrader följt med?
5. **Skriv in listan i `listor/KALLOR.md`**: källa, datum, metod och kända avvikelser.

## Listor som visas lite i taget

Se först efter hur sidan går vidare till nästa del av listan. Det finns tre varianter:

| Så ser det ut | Gör så här |
|---|---|
| Adressen ändras med ett sidnummer: `…?page=2`, `…/sida/3/` | Skriv `{sida}` där numret står. Skriptet räknar uppåt tills en sida är tom eller likadan som den förra. |
| En länk "Nästa" byter sida, men adressen följer inget mönster | Ange länken med `--nasta` och en CSS-selektor. |
| Knappen "Visa fler"/"Load more", eller mer laddas när man scrollar | `--webblasare`, eller bokmärket "Ladda allt" (nedan). |

```bash
python3 listskapare/listskapare.py "https://exempel.se/lista?page={sida}" --visa
python3 listskapare/listskapare.py "https://exempel.se/lista?page={sida}" --kandidat 2 --ut lista.txt
python3 listskapare/listskapare.py "https://exempel.se/lista" --selektor "h3" --nasta "a.next" --ut lista.txt
python3 listskapare/listskapare.py "https://exempel.se/lista" --webblasare --visa
```

Börjar numreringen på 0 i stället för 1: lägg till `--forsta-sida 0`. Skriptet väntar 2 sekunder
mellan sidorna (`--paus`) och går högst 50 sidor (`--maxsidor`).

`--webblasare` öppnar sidan i en webbläsare utan fönster, klickar på knappar av typen "Visa fler",
"Ladda fler", "Load more" eller "50 more", och scrollar när det inte finns någon sådan knapp. Det
håller på tills inget nytt laddas två gånger i rad, eller högst 300 gånger (`--max-rundor`). Det
kräver Node.js och Playwright.

### Bokmärket "Ladda allt"

Samma sak, men i din egen webbläsare. Det behövs när en sida spärrar hämtningar från skript, men
fungerar för vanliga besökare.

1. **En gång:** skapa ett bokmärke och klistra in hela raden i
   `webblasarskript/ladda-allt.bokmarke.txt` som adress.
2. **Varje gång:** öppna listan och klicka på bokmärket. En ruta uppe till höger visar hur det går.
   När den säger "Klart" har hela sidan sparats som en `.html`-fil bland dina hämtade filer.
3. Kör `python3 listskapare/listskapare.py sidan.html --visa`, eller ladda upp filen till Claude.

Bokmärket klickar inte på länkar som byter sida, eftersom det redan laddade då försvinner. För
listor med "Nästa"-länkar fungerar `--nasta` eller `{sida}` bättre.

**Begränsningar:**
- Knappen hittas på texten. Har den en annan text, som "Fortsätt" eller bara en pil, hittas den inte.
  Då scrollar skriptet i stället, och det räcker inte alltid.
- Cookie-rutor och inloggningskrav hanteras inte.
- En sida som tar bort de första posterna när nya laddas (vanligt i mycket långa flöden) ger en
  ofullständig lista. Kontrollera alltid antalet rader mot källan.

Ändrar du ett webbläsarskript: kör `python3 webblasarskript/gor-bokmarke.py webblasarskript/ladda-allt.js`
så att bokmärket uppdateras.

## Sidor som blockerar automatiska hämtningar

Vissa webbplatser (t.ex. IMDb) stoppar skript. Kringgå inte spärren. Gör i stället så här, i ordning:

1. **Officiell data.** Många har nedladdningsbar data eller ett API. För IMDb finns ett färdigt läge:
   ```bash
   python3 listskapare/listskapare.py imdb --antal 1000 --ut listskapare/listor/imdb-topp-1000.txt
   ```
   Fler val: `--minroster`, `--typ movie,tvSeries`, `--originaltitel`, `--utan-ar`.
2. **Spara sidan själv i webbläsaren** (Arkiv > Spara som > "Webbsida, endast HTML") och kör skriptet
   på filen i stället för på URL:en. På sidor som laddar fler poster med en knapp ("50 more"), klicka
   tills alla poster syns innan du sparar.
3. **En annan källa** med samma lista, t.ex. Wikipedia.

### IMDb-listor direkt från webbläsaren

`webblasarskript/imdb-lista.js` körs i din egen webbläsare på en öppen IMDb-lista. Det klickar
"50 more" tills allt har laddats och laddar sedan ner en `.txt` med en titel per rad, i formen
`Titel (år)`. Det väntar 1,5 sekunder mellan klicken.

**Som bokmärke (en gång):** skapa ett nytt bokmärke i webbläsaren och klistra in hela raden i
`webblasarskript/imdb-lista.bokmarke.txt` som adress.

**Varje gång:** öppna listan, t.ex.
`https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc`, klicka på bokmärket
och vänta tills rutan uppe till höger säger "Klart". Filen hamnar bland dina hämtade filer.

Utan bokmärke: tryck F12, välj fliken Console, klistra in innehållet i `imdb-lista.js` och tryck Enter.

Skriptet är testat mot en egen kopia av sidans uppbyggnad, inte mot imdb.com, som blockerar
hämtningar från den miljö där det skrevs. Om IMDb ändrar sidan kan skriptet behöva justeras.

## Krav

Python 3.10 eller senare med `beautifulsoup4` och `lxml`. För `--webblasare` behövs också Node.js med Playwright (`npm install playwright` och `npx playwright install chromium`).

```bash
pip install beautifulsoup4 lxml
```
