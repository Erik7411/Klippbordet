"""Gör om ett webbläsarskript till ett bokmärke.

    python3 gor-bokmarke.py ladda-allt.js

Skriver ladda-allt.bokmarke.txt (adressen att klistra in) och, för ladda-allt.js, även
../bokmarke.html: en sida med en knapp att dra till bokmärkesfältet.
"""
import html
import os
import re
import sys
import urllib.parse

SIDA = """<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Installera Listskapare</title>
<style>
  :root{color-scheme:light dark;--bg:light-dark(#fff,#071318);--ink:light-dark(#0b1f27,#e8f4f3);
    --mut:light-dark(#4a5f66,#9fbcbc);--teal:light-dark(#0a8f86,#3fd2c6);--pan:light-dark(#eaf6f5,#0d252c)}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 system-ui,"Segoe UI",sans-serif;
    padding:clamp(24px,6vw,64px) max(5vw,16px)}
  main{max-width:640px;margin:0 auto}
  h1{font-size:clamp(30px,5vw,42px);line-height:1.1;margin:0 0 12px}
  p{margin:0 0 16px}
  .dra{display:inline-block;margin:12px 0 20px;padding:16px 26px;border-radius:12px;background:var(--teal);
    color:#fff;font-weight:700;font-size:20px;text-decoration:none;cursor:grab;border:3px dashed transparent}
  .dra:active{cursor:grabbing}
  .not{background:var(--pan);border-radius:10px;padding:14px 16px;color:var(--mut);font-size:15px}
  kbd{font:14px ui-monospace,Menlo,monospace;border:1px solid var(--mut);border-radius:5px;padding:0 5px}
  #svar{min-height:1.5em;color:var(--teal);font-weight:600}
</style>
</head>
<body>
<main>
  <h1>Installera Listskapare</h1>
  <p>Dra knappen nedan upp till bokmärkesfältet i webbläsaren. Det är allt.</p>
  <p>Syns inget bokmärkesfält: tryck <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd>
     (Mac: <kbd>⌘</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd>).</p>
  <a class="dra" id="dra" href="{bokmarke}" title="Dra mig till bokmärkesfältet">Listskapare</a>
  <p id="svar" aria-live="polite"></p>
  <p><b>Använd det så här:</b> öppna en lista, till exempel en topplista på IMDb, och klicka på
     bokmärket. Det klickar "Visa fler" och scrollar tills allt har laddats. IMDb-listor sparas
     direkt som en .txt-fil, en titel per rad. Andra sidor sparas som en .html-fil som du skickar
     till Claude.</p>
  <p class="not">Bokmärket körs bara när du klickar på det, och bara på sidan du har öppen.
     Det skickar inget någonstans: filen hamnar bland dina hämtade filer.</p>
</main>
<script>
  document.getElementById('dra').addEventListener('click', function (e) {
    e.preventDefault();
    document.getElementById('svar').textContent = 'Dra knappen till bokmärkesfältet i stället för att klicka på den.';
  });
</script>
</body>
</html>
"""


def bokmarke(vag: str) -> str:
    rader = []
    for rad in open(vag, encoding="utf-8").read().splitlines():
        rad = re.sub(r"\s+//\s.*$", "", rad).strip()
        if rad and not rad.startswith("//"):
            rader.append(rad)
    return "javascript:" + urllib.parse.quote(" ".join(rader), safe="(){}[]=>;:,.'`$*+?!|/^\\-_~&<")


for vag in sys.argv[1:]:
    bm = bokmarke(vag)
    ut = vag.removesuffix(".js") + ".bokmarke.txt"
    open(ut, "w", encoding="utf-8").write(bm + "\n")
    print(f"{ut}: {len(bm)} tecken")
    if os.path.basename(vag) == "ladda-allt.js":
        sida = os.path.join(os.path.dirname(os.path.abspath(vag)), "..", "bokmarke.html")
        open(sida, "w", encoding="utf-8").write(SIDA.replace("{bokmarke}", html.escape(bm, quote=True)))
        print(f"{os.path.normpath(sida)}: installationssida")
