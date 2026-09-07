import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import re

SOURCE_URL = "https://my.msme.gov.in/mymsme/Scheme.aspx"
OUTPUT = Path("data/schemes.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ManufacturingOpportunityTracker/1.0)"
}


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def fetch_scheme_list():
    response = requests.get(
        SOURCE_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = []

    for tr in soup.find_all("tr"):
        cells = tr.find_all(["td", "th"])

        if not cells:
            continue

        scheme_name = clean(cells[0].get_text(" ", strip=True))

        if not scheme_name:
            continue

        # Skip table headings
        if scheme_name.lower() in ["scheme", "schemes", "s.no."]:
            continue

        links = tr.find_all("a", href=True)

        source_url = SOURCE_URL

        if links:
            source_url = urljoin(
                SOURCE_URL,
                links[-1]["href"]
            )

        rows.append({
            "scheme_name": scheme_name,
            "ministry": "Ministry of Micro, Small & Medium Enterprises",
            "sector": "MSME / Manufacturing",
            "state": "India",
            "benefit": "",
            "eligibility": "",
            "deadline": "",
            "source_url": source_url
        })

    return rows


def main():

    print("Fetching official MSME scheme list...")

    rows = fetch_scheme_list()

    if not rows:
        raise RuntimeError(
            "No schemes were found on the official MSME source."
        )

    df = pd.DataFrame(rows)

    # Remove duplicates
    df = df.drop_duplicates(
        subset=["scheme_name"],
        keep="first"
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT,
        index=False
    )

    print(f"Successfully collected {len(df)} schemes.")

    print("\nSchemes found:")

    for name in df["scheme_name"].head(20):
        print("-", name)


if __name__ == "__main__":
    main()
