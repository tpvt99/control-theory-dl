"""OpenReview (ICLR, TMLR, ...). Needs a free account: set OPENREVIEW_USER / OPENREVIEW_PASS.
The anonymous REST API is bot-challenged, so we use the official openreview-py client."""
import os


def fetch(venueid, venue, year):
    import openreview  # pip install openreview-py
    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net",
        username=os.environ["OPENREVIEW_USER"], password=os.environ["OPENREVIEW_PASS"])
    for n in client.get_all_notes(content={"venueid": venueid}):
        c = n.content
        g = lambda k: (c.get(k) or {}).get("value")
        yield {
            "id": f"openreview:{n.id}", "source": "openreview", "venue": venue, "year": year,
            "title": g("title"), "authors": ", ".join(g("authors") or []),
            "abstract": g("abstract"), "url": f"https://openreview.net/forum?id={n.id}",
            "pdf_url": f"https://openreview.net/pdf?id={n.id}",
        }
