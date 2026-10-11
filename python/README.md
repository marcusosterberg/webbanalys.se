# Python för webbanalys

Här finns koden till artikelserien om Python för webbanalys på [webbanalys.se](https://webbanalys.se). Serien visar hur vi själva hämtar, tvättar, harmoniserar och analyserar data, steg för steg, så att vi förstår och kan granska varje led i arbetet.

Genom hela serien jämför vi olika mätmetoders data om samma webbplatser, nämligen Sveriges kommuner och regioner. Webperfs automatiserade tester och fältdata från riktiga besökare i CrUX mäter på olika sätt, medan Wikidata och Kolada ger sammanhang om kommunerna.

## Innehåll

Varje notebook hör till en artikel i serien och är numrerad i samma ordning.

| Notebook | Artikel |
| --- | --- |
| `01-miljo` | Arbetsmiljön |
| `02-inspektera` | Inspektera innan vi läser in |
| `03-hamta-webperf` | Hämta från ett API |
| `04-wikidata` | Berika med länkade data |
| `05-crux` | Fältdata från riktiga besökare |
| `06-tvatta` | Tvätta data |
| `07-harmonisera` | Harmonisera och slå ihop |
| `08-validera` | Validera |
| `09-lagra` | Lagra |
| `10-analys` | Analysera och visa |
| `11-pipeline` | Från notebook till pipeline |

Skripten från den sista artikeln hamnar i mappen `pipeline`.

## Kom igång

Vi använder [uv](https://docs.astral.sh/uv/) för att installera Python och hålla beroendena låsta, så att allt fungerar likadant över tid.

```sh
cd python
uv sync
uv run jupyter lab
```

Starta sedan med `notebooks/01-miljo.ipynb`. En god vana är att alltid välja att starta om och köra alla celler innan vi litar på ett resultat.

## API-nyckel till CrUX

Notebook 05 hämtar data från Chrome UX Report och kräver en kostnadsfri API-nyckel från Google. Nyckeln läses från miljövariabeln `CRUX_API_KEY` och ska aldrig checkas in.

```sh
export CRUX_API_KEY="din-nyckel"
```

## Data

Ingen data från källorna finns i repot. Vi hämtar själva, vilket också är en del av lektionerna. Allt som hamnar i `data/` ignoreras av git.

## Källor och licenser

Koden är licensierad under MIT, se [LICENSE](LICENSE).

Datakällorna har egna villkor som gäller när vi publicerar resultat byggda på dem.

- [Webperfs öppna data](https://api.webperf.se) är licensierade under CC BY-SA 4.0. Ange Webperf som källa och dela bearbetningar under samma licens.
- [Wikidata](https://www.wikidata.org) är CC0.
- [Kolada](https://www.kolada.se) och [Chrome UX Report](https://developer.chrome.com/docs/crux) har egna villkor som behöver kontrolleras innan resultat publiceras.
