import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import re

BASE_URL = "https://www.myscheme.gov.in"
OUTPUT = Path("data/schemes.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ManufacturingOpportunityTracker/1.0)"
}


def get_page(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def find_scheme_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/schemes/" in href:
            links.add(urljoin(BASE_URL, href))

    return sorted(links)


def extract_scheme(url):
    try:
        html = get_page(url)
        soup = BeautifulSoup(html, "html.parser")

        text = clean(soup.get_text(" ", strip=True))

        title = soup.title.get_text(strip=True) if soup.title else url

        return {
            "scheme_name": title[:250],
            "ministry": "",
            "sector": "Manufacturing / MSME",
            "state": "India",
            "benefit": "",
            "eligibility": text[:2000],
            "deadline": "",
            "source_url": url
        }

    except Exception as e:
        print(f"Failed: {url} -> {e}")
        return None


def main():

    print("Fetching myScheme...")

    homepage = get_page(BASE_URL)

    links = find_scheme_links(homepage)

    print(f"Found {len(links)} scheme links.")

    rows = []

    # Start conservatively.
    # We will expand this after the first successful run.
    for url in links[:100]:

        result = extract_scheme(url)

        if result:
            rows.append(result)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    new_df = pd.DataFrame(rows)

    if OUTPUT.exists():
        old_df = pd.read_csv(OUTPUT)
        final_df = pd.concat([old_df, new_df], ignore_index=True)
        final_df = final_df.drop_duplicates(
            subset=["source_url"],
            keep="last"
        )
    else:
        final_df = new_df

    final_df.to_csv(OUTPUT, index=False)

    print(f"Saved {len(final_df)} schemes.")


if __name__ == "__main__":
    main()
