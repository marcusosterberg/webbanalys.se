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

Använder du VS Code i stället för JupyterLab behöver notebooken köras med projektets Python. Klicka på **Select Kernel**, välj **Python Environments** och välj den i `python/.venv`. Notebook 01 kontrollerar att valet blev rätt.

Starta sedan med `notebooks/01-miljo.ipynb`. En god vana är att alltid välja att starta om och köra alla celler innan vi litar på ett resultat.

## Output checkas inte in

Notebooks i repot sparas utan output, eftersom resultatet beror på när vi hämtade data. Den som gör commits tar bort output automatiskt med [nbstripout](https://github.com/kynan/nbstripout). Filen `.gitattributes` pekar ut filtret, men själva kommandot behöver läggas in en gång per klon. Kör följande i repots rotmapp.

```sh
git config filter.nbstripout.clean "uvx --from nbstripout==0.9.1 nbstripout --extra-keys metadata.language_info"
git config filter.nbstripout.smudge cat
git config filter.nbstripout.required true
git config diff.ipynb.textconv "uvx --from nbstripout==0.9.1 nbstripout -t"
```

Output finns kvar i våra egna notebooks men kommer inte med i någon commit.

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
