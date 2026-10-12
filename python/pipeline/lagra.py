"""Steg 5. Spara den validerade tabellen.

Tabellen sparas som Parquet, som CSV för kalkylprogram och i en
DuckDB-databas, tillsammans med en beskrivning av källorna.
Motsvarar notebook 09.
"""

import json

import duckdb

from gemensamt import DATA, HARMONISERAD


def beskrivning(tabell):
    return {
        "fil": "webbplatser.parquet",
        "beskrivning": "En rad per webbplats för Sveriges kommuner och regioner, med betyg, fältdata, befolkning och bredband.",
        "licens": "CC BY-SA 4.0",
        "kallor": [
            {"namn": "Webperf", "url": "https://api.webperf.se", "licens": "CC BY-SA 4.0",
             "hamtad": str(tabell["hamtad"].min())},
            {"namn": "Wikidata", "url": "https://www.wikidata.org", "licens": "CC0",
             "hamtad": str(tabell["hamtad_wikidata"].min())},
            {"namn": "Chrome UX Report", "url": "https://developer.chrome.com/docs/crux", "licens": "CC BY 4.0",
             "hamtad": str(tabell["hamtad_crux"].min())},
            {"namn": "Kolada", "url": "https://www.kolada.se", "licens": "se kolada.se",
             "ar": int(tabell["kolada_ar"].iloc[0])},
        ],
    }


def lagra(tabell):
    HARMONISERAD.mkdir(parents=True, exist_ok=True)

    parquet = HARMONISERAD / "webbplatser.parquet"
    tabell.to_parquet(parquet, index=False)

    tabell.to_csv(
        HARMONISERAD / "webbplatser-kalkylark.csv",
        index=False, sep=";", decimal=",", encoding="utf-8-sig",
    )

    with duckdb.connect(str(DATA / "webbanalys.duckdb")) as databas:
        databas.sql(f"CREATE OR REPLACE TABLE webbplatser AS SELECT * FROM read_parquet('{parquet}')")

    text = json.dumps(beskrivning(tabell), ensure_ascii=False, indent=2)
    (HARMONISERAD / "om-datan.json").write_text(text, encoding="utf-8")

    print(f"  Sparat i {HARMONISERAD.relative_to(DATA.parent)} och {DATA.name}/webbanalys.duckdb")
