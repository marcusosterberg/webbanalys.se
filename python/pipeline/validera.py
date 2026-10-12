"""Steg 4. Pröva den sammanslagna tabellen mot reglerna från notebook 08.

Om någon regel inte håller avbryts pipelinen, så att ingen data som
inte klarat valideringen sparas.
"""

import pandas as pd

from gemensamt import KOLADA_AR, las_radata

BETYG = ["betyg_totalt", "betyg_tillganglighet", "betyg_prestanda", "betyg_sakerhet", "betyg_standard"]


def sveriges_befolkning():
    """Sveriges befolkning från Kolada, där riket har id 0000."""
    for post in las_radata(f"kolada-N01951-{KOLADA_AR}.json")["svar"]["values"]:
        if post["municipality"] == "0000":
            for varde in post["values"]:
                if varde["gender"] == "T":
                    return varde["value"]
    raise ValueError("Sveriges befolkning saknas i Koladas data")


def kontroller(tabell):
    """Alla regler som par av namn och villkor."""
    ar_kommun = tabell["typ"] == "kommun"
    ar_region = tabell["typ"] == "region"
    saknar_kommunkod = tabell["kommunkod"].isna()
    har_crux = tabell["crux_status"] == 200
    med_kod = tabell[~saknar_kommunkod]
    skillnad = (tabell["befolkning"] - tabell["invanare_kolada"]) / tabell["invanare_kolada"] * 100
    sverige = sveriges_befolkning()
    summa_regioner = tabell.loc[ar_region, "befolkning"].sum()

    regler = [
        ("289 kommuner", ar_kommun.sum() == 289),
        ("21 regioner", ar_region.sum() == 21),
    ]
    for nyckel in ["webperf_id", "qid", "origin", "kolada_id"]:
        regler.append((f"{nyckel} är unik", tabell[nyckel].is_unique))

    regler += [
        ("kommunkod har fyra siffror", tabell["kommunkod"].dropna().str.fullmatch(r"\d{4}").all()),
        ("kolada_id har fyra siffror", tabell["kolada_id"].str.fullmatch(r"\d{4}").all()),
        ("lanskod har två siffror", tabell["lanskod"].str.fullmatch(r"\d{2}").all()),
        ("origin börjar med https://", tabell["origin"].str.startswith("https://").all()),
    ]
    for kolumn in BETYG:
        regler.append((f"{kolumn} mellan 1 och 5", tabell[kolumn].dropna().between(1, 5).all()))

    regler += [
        ("lcp_p75_ms större än noll", (tabell["lcp_p75_ms"].dropna() > 0).all()),
        ("inp_p75_ms större än noll", (tabell["inp_p75_ms"].dropna() > 0).all()),
        ("cls_p75 inte negativ", (tabell["cls_p75"].dropna() >= 0).all()),
        ("bredband större än noll", (tabell["bredband_ned_mbit_s"] > 0).all()),
        ("befolkning större än noll", (tabell["befolkning"] > 0).all()),
        ("bara regioner saknar kommunkod", (ar_region | ~saknar_kommunkod).all()),
        ("alla kommuner har kommunkod", (~saknar_kommunkod[ar_kommun]).all()),
        ("cls finns precis för dem som har CrUX-data", (tabell["cls_p75"].notna() == har_crux).all()),
    ]
    for kolumn in ["befolkning", "invanare_kolada", "bredband_ned_mbit_s", "lan"] + BETYG:
        regler.append((f"{kolumn} saknas inte", tabell[kolumn].notna().all()))

    regler += [
        ("kommunkoden börjar med länskoden", (med_kod["kommunkod"].str[:2] == med_kod["lanskod"]).all()),
        ("befolkning skiljer högst 2 procent mellan Wikidata och Kolada", (skillnad.abs() <= 2).all()),
        ("regionernas befolkning skiljer högst 1 procent från Sveriges", abs(summa_regioner - sverige) / sverige <= 0.01),
        ("CrUX har en enda mätperiod", tabell["period_slut"].nunique() == 1),
    ]
    return regler


def validera(tabell):
    resultat = pd.DataFrame(
        [{"kontroll": namn, "godkand": bool(villkor)} for namn, villkor in kontroller(tabell)]
    )
    misslyckade = resultat.loc[~resultat["godkand"], "kontroll"].tolist()
    if misslyckade:
        raise ValueError(f"Kontroller som inte gick igenom: {misslyckade}")
    print(f"  Alla {len(resultat)} kontroller gick igenom")
    return resultat
