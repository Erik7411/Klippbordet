#!/usr/bin/env python3
"""Listskapare: plocka ut en lista från en webbsida och spara den som .txt, en post per rad.

Används för att ta fram underlag till momenten Nämn en, Tidslinjen och Pingpong.

Exempel:
  # Visa vilka listor som finns på en sida (gissar själv, visar kandidater)
  python3 listskapare.py https://sv.wikipedia.org/wiki/Lista_över_Sveriges_statsministrar --visa

  # Ta kandidat nr 2 och spara
  python3 listskapare.py URL --kandidat 2 --ut statsministrar.txt

  # Slå ihop två tabellkolumner (t.ex. namn och tillträdesår, för Tidslinjen)
  python3 listskapare.py URL --tabell 2 --kolumner 2,4 --ut lista.txt

  # Ange själv vad som ska plockas (CSS-selektor) och följ "nästa sida"-länkar
  python3 listskapare.py URL --selektor "h3.title" --nasta "a.next" --ut lista.txt

  # Lista uppdelad på numrerade sidor: skriv {sida} där sidnumret står
  python3 listskapare.py "https://exempel.se/lista?page={sida}" --kandidat 1 --ut lista.txt

  # Lista med "Visa fler"-knapp eller som laddar mer när man scrollar
  python3 listskapare.py URL --webblasare --visa

  # Sida som blockerar automatiska hämtningar: spara sidan i webbläsaren
  # (Arkiv > Spara som > "Webbsida, endast HTML") och läs den lokala filen
  python3 listskapare.py sparad_sida.html --visa

  # IMDb (blockerar skrapning): bygg listan ur IMDb:s officiella datafiler
  python3 listskapare.py imdb --antal 1000 --ut imdb-topp-1000.txt
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    sys.exit("Saknar beautifulsoup4. Installera med: pip install beautifulsoup4 lxml")

UA = "Listskapare/1.0 (list tool for research; python-urllib)"


# ---------------------------------------------------------------- hämtning

WEBBLASARE = False   # sätts av --webblasare
MAX_RUNDOR = 0


def hamta_med_webblasare(url: str) -> str:
    """Öppnar sidan i Chromium, laddar alla poster ("Visa fler", scroll) och returnerar HTML."""
    import subprocess
    import tempfile
    skript = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "webblasarskript", "hamta-med-webblasare.js")
    with tempfile.TemporaryDirectory() as mapp:
        ut = os.path.join(mapp, "sida.html")
        r = subprocess.run(["node", skript, url, ut, str(MAX_RUNDOR)])
        if r.returncode != 0 or not os.path.exists(ut):
            raise RuntimeError("webbläsaren kunde inte hämta sidan (se ovan)")
        with open(ut, encoding="utf-8") as f:
            return f.read()


def hamta(kalla: str, tyst_fel: bool = False) -> tuple[str | None, str]:
    """Returnerar (html, bas-url). Källan kan vara en URL eller en lokal fil."""
    if WEBBLASARE and not os.path.exists(kalla):
        try:
            return hamta_med_webblasare(kalla), kalla
        except Exception as e:
            if tyst_fel:
                return None, ""
            sys.exit(f"Kunde inte hämta {kalla}: {e}")
    if os.path.exists(kalla):
        with open(kalla, encoding="utf-8", errors="replace") as f:
            return f.read(), ""
    # Adresser med å/ä/ö (t.ex. Lista_över_…) måste kodas; redan kodade %C3%B6 lämnas orörda
    kalla = urllib.parse.quote(kalla, safe=":/?&=%#+,;@!$'()*~[]")
    req = urllib.request.Request(kalla, headers={
        "User-Agent": UA, "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
            if r.status != 200 or not data:
                raise RuntimeError(f"HTTP {r.status}, {len(data)} byte")
            charset = r.headers.get_content_charset() or "utf-8"
            return data.decode(charset, errors="replace"), r.geturl()
    except Exception as e:
        if tyst_fel:
            print(f"  slut: {kalla} gav {e}", file=sys.stderr)
            return None, ""
        kod = getattr(e, "code", None)
        sparrad = kod in (401, 403, 429) or "HTTP 202" in str(e)
        sys.exit(f"Kunde inte hämta {kalla}: {e}" + (
            "\nSidan verkar spärra automatiska hämtningar. Kringgå inte spärren: använd "
            "officiell data, bokmärket i den egna webbläsaren eller en annan källa." if sparrad else ""))


# ---------------------------------------------------------------- städning

FOTNOT = re.compile(r"\[(\d+|[a-z]|not \d+|källa behövs|citation needed)\]", re.I)
NUMRERING = re.compile(r"^\s*\(?\d{1,4}[.):]\s+")


def stada(text: str) -> str:
    text = FOTNOT.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = NUMRERING.sub("", text)
    return text.strip(" ,;·•–-")


def unika(rader: list[str]) -> list[str]:
    sett, ut = set(), []
    for r in rader:
        r = stada(r)
        if r and r.casefold() not in sett:
            sett.add(r.casefold())
            ut.append(r)
    return ut


# ---------------------------------------------------------------- kandidater

BRUS = (".reference, .references, .reflist, .navbox, .mw-editsection, .sortkey, "
        ".noprint, .metadata, .infobox, .sidebar, #toc, .toc")


def tabellrutnat(tab) -> list[list[str]]:
    """Gör om en HTML-tabell till ett rutnät och fyller i rowspan/colspan."""
    rutnat: list[list[str]] = []
    vantar: dict[int, tuple[int, str]] = {}  # kolumn -> (rader kvar, text)
    for tr in tab.find_all("tr"):
        if tr.find_parent("table") is not tab:
            continue
        rad: list[str] = []
        celler = tr.find_all(["td", "th"], recursive=False)
        ci = 0
        while celler or ci in vantar:
            if ci in vantar:
                kvar, text = vantar[ci]
                rad.append(text)
                vantar[ci] = (kvar - 1, text)
                if kvar - 1 <= 0:
                    del vantar[ci]
                ci += 1
                continue
            cell = celler.pop(0)
            text = stada(cell.get_text(" "))
            for _ in range(int(re.sub(r"\D", "", cell.get("colspan", "1")) or 1)):
                rs = int(re.sub(r"\D", "", cell.get("rowspan", "1")) or 1)
                if rs > 1:
                    vantar[ci] = (rs - 1, text)
                rad.append(text)
                ci += 1
        if rad:
            rutnat.append(rad)
    return rutnat


def tabeller(soup: BeautifulSoup) -> list[tuple[list[str], list[list[str]]]]:
    ut = []
    for tab in soup.find_all("table"):
        g = tabellrutnat(tab)
        if len(g) >= 4:
            ut.append((g[0], g[1:]))
    return ut


def ser_bra_ut(v: list[str]) -> bool:
    """Sållar bort kandidater med långa textstycken (fotnoter, navigationsrutor)."""
    langder = sorted(len(x) for x in v)
    return langder[len(langder) // 2] <= 70


def kandidater(soup: BeautifulSoup) -> list[tuple[str, list[str]]]:
    """Hittar troliga listor på sidan, flest poster först."""
    ut: list[tuple[str, list[str]]] = []

    # 1. Strukturerad data (JSON-LD ItemList) – mest pålitlig när den finns
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        for obj in data if isinstance(data, list) else [data]:
            if isinstance(obj, dict) and obj.get("@type") == "ItemList":
                namn = []
                for el in obj.get("itemListElement", []):
                    item = el.get("item", el) if isinstance(el, dict) else {}
                    if isinstance(item, dict) and item.get("name"):
                        namn.append(item["name"])
                if namn:
                    ut.append(("JSON-LD ItemList", namn))

    for s in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        s.decompose()
    for s in soup.select(BRUS):
        s.decompose()
    # Dolda element, t.ex. Wikipedias sorteringsvärden "&&&&032629.&&0" före "32 629"
    for s in soup.find_all(style=re.compile(r"display\s*:\s*none")):
        s.decompose()

    # 2. Tabeller – en kandidat per kolumn
    for ti, (rubrik, rader) in enumerate(tabeller(soup), 1):
        for ci in range(max(len(r) for r in rader)):
            namn = rubrik[ci] if ci < len(rubrik) and rubrik[ci] else f"kolumn {ci + 1}"
            ut.append((f"tabell {ti}, kolumn {ci + 1} \"{namn}\"",
                       [r[ci] for r in rader if ci < len(r)]))

    # 3. Punkt- och numrerade listor
    for li_i, lst in enumerate(soup.find_all(["ol", "ul"]), 1):
        poster = [li.get_text(" ") for li in lst.find_all("li", recursive=False)]
        if len(poster) >= 5:
            ut.append((f"{lst.name}-lista {li_i}", poster))

    # 4. Rubriker (vanligt på "topp 100"-artiklar)
    for niva in ("h2", "h3", "h4"):
        rub = [h.get_text(" ") for h in soup.find_all(niva)]
        if len(rub) >= 5:
            ut.append((f"alla {niva}-rubriker", rub))

    ut = [(namn, unika(v)) for namn, v in ut]
    ut = [(namn, v) for namn, v in ut if len(v) >= 3 and ser_bra_ut(v)]
    ut.sort(key=lambda x: -len(x[1]))

    # 5. Upprepade element med samma klass (kort i rutnät, citat, produktkort …).
    #    Läggs sist så att tabeller och listor behåller sina nummer.
    grupper: dict[str, list[str]] = {}
    for el in soup.find_all(class_=True):
        if el.name in ("html", "body", "main", "section"):
            continue
        nyckel = f"{el.name}.{el.get('class')[0]}"
        grupper.setdefault(nyckel, []).append(el.get_text(" "))
    upprepade = [(f'element {k} (--selektor "{k}")', unika(v))
                 for k, v in grupper.items() if len(v) >= 5]
    upprepade = [(namn, v) for namn, v in upprepade if len(v) >= 3 and ser_bra_ut(v)]
    upprepade.sort(key=lambda x: -len(x[1]))
    return ut + upprepade


def tabellkolumner(soup: BeautifulSoup, tabellnr: int, kolumner: list[int],
                   skiljetecken: str) -> list[str]:
    """Slår ihop valda kolumner ur en tabell, t.ex. namn + årtal för Tidslinjen."""
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    for s in soup.select(BRUS):
        s.decompose()
    # Dolda element, t.ex. Wikipedias sorteringsvärden "&&&&032629.&&0" före "32 629"
    for s in soup.find_all(style=re.compile(r"display\s*:\s*none")):
        s.decompose()
    tabs = tabeller(soup)
    if not 1 <= tabellnr <= len(tabs):
        sys.exit(f"Sidan har {len(tabs)} tabeller; tabell {tabellnr} finns inte.")
    _, rader = tabs[tabellnr - 1]
    ut = []
    for r in rader:
        delar = [r[k - 1] for k in kolumner if k - 1 < len(r) and r[k - 1]]
        if len(delar) == len(kolumner):
            ut.append(skiljetecken.join(delar))
    return unika(ut)


def sidor(kalla: str, nasta: str | None, forsta: int, maxsidor: int, paus: float):
    """Går igenom en lista som är uppdelad på flera sidor.

    Två sätt: en URL med {sida} där sidnumret ska stå (…?page={sida}), eller en
    CSS-selektor för "nästa sida"-länken (--nasta). Annars bara en sida.
    """
    if "{sida}" in kalla:
        for nr in range(forsta, forsta + maxsidor):
            html, _ = hamta(kalla.replace("{sida}", str(nr)), tyst_fel=nr > forsta)
            if html is None:
                return
            yield BeautifulSoup(html, "lxml"), nr
            time.sleep(paus)
        return
    for nr in range(1, maxsidor + 1):
        html, bas = hamta(kalla)
        soup = BeautifulSoup(html, "lxml")
        lank = soup.select_one(nasta) if nasta else None
        yield soup, nr
        if not lank or not lank.get("href") or not bas:
            return
        kalla = urllib.parse.urljoin(bas, lank["href"])
        time.sleep(paus)


# ---------------------------------------------------------------- IMDb

IMDB_BAS = "https://datasets.imdbws.com/"


def imdb(args) -> list[str]:
    """Bygger en topplista ur IMDb:s officiella datafiler (datasets.imdbws.com).

    OBS: IMDb publicerar inte exakt hur deras egen "Top 1000" väljs. Listan här
    sorteras på snittbetyg (och antal röster vid lika), bland titlar med minst
    --minroster röster. Den blir nära men inte garanterat identisk med IMDb:s.
    """
    mapp = args.cache
    os.makedirs(mapp, exist_ok=True)
    for f in ("title.ratings.tsv.gz", "title.basics.tsv.gz"):
        vag = os.path.join(mapp, f)
        if not os.path.exists(vag) or time.time() - os.path.getmtime(vag) > 86400:
            print(f"  laddar ner {f} …", file=sys.stderr)
            urllib.request.urlretrieve(IMDB_BAS + f, vag)
    betyg = {}
    with gzip.open(os.path.join(mapp, "title.ratings.tsv.gz"), "rt", encoding="utf-8") as f:
        next(f)
        for rad in f:
            tid, snitt, roster = rad.rstrip("\n").split("\t")
            if int(roster) >= args.minroster:
                betyg[tid] = (float(snitt), int(roster))
    typer = set(args.typ.split(","))
    titlar = []
    with gzip.open(os.path.join(mapp, "title.basics.tsv.gz"), "rt", encoding="utf-8") as f:
        next(f)
        for rad in f:
            p = rad.rstrip("\n").split("\t")
            if p[0] in betyg and p[1] in typer:
                titel = p[3] if args.originaltitel else p[2]
                ar = p[5] if p[5] != "\\N" else "?"
                titlar.append((titel, ar, *betyg[p[0]]))
    titlar.sort(key=lambda t: (-t[2], -t[3]))
    return [f"{t} ({ar})" if args.med_ar else t for t, ar, _, _ in titlar[:args.antal]]


# ---------------------------------------------------------------- main

def spara(rader: list[str], ut: str | None) -> None:
    text = "\n".join(rader) + "\n"
    if ut:
        with open(ut, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Sparade {len(rader)} rader i {ut}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kalla", help="URL, lokal HTML-fil, eller ordet 'imdb'")
    ap.add_argument("--ut", help="txt-fil att spara till (annars skrivs listan ut)")
    ap.add_argument("--visa", action="store_true", help="visa kandidatlistor och avsluta")
    ap.add_argument("--kandidat", type=int, default=1, help="vilken kandidat som ska sparas")
    ap.add_argument("--selektor", help="CSS-selektor för posterna, t.ex. 'h3.title'")
    ap.add_argument("--nasta", help="CSS-selektor för 'nästa sida'-länken")
    ap.add_argument("--maxsidor", type=int, default=50)
    ap.add_argument("--forsta-sida", type=int, default=1, help="första sidnumret vid {sida}")
    ap.add_argument("--paus", type=float, default=2.0, help="sekunder mellan sidor")
    ap.add_argument("--max", type=int, help="högst så här många rader")
    ap.add_argument("--webblasare", action="store_true",
                    help="öppna sidan i en webbläsare och klicka 'Visa fler'/scrolla tills allt laddats")
    ap.add_argument("--max-rundor", type=int, default=0, help="högst så många klick/scrollningar")
    ap.add_argument("--tabell", type=int, help="tabellnummer (se --visa)")
    ap.add_argument("--kolumner", help="kolumnnummer att slå ihop, t.ex. 2,4")
    ap.add_argument("--skiljetecken", default=" – ")
    # IMDb
    ap.add_argument("--antal", type=int, default=1000)
    ap.add_argument("--minroster", type=int, default=25000)
    ap.add_argument("--typ", default="movie", help="IMDb-titeltyp(er), t.ex. movie,tvSeries")
    ap.add_argument("--originaltitel", action="store_true")
    ap.add_argument("--utan-ar", dest="med_ar", action="store_false")
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/listskapare"))
    args = ap.parse_args()
    global WEBBLASARE, MAX_RUNDOR
    WEBBLASARE, MAX_RUNDOR = args.webblasare, args.max_rundor

    if args.kalla == "imdb":
        rader = imdb(args)
    else:
        kol = [int(k) for k in (args.kolumner or "1").split(",")]
        rader, anvand, forra = [], None, None
        for soup, nr in sidor(args.kalla, args.nasta, args.forsta_sida, args.maxsidor, args.paus):
            if args.selektor:
                nya = unika([e.get_text(" ") for e in soup.select(args.selektor)])
            elif args.tabell:
                nya = tabellkolumner(soup, args.tabell, kol, args.skiljetecken)
            else:
                kand = kandidater(soup)
                if not kand:
                    sys.exit("Hittade inga listor. Prova --selektor.")
                if args.visa:
                    for i, (namn, v) in enumerate(kand[:20], 1):
                        prov = " | ".join(x if len(x) <= 40 else x[:39] + "…" for x in v[:4])
                        print(f"{i:>2}. {namn} – {len(v)} poster: {prov} …")
                    return
                namn, nya = kand[min(args.kandidat, len(kand)) - 1]
                if anvand is None:
                    anvand = namn
                    print(f"Använder: {namn}", file=sys.stderr)
            antal_fore = len(rader)
            rader = unika(rader + nya)
            print(f"  sida {nr}: {len(nya)} poster, {len(rader) - antal_fore} nya", file=sys.stderr)
            if not nya or nya == forra:
                print("  tom sida eller samma som förra, slutar", file=sys.stderr)
                break
            forra = nya

    if args.max:
        rader = rader[:args.max]
    spara(rader, args.ut)


if __name__ == "__main__":
    main()
