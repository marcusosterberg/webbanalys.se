"""Sådant som flera steg i pipelinen använder.

Sökvägarna utgår från mappen python/, oavsett varifrån skripten körs.
"""

import json
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd

ROT = Path(__file__).resolve().parent.parent
DATA = ROT / "data"
RADATA = DATA / "radata"
TVATTAD = DATA / "tvattad"
HARMONISERAD = DATA / "harmoniserad"

KOLADA_AR = 2025

USER_AGENT = "webbanalys.se, kodexempel i serien Python for webbanalys (https://webbanalys.se)"


def nu():
    """Tiden just nu i svensk tid, som text."""
    return pd.Timestamp.now(tz="Europe/Stockholm").isoformat(timespec="seconds")


def spara_radata(filnamn, paket):
    """Sparar ett svar från en källa i data/radata som JSON."""
    RADATA.mkdir(parents=True, exist_ok=True)
    text = json.dumps(paket, ensure_ascii=False, indent=2)
    (RADATA / filnamn).write_text(text, encoding="utf-8")


def las_radata(filnamn):
    """Läser en fil med rådata."""
    return json.loads((RADATA / filnamn).read_text(encoding="utf-8"))


def till_origin(adress):
    """Gör om en adress till protokoll och domännamn, till exempel https://ale.se."""
    delar = urlsplit(adress)
    return f"{delar.scheme}://{delar.netloc}"


def sista_delen(adresser):
    """Tar texten efter det sista snedstrecket, till exempel Q498470 ur en adress till Wikidata."""
    return adresser.str.rsplit("/", n=1).str[-1]


def webperf_platser():
    """Webperfs kommuner och regioner ur rådatan, som en lista med poster."""
    kommuner = las_radata("webperf-kommuner.json")["svar"]["municipalities"]
    regioner = las_radata("webperf-regioner.json")["svar"]["regions"]
    return kommuner + regioner
