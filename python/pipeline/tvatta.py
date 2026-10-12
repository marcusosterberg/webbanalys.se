"""Steg 2. Gör om rådatan till en tvättad tabell per källa.

Tabellerna sparas som Parquet i data/tvattad. Inget hämtas här.
Motsvarar notebook 06 och tvättningen av Kolada i notebook 07.
"""

import pandas as pd

from gemensamt import KOLADA_AR, TVATTAD, las_radata, sista_delen, till_origin

KOLADA_KOLUMNER = {"N90002": "bredband_ned_mbit_s", "N01951": "invanare_kolada"}


def tvatta_webperf():
    kommuner_fil = las_radata("webperf-kommuner.json")
    regioner_fil = las_radata("webperf-regioner.json")

    kommuner = pd.json_normalize(kommuner_fil["svar"]["municipalities"])
    regioner = pd.json_normalize(regioner_fil["svar"]["regions"])
    kommuner["typ"] = "kommun"
    regioner["typ"] = "region"
    webperf = pd.concat([kommuner, regioner], ignore_index=True)

    webperf = webperf.rename(columns={
        "id": "webperf_id",
        "title": "namn",
        "website": "webbplats",
        "same_as": "wikidata_url",
        "ratings.overall": "betyg_totalt",
        "ratings.accessibility": "betyg_tillganglighet",
        "ratings.performance": "betyg_prestanda",
        "ratings.security": "betyg_sakerhet",
        "ratings.standards": "betyg_standard",
    })
    webperf = webperf[[
        "webperf_id", "namn", "typ", "webbplats", "wikidata_url",
        "betyg_totalt", "betyg_tillganglighet", "betyg_prestanda", "betyg_sakerhet", "betyg_standard",
    ]]

    webperf["qid"] = sista_delen(webperf["wikidata_url"])
    webperf["origin"] = webperf["webbplats"].map(till_origin)
    webperf["hamtad"] = pd.Timestamp(kommuner_fil["hamtad"])

    for nyckel in ["webperf_id", "qid", "origin"]:
        if not webperf[nyckel].is_unique:
            raise ValueError(f"{nyckel} är inte unik i Webperfs data")
    return webperf


def wikidata_tabell(filnamn):
    fil = las_radata(filnamn)
    rader = [{namn: varde["value"] for namn, varde in traff.items()} for traff in fil["svar"]["results"]["bindings"]]
    tabell = pd.DataFrame(rader)
    if "item" in tabell.columns:
        tabell["qid"] = sista_delen(tabell["item"])
        tabell = tabell.drop(columns="item")
    return tabell, fil["hamtad"]


def tvatta_wikidata():
    kommunkod, hamtad = wikidata_tabell("wikidata-kommunkod.json")
    lan, _ = wikidata_tabell("wikidata-lan.json")
    befolkning, _ = wikidata_tabell("wikidata-befolkning.json")
    lan_befolkning, _ = wikidata_tabell("wikidata-lan-befolkning.json")

    lan = lan.rename(columns={"lanLabel": "lan"})

    befolkning = befolkning.rename(columns={"tidpunkt": "befolkning_datum"})
    befolkning["befolkning"] = befolkning["befolkning"].astype("Int64")
    befolkning["befolkning_datum"] = pd.to_datetime(befolkning["befolkning_datum"].str[:10])

    lan_befolkning = lan_befolkning.rename(columns={"lan_tidpunkt": "lan_befolkning_datum"})
    lan_befolkning["lan_befolkning"] = lan_befolkning["lan_befolkning"].astype("Int64")
    lan_befolkning["lan_befolkning_datum"] = pd.to_datetime(lan_befolkning["lan_befolkning_datum"].str[:10])

    wikidata = (
        lan
        .merge(kommunkod, on="qid", how="left")
        .merge(befolkning, on="qid", how="left")
        .merge(lan_befolkning, on="lanskod", how="left")
    )
    wikidata = wikidata[[
        "qid", "kommunkod", "lan", "lanskod", "befolkning", "befolkning_datum",
        "lan_befolkning", "lan_befolkning_datum",
    ]]
    wikidata["hamtad"] = pd.Timestamp(hamtad)

    if not wikidata["qid"].is_unique:
        raise ValueError("qid är inte unik i Wikidatas data")
    return wikidata


def crux_rad(origin, status, svar):
    rad = {"origin": origin, "crux_status": status}
    if status != 200:
        return rad
    matt = svar["record"]["metrics"]
    period = svar["record"]["collectionPeriod"]
    for namn, kolumn in [
        ("largest_contentful_paint", "lcp_p75_ms"),
        ("interaction_to_next_paint", "inp_p75_ms"),
        ("cumulative_layout_shift", "cls_p75"),
    ]:
        if namn in matt:
            rad[kolumn] = matt[namn]["percentiles"]["p75"]
    rad["period_start"] = "{year}-{month:02d}-{day:02d}".format(**period["firstDate"])
    rad["period_slut"] = "{year}-{month:02d}-{day:02d}".format(**period["lastDate"])
    return rad


def tvatta_crux():
    fil = las_radata("crux.json")
    rader = [crux_rad(origin, post["status"], post["svar"]) for origin, post in fil["svar"].items()]
    crux = pd.DataFrame(rader)

    crux["lcp_p75_ms"] = crux["lcp_p75_ms"].astype("Int64")
    crux["inp_p75_ms"] = crux["inp_p75_ms"].astype("Int64")
    crux["cls_p75"] = pd.to_numeric(crux["cls_p75"])
    crux["period_start"] = pd.to_datetime(crux["period_start"])
    crux["period_slut"] = pd.to_datetime(crux["period_slut"])
    crux["hamtad"] = pd.Timestamp(fil["hamtad"])
    return crux


def kolada_tabell(svar, kolumn):
    """Värdet totalt, T, för varje kommun och region. Grupper med id som G... och riket, 0000, tas bort."""
    rader = []
    for post in svar["values"]:
        kolada_id = post["municipality"]
        if len(kolada_id) != 4 or kolada_id == "0000":
            continue
        for varde in post["values"]:
            if varde["gender"] == "T":
                rader.append({"kolada_id": kolada_id, kolumn: varde["value"]})
    return pd.DataFrame(rader)


def tvatta_kolada():
    kolada = None
    for nyckeltal, kolumn in KOLADA_KOLUMNER.items():
        svar = las_radata(f"kolada-{nyckeltal}-{KOLADA_AR}.json")["svar"]
        tabell = kolada_tabell(svar, kolumn)
        kolada = tabell if kolada is None else kolada.merge(tabell, on="kolada_id", how="outer")

    kolada["invanare_kolada"] = kolada["invanare_kolada"].astype("Int64")
    kolada["kolada_ar"] = KOLADA_AR

    if not kolada["kolada_id"].is_unique:
        raise ValueError("kolada_id är inte unik i Koladas data")
    return kolada


def tvatta_allt():
    TVATTAD.mkdir(parents=True, exist_ok=True)
    for namn, funktion in [
        ("webperf", tvatta_webperf),
        ("wikidata", tvatta_wikidata),
        ("crux", tvatta_crux),
        ("kolada", tvatta_kolada),
    ]:
        tabell = funktion()
        tabell.to_parquet(TVATTAD / f"{namn}.parquet", index=False)
        print(f"  {namn}: {len(tabell)} rader")
