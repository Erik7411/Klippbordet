"""Gör om ett webbläsarskript till ett bokmärke: python3 gor-bokmarke.py ladda-allt.js"""
import re
import sys
import urllib.parse

for vag in sys.argv[1:]:
    rader = []
    for rad in open(vag, encoding="utf-8").read().splitlines():
        rad = re.sub(r"\s+//\s.*$", "", rad).strip()
        if rad and not rad.startswith("//"):
            rader.append(rad)
    bokmarke = "javascript:" + urllib.parse.quote(" ".join(rader), safe="(){}[]=>;:,.'`$*+?!|/^\\-_~&<")
    ut = vag.removesuffix(".js") + ".bokmarke.txt"
    open(ut, "w", encoding="utf-8").write(bokmarke + "\n")
    print(f"{ut}: {len(bokmarke)} tecken")
