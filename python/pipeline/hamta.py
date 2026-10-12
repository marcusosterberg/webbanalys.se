"""Steg 1. Hämta data från Webperf, Wikidata, CrUX och Kolada.

Svaren sparas som de kom i data/radata, tillsammans med när de hämtades.
Motsvarar notebook 03, 04, 05 och början av 07.
"""

import os
import time

import httpx
import pandas as pd
from dotenv import load_dotenv

from gemensamt import KOLADA_AR, ROT, USER_AGENT, nu, sista_delen, spara_radata, till_origin, webperf_platser

WEBPERF = "https://api.webperf.se"
WIKIDATA = "https://query.wikidata.org/sparql"
CRUX = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"
KOLADA = "https://api.kolada.se/v3"

CRUX_MATT = ["largest_contentful_paint", "interaction_to_next_paint", "cumulative_layout_shift"]
KOLADA_NYCKELTAL = ["N90002", "N01951"]

# Frågorna till Wikidata. ALLA_QID byts ut mot listan med id-nummer.
WIKIDATA_FRAGOR = {
    "kommunkod": """
SELECT ?item ?kommunkod WHERE {
  VALUES ?item { ALLA_QID }
  ?item p:P525 ?pastaende .
  ?pastaende ps:P525 ?kommunkod .
  FILTER NOT EXISTS { ?pastaende pq:P582 ?slutdatum . }
}
""",
    "lan": """
SELECT DISTINCT ?item ?lanLabel ?lanskod WHERE {
  VALUES ?item { ALLA_QID }
  { ?item wdt:P131 ?lan . } UNION { ?lan wdt:P150 ?item . }
  ?lan wdt:P31 wd:Q200547 ;
       wdt:P507 ?lanskod .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "sv". }
}
""",
    "befolkning": """
SELECT ?item ?befolkning ?tidpunkt WHERE {
  VALUES ?item { ALLA_QID }
  ?item p:P1082 ?pastaende .
  ?pastaende a wikibase:BestRank ;
             ps:P1082 ?befolkning .
  OPTIONAL { ?pastaende pq:P585 ?tidpunkt . }
}
""",
    "lan-befolkning": """
SELECT ?lanskod ?lan_befolkning ?lan_tidpunkt WHERE {
  ?lan wdt:P31 wd:Q200547 ;
       wdt:P507 ?lanskod ;
       p:P1082 ?pastaende .
  ?pastaende a wikibase:BestRank ;
             ps:P1082 ?lan_befolkning .
  OPTIONAL { ?pastaende pq:P585 ?lan_tidpunkt . }
}
""",
}


def hamta_webperf():
    hamtad = nu()
    for namn, sokvag in [("kommuner", "/v1/public/municipalities"), ("regioner", "/v1/public/regions")]:
        svar = httpx.get(WEBPERF + sokvag, headers={"User-Agent": USER_AGENT}, timeout=30)
        svar.raise_for_status()
        spara_radata(f"webperf-{namn}.json", {"hamtad": hamtad, "kalla": WEBPERF, "svar": svar.json()})
    print("  Webperf klart")


def hamta_wikidata():
    qid = sista_delen(pd.Series([plats["same_as"] for plats in webperf_platser()]))
    alla_qid = " ".join("wd:" + q for q in qid)
    hamtad = nu()
    for namn, mall in WIKIDATA_FRAGOR.items():
        fraga = mall.replace("ALLA_QID", alla_qid)
        svar = httpx.post(
            WIKIDATA,
            data={"query": fraga, "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=120,
        )
        svar.raise_for_status()
        paket = {"hamtad": hamtad, "kalla": WIKIDATA, "fraga": fraga, "svar": svar.json()}
        spara_radata(f"wikidata-{namn}.json", paket)
    print("  Wikidata klart")


def hamta_crux():
    load_dotenv(ROT / ".env")
    nyckel = os.environ.get("CRUX_API_KEY")
    if not nyckel:
        raise RuntimeError("CRUX_API_KEY saknas. Lägg den i python/.env enligt README.")

    origins = [till_origin(plats["website"]) for plats in webperf_platser()]
    svar_per_origin = {}
    with httpx.Client(headers={"X-Goog-Api-Key": nyckel}, timeout=30) as klient:
        for origin in origins:
            svar = klient.post(CRUX, json={"origin": origin, "metrics": CRUX_MATT})
            if svar.status_code not in (200, 404):
                svar.raise_for_status()
            svar_per_origin[origin] = {"status": svar.status_code, "svar": svar.json()}
            # CrUX tillåter 150 frågor per minut
            time.sleep(0.5)

    paket = {"hamtad": nu(), "kalla": CRUX, "matt": CRUX_MATT, "svar": svar_per_origin}
    spara_radata("crux.json", paket)
    print("  CrUX klart,", len(svar_per_origin), "origin")


def hamta_kolada():
    hamtad = nu()
    for nyckeltal in KOLADA_NYCKELTAL:
        svar = httpx.get(f"{KOLADA}/data/kpi/{nyckeltal}/year/{KOLADA_AR}", timeout=60)
        svar.raise_for_status()
        innehall = svar.json()
        if innehall["next_url"]:
            raise RuntimeError(f"Kolada delade upp svaret för {nyckeltal} i sidor, vilket koden inte hanterar.")
        paket = {"hamtad": hamtad, "kalla": KOLADA, "nyckeltal": nyckeltal, "ar": KOLADA_AR, "svar": innehall}
        spara_radata(f"kolada-{nyckeltal}-{KOLADA_AR}.json", paket)
    print("  Kolada klart")


def hamta_allt():
    hamta_webperf()
    hamta_wikidata()
    hamta_crux()
    hamta_kolada()
