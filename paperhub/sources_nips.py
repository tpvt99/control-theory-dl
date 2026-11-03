"""NeurIPS via papers.nips.cc (static, open)."""
import html
import re
from .http import get

ITEM = re.compile(r'<a title="paper title" href="(/paper_files/paper/\d+/hash/[^"]+)">(.*?)</a>\s*<span class="paper-authors">(.*?)</span>', re.S)


def fetch(year, venue="NeurIPS"):
    page = get(f"https://papers.nips.cc/paper_files/paper/{year}", delay=1).text
    for href, title, authors in ITEM.findall(page):
        pdf = href.replace("/hash/", "/file/").replace("-Abstract-Conference.html", "-Paper-Conference.pdf") \
                  .replace("-Abstract.html", "-Paper.pdf")
        h = href.split("/hash/")[1].split("-")[0]
        yield {
            "id": f"nips:{year}/{h}", "source": "nips", "venue": venue, "year": year,
            "title": html.unescape(" ".join(title.split())),
            "authors": html.unescape(authors.strip()),
            "url": "https://papers.nips.cc" + href, "pdf_url": "https://papers.nips.cc" + pdf,
        }
