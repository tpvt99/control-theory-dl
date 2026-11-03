"""arXiv via the public API (no key). Rule: >=3s between requests."""
import re
import xml.etree.ElementTree as ET
from .http import get

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"


def fetch(categories, date_from, date_to, page=200):
    """Yield paper dicts for submissions in [date_from, date_to] (YYYYMMDD)."""
    cat_q = "(" + "+OR+".join(f"cat:{c}" for c in categories) + ")"
    q = f"{cat_q}+AND+submittedDate:[{date_from}0000+TO+{date_to}2359]"
    start = 0
    while True:
        url = (f"{API}?search_query={q}&start={start}&max_results={page}"
               f"&sortBy=submittedDate&sortOrder=ascending")
        root = ET.fromstring(get(url, delay=3.1).content)
        entries = root.findall("a:entry", NS)
        if not entries:
            return
        for e in entries:
            aid = e.find("a:id", NS).text.rsplit("/abs/", 1)[1]
            base = re.sub(r"v\d+$", "", aid)
            cats = [c.get("term") for c in e.findall("a:category", NS)]
            pub = e.find("a:published", NS).text
            yield {
                "id": f"arxiv:{base}", "source": "arxiv", "venue": "arXiv",
                "year": int(pub[:4]),
                "title": " ".join(e.find("a:title", NS).text.split()),
                "authors": ", ".join(a.find("a:name", NS).text for a in e.findall("a:author", NS)),
                "abstract": " ".join(e.find("a:summary", NS).text.split()),
                "url": f"https://arxiv.org/abs/{base}",
                "pdf_url": f"https://arxiv.org/pdf/{base}",
                "categories": " ".join(cats), "published": pub,
            }
        start += page
