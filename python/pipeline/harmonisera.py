"""Steg 3. Harmonisera de tvättade tabellerna och slå ihop dem.

Resultatet är en tabell med en rad per webbplats. Den sparas först efter
valideringen, i steget lagra. Motsvarar notebook 07.
"""

import pandas as pd

from gemensamt import TVATTAD

KOLUMNER = [
    "webperf_id", "namn", "typ", "webbplats", "origin",
    "qid", "kommunkod", "kolada_id", "lan", "lanskod",
    "befolkning", "befolkning_datum", "befolkning_avser", "invanare_kolada",
    "betyg_totalt", "betyg_tillganglighet", "betyg_prestanda", "betyg_sakerhet", "betyg_standard",
    "crux_status", "lcp_p75_ms", "inp_p75_ms", "cls_p75", "period_start", "period_slut",
    "bredband_ned_mbit_s", "kolada_ar",
    "hamtad", "hamtad_wikidata", "hamtad_crux",
]


def koppla(vanster, hoger, nyckel, **installningar):
    """Slår ihop två tabeller och avbryter om någon rad saknar träff eller får flera."""
    tabell = vanster.merge(hoger, on=nyckel, how="left", indicator=True, **installningar)
    utan_traff = (tabell["_merge"] != "both").sum()
    if utan_traff or len(tabell) != len(vanster):
        raise ValueError(f"Sammanslagningen på {nyckel} gav {utan_traff} rader utan träff eller fel antal rader")
    return tabell.drop(columns="_merge")


def harmonisera():
    webperf = pd.read_parquet(TVATTAD / "webperf.parquet")
    wikidata = pd.read_parquet(TVATTAD / "wikidata.parquet")
    crux = pd.read_parquet(TVATTAD / "crux.parquet")
    kolada = pd.read_parquet(TVATTAD / "kolada.parquet")

    tabell = koppla(webperf, wikidata, "qid", suffixes=("", "_wikidata"))

    # Koladas id är kommunkoden för kommuner och 00 plus länskoden för regioner
    tabell["kolada_id"] = tabell["kommunkod"].where(tabell["typ"] == "kommun", "00" + tabell["lanskod"])

    # Regionerna får länets befolkning
    ar_kommun = tabell["typ"] == "kommun"
    tabell["befolkning"] = tabell["befolkning"].where(ar_kommun, tabell["lan_befolkning"])
    tabell["befolkning_datum"] = tabell["befolkning_datum"].where(ar_kommun, tabell["lan_befolkning_datum"])
    tabell["befolkning_avser"] = "kommunen"
    tabell.loc[~ar_kommun, "befolkning_avser"] = "länet"
    tabell = tabell.drop(columns=["lan_befolkning", "lan_befolkning_datum"])

    tabell = koppla(tabell, crux, "origin", suffixes=("", "_crux"))
    tabell = koppla(tabell, kolada, "kolada_id")

    webbplatser = tabell[KOLUMNER]
    print(f"  {len(webbplatser)} webbplatser")
    return webbplatser
