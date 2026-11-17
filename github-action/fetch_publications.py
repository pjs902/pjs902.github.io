#!/usr/bin/env python3
"""
Fetch this author's publications from SciX (NASA ADS's successor) and write them to
publications.json as static data the site can fetch client-side.

Requires a SciX API token (https://scixplorer.org/user/settings/token) in SCIX_API_TOKEN
or the legacy ADS_API_TOKEN; scixplorer reads either. Never commit the token itself.
"""
import json
import os
import sys

from scixplorer import Document

ORCID = "0000-0002-7489-5244"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "publications.json")

FIELDS = ["bibcode", "title", "author", "pub", "year", "identifier",
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
    query = (
        Document
        .select(*FIELDS)
        .where(Document.orcid == ORCID)
        .order_by(Document.date.desc(), Document.bibcode.desc())  # bibcode breaks same-month ties, as the site's search link does
    )
    docs = [paper.to_dict() for paper in query]
    if not docs:
        sys.exit("SciX returned no papers; keeping the old publications.json")
    papers = []
    for d in docs:
        arxiv_id = next((i for i in d.get("identifier", []) if i.startswith("arXiv:")), None)
        papers.append({
            "year": str(d["year"]) if d.get("year") else None,  # scixplorer gives an int; the site expects the old string
            "title": (d.get("title") or [""])[0],
            "authors": d.get("author", [])[:12],
            "journal": citation(d),
            "doctype": d.get("doctype"),
            "me": my_index(d),
            "bibcode": d.get("bibcode"),
            "adsUrl": f"https://scixplorer.org/abs/{d.get('bibcode')}/abstract",
            "arxivUrl": f"https://arxiv.org/abs/{arxiv_id.split(':', 1)[1]}" if arxiv_id else None,
        })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(papers, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(papers)} publications to {OUTPUT_PATH}")

if __name__ == "__main__":
    fetch()
