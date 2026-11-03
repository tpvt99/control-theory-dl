"""PMLR proceedings (ICML, COLT, CoRL, L4DC, AISTATS...). Static HTML, fully open."""
import html
import re
from .http import get

PAPER = re.compile(r'<div class="paper">(.*?)</div>', re.S)


def fetch(volume, venue, year):
    page = get(f"https://proceedings.mlr.press/{volume}/", delay=1).text
    for blk in PAPER.findall(page):
        t = re.search(r'class="title">(.*?)</p>', blk, re.S)
        a = re.search(r'class="authors">(.*?)</span>', blk, re.S)
        absu = re.search(r'href="([^"]+\.html)"', blk)
        pdf = re.search(r'href="([^"]+\.pdf)"', blk)
        if not (t and absu):
            continue
        url = absu.group(1)
        slug = url.rsplit("/", 1)[-1].removesuffix(".html")
        yield {
            "id": f"pmlr:{volume}/{slug}", "source": "pmlr", "venue": venue, "year": year,
            "title": html.unescape(" ".join(t.group(1).split())),
            "authors": html.unescape(a.group(1).replace("&nbsp;", " ")) if a else None,
            "url": url, "pdf_url": pdf.group(1) if pdf else None,
        }
