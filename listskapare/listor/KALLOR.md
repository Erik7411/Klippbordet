# Källor för listorna

| Fil | Källa | Hämtad | Metod | Anmärkning |
|---|---|---|---|---|
| `imdb-topp-1000.txt` | IMDb:s officiella datafiler, `title.ratings.tsv.gz` och `title.basics.tsv.gz` från datasets.imdbws.com | 2026-11-25 | `listskapare.py imdb --antal 1000` | Titeltyp `movie` med minst 25 000 röster, sorterade på snittbetyg och vid lika betyg på antal röster. **Ingen kopia av IMDb:s egen "Top 1000"**: IMDb redovisar inte hur den listan väljs ut, och www.imdb.com blockerade hämtningen (403). Titlarna är IMDb:s huvudtitlar (oftast engelska), med premiärår. Några titlar ligger högt efter röstkampanjer, t.ex. *The Chaos Class* (1975) på plats 4 och *You Can See Everything* (2026) på plats 9; de bör granskas före användning. Datafilerna får enligt IMDb användas "for personal and non-commercial use" (data.imdb.com/non-commercial-datasets); om det täcker användningen i ett tv-program har jag inte kunnat bedöma. |
