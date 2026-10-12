"""Kör hela pipelinen från början till slut.

Från mappen python/:

    uv run python pipeline/kor.py
    uv run python pipeline/kor.py --utan-hamtning

Med --utan-hamtning används rådatan som redan finns i data/radata, så att
inga källor anropas.
"""

import argparse

import hamta
import harmonisera
import lagra
import tvatta
import validera


def kor(hamta_data=True):
    if hamta_data:
        print("1. Hämtar")
        hamta.hamta_allt()
    else:
        print("1. Hämtar inte, använder befintlig rådata")

    print("2. Tvättar")
    tvatta.tvatta_allt()

    print("3. Harmoniserar")
    webbplatser = harmonisera.harmonisera()

    print("4. Validerar")
    validera.validera(webbplatser)

    print("5. Lagrar")
    lagra.lagra(webbplatser)

    print("Klart")


if __name__ == "__main__":
    tolkare = argparse.ArgumentParser(description="Hämtar, tvättar, harmoniserar, validerar och lagrar data om kommunernas webbplatser.")
    tolkare.add_argument("--utan-hamtning", action="store_true", help="använd rådatan som redan finns i data/radata")
    argument = tolkare.parse_args()
    kor(hamta_data=not argument.utan_hamtning)
