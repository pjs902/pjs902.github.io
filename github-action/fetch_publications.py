#!/usr/bin/env python3
"""
Fetch this author's publications from the NASA ADS API and write them to
publications.json as static data the site can fetch client-side.

Requires an ADS API token (get one free at https://ui.adsabs.harvard.edu/user/settings/token)
passed via the ADS_API_TOKEN environment variable — never commit the token itself.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

ORCID = "0000-0002-7489-5244"
TOKEN = os.environ.get("ADS_API_TOKEN")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "publications.json")

FIELDS = ["bibcode", "title", "author", "pub", "year", "identifier", "doi",
          "doctype", "bibstem", "volume", "page", "orcid_pub", "orcid_user", "orcid_other"]


def my_index(d):
    """Author-list position of ORCID's owner, from ADS's per-author ORCID arrays (None if unmatched)."""
    for key in ("orcid_pub", "orcid_user", "orcid_other"):
        for i, v in enumerate(d.get(key, [])):
            if v == ORCID:
                return i
    return None


def citation(d):
    """Short journal reference: 'ApJ, 975, 268' for articles, the arXiv id for e-prints, else ADS's pub name."""
    page = (d.get("page") or [""])[0]
    if d.get("doctype") == "eprint" and page.startswith("arXiv:"):
        return page
    if d.get("volume") and d.get("bibstem"):
        return ", ".join(filter(None, [d["bibstem"][0], d["volume"], page]))
    return d.get("pub", "")

def fetch():
    if not TOKEN:
        print("ERROR: ADS_API_TOKEN environment variable not set.", file=sys.stderr)
        sys.exit(1)

    query = urllib.parse.urlencode({
        "q": f"orcid:{ORCID}",
        "fl": ",".join(FIELDS),
        "sort": "date desc",
        "rows": 200,
    })
    url = f"https://api.adsabs.harvard.edu/v1/search/query?{query}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)

    docs = data.get("response", {}).get("docs", [])
    papers = []
    for d in docs:
        arxiv_id = next((i for i in d.get("identifier", []) if i.startswith("arXiv:")), None)
        papers.append({
            "year": d.get("year"),
            "title": (d.get("title") or [""])[0],
            "authors": d.get("author", [])[:12],
            "journal": citation(d),
            "doctype": d.get("doctype"),
            "me": my_index(d),
            "bibcode": d.get("bibcode"),
            "adsUrl": f"https://ui.adsabs.harvard.edu/abs/{d.get('bibcode')}/abstract",
            "arxivUrl": f"https://arxiv.org/abs/{arxiv_id.split(':', 1)[1]}" if arxiv_id else None,
            "doiUrl": f"https://doi.org/{d['doi'][0]}" if d.get("doi") else None,
        })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(papers, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(papers)} publications to {OUTPUT_PATH}")

if __name__ == "__main__":
    fetch()
