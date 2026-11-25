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

## Krav

Python 3.10 eller senare med `beautifulsoup4` och `lxml`:

```bash
pip install beautifulsoup4 lxml
```
