"""Checks the ADS-to-site formatting. Run: python3 github-action/test_fetch.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fetch_publications import ORCID, citation, my_index

article = {"doctype": "article", "bibstem": ["ApJ"], "volume": "975", "page": ["268"],
           "orcid_pub": ["-", ORCID], "pub": "The Astrophysical Journal"}
eprint = {"doctype": "eprint", "page": ["arXiv:2611.15866"], "pub": "arXiv e-prints",
          "orcid_user": [ORCID]}
other = {"doctype": "inproceedings", "pub": "IAU Symposium", "orcid_pub": ["-", "-"]}

assert citation(article) == "ApJ, 975, 268"
assert citation(eprint) == "arXiv:2611.15866"
assert citation(other) == "IAU Symposium"
assert my_index(article) == 1
assert my_index(eprint) == 0
assert my_index(other) is None
print("ok")
