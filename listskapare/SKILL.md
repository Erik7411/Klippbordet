---
name: listskapare
description: Gör webblistor till .txt med en post per rad, till Nämn en, Tidslinjen och Pingpong. Använd vid /listskapare eller när Eken vill skrapa, hämta eller sammanställa en lista från en webbsida.
---

# Listskapare

Gör en webblista till en `.txt`-fil med **en post per rad**: utan numrering, rubriker, fotnoter
eller förklaringar. Filen ska gå att använda direkt i Nämn en, Tidslinjen eller Pingpong. Allt
om var listan kommer ifrån redovisas i svaret, inte i filen, så att filen förblir ren.

Eken vill ha sakliga, källkritiska svar på svenska. Det betyder här: säg exakt varifrån listan
kommer, hur många poster den har och vad som kan vara fel med den. En lista som ser komplett ut
men inte är det är värre än ingen lista, eftersom den hamnar i ett tv-program.

## Verktygen

Allt finns i skillens mapp (här kallad `SKILLMAPP`):

- `listskapare.py` – hämtar en sida (eller läser en sparad HTML-fil), hittar listorna och sparar
  vald lista. Kräver Python 3.10+ med `beautifulsoup4` och `lxml`
  (`pip install beautifulsoup4 lxml` om importen misslyckas).
- `webblasarskript/hamta-med-webblasare.js` – används av `--webblasare`; kräver Node.js och Playwright.
- `bokmarke.html` – installationssida för bokmärket "Listskapare": Eken drar en knapp till
  bokmärkesfältet. Bokmärket laddar hela listan i Ekens egen webbläsare; IMDb-listor sparas
  direkt som .txt, andra sidor som .html. Adressen finns också i `webblasarskript/ladda-allt.bokmarke.txt`.
- `README.md` – samma rutin skriven för människor. Läs den bara om något här är oklart.

Kör alltid skriptet i stället för att skriva egen skrapkod: det är testat, städar bort fotnoter
och dubbletter, och ger samma resultat varje gång.

## Rutin

### 1. Välj källa

Ta en sida som har hela listan på ett ställe: Wikipedia-tabeller, officiella förteckningar,
organisationens egen topplista. Svensk Wikipedia ger svenska namnformer, vilket oftast är vad
programmet vill ha. Föreslår Eken en källa, använd den.

### 2. Se vilka listor som finns

```bash
python3 SKILLMAPP/listskapare.py "URL" --visa
```

Skriptet visar kandidater (tabellkolumner, punktlistor, rubriker, JSON-LD) med flest poster först,
med de första posterna som prov. Välj den som faktiskt är listan; den största är inte alltid rätt.

### 3. Spara

```bash
python3 SKILLMAPP/listskapare.py "URL" --kandidat 4 --ut namn.txt
```

Spara där Eken kan öppna filen: i arbetsmappen eller utdatamappen, aldrig i skillens mapp. Ge
filen ett beskrivande namn med små bokstäver och bindestreck, t.ex. `sveriges-statsministrar.txt`.

**Format per moment:**
- **Nämn en** och **Pingpong**: bara posten, t.ex. `Arvid Posse`. Vet du inte vilket format
  Pingpong-momentet behöver i ett visst fall, fråga hellre än gissa.
- **Tidslinjen**: posten och dess tidpunkt. Slå ihop två tabellkolumner:
  ```bash
  python3 SKILLMAPP/listskapare.py "URL" --tabell 1 --kolumner 2,3 --ut namn.txt
  ```
  ger `Louis De Geer d.ä. – 20 mars 1876`. Tabellnumret står i `--visa`-utskriften.

Hittar inte `--visa` rätt lista: ange en CSS-selektor med `--selektor "h3.titel"`.

### 4. Listor som visas lite i taget

| Så ser sidan ut | Gör så här |
|---|---|
| Sidnummer i adressen (`?page=2`, `/sida/3/`) | Skriv `{sida}` där numret står: `"https://x.se/lista?page={sida}"`. Skriptet slutar vid en tom sida eller en sida som är likadan som den förra. `--forsta-sida 0` om numreringen börjar på 0. |
| En "Nästa"-länk utan mönster i adressen | `--nasta "a.next"` (CSS-selektor för länken). |
| "Visa fler"/"Load more", eller mer laddas vid scroll | `--webblasare`. Klickar och scrollar tills inget nytt laddas. |

Skriptet väntar 2 sekunder mellan sidorna. Sänk inte pausen för att det ska gå fortare: det är
någon annans server.

### 5. Kontrollera innan du lämnar över

- **Antal**: stämmer antalet rader med vad källan själv säger ("290 kommuner", "Top 1000")?
  Räkna med `wc -l`. Avviker det, säg hur mycket och varför, om du vet.
- **Början och slut**: läs de första och sista raderna och jämför med källan.
- **Skräp**: rubrikrader, "Totalt", fotnotsrester, tomma rader, dubbletter.
- **Rimlighet**: titta igenom hela listan efter poster som inte hör dit.

- **Aktualitet**: slutar listan med något som gäller "nu" (sittande statsminister, regerande
  mästare, senaste vinnare) kan sidan vara inaktuell. Kontrollera dagsläget med en webbsökning om
  du kan, och säg vad du fann. Kan du inte kontrollera det, säg det.
- **Återkommande poster**: en tabell har ofta en rad per tillfälle, inte per person eller sak
  (Branting var statsminister tre gånger). Välj det som passar momentet, för Nämn en oftast en rad
  per person, och säg vilket du valt och hur många rader det andra valet skulle ge.
- **Namnform**: i Nämn en ska listan visa vilka svar som godkänns. Står namnen i en lång form
  ("Falu kommun", "Lindman, Arvid"), säg det och erbjud en kortare form. Gör den inte mekaniskt
  om det kräver bedömning (Falu → Falun).

Rätta det som går att rätta (fel kandidat, fel kolumn, en rubrikrad som följt med) och kör om.

### 6. Redovisa

Avsluta med en kort redovisning i svaret:

- källa (URL) och datum för hämtningen
- metod (vilket kommando, vilken kandidat eller kolumn)
- antal rader, och om det stämmer med källan
- kända avvikelser och osäkerheter

Arbetar du i Ekens repo Klippbordet: lägg också till en rad i `listskapare/listor/KALLOR.md` och
spara listan i `listskapare/listor/`.

Skicka filen till Eken med verktyget för att dela filer, om ett sådant finns.

## När sidan blockerar

Svarar sidan 403, visar en CAPTCHA, eller kräver inloggning: **försök inte ta dig förbi spärren**
(falska webbläsaravtryck, proxytjänster, CAPTCHA-lösare). Spärren är sidägarens beslut, sådan
skrapning bryter ofta mot användarvillkoren, och för material till ett SVT-program är det en
onödig risk. Gör så här, i ordning, och berätta för Eken vad du valde och varför:

1. **Officiell data.** Många har nedladdningsbar data eller ett API. För IMDb finns ett färdigt läge:
   ```bash
   python3 SKILLMAPP/listskapare.py imdb --antal 1000 --ut imdb-topp-1000.txt
   ```
   Det bygger listan ur IMDb:s datafiler (filmer med minst 25 000 röster, sorterade på betyg).
   Säg tydligt att det **inte** är en kopia av IMDb:s egen topplista, att IMDb inte redovisar hur
   den väljs ut, och att datafilerna enligt IMDb är "for personal and non-commercial use".
   Fler val: `--minroster`, `--typ movie,tvSeries`, `--originaltitel`, `--utan-ar`.
2. **Ekens egen webbläsare.** Sidan fungerar oftast för vanliga besökare. Har Eken inte
   bokmärket "Listskapare" än: skicka `bokmarke.html` och be Eken öppna den och dra knappen till
   bokmärkesfältet. Sedan: öppna listan, klicka på bokmärket, vänta på "Klart". En IMDb-lista blir
   då en färdig .txt (kontrollera den ändå). Andra sidor blir en .html-fil som Eken skickar hit;
   kör `listskapare.py` på den.
3. **En annan källa** med samma lista, t.ex. Wikipedia.

## Fyll aldrig i ur minnet utan att säga det

Går listan inte att hämta, lämna inte över en lista ur ditt eget minne som om den vore hämtad.
Om Eken vill ha en lista ur minnet ändå, märk den uttryckligen som det och som okontrollerad.
Samma sak om du kompletterar en hämtad lista: säg vilka rader du lagt till och varifrån.
