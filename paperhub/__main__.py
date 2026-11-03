import argparse
import datetime as dt
import tomllib
from pathlib import Path

from . import db
from .http import get

ROOT = db.ROOT


def _ingest(gen, con):
    new = tot = 0
    for p in gen:
        tot += 1
        new += db.upsert(con, p)
        if tot % 200 == 0:
            con.commit()
    con.commit()
    print(f"  {tot} seen, {new} new")


def cmd_sync(a):
    cfg = tomllib.loads((ROOT / "venues.toml").read_text())
    con = db.connect()
    for name in a.names or [n for n in cfg if cfg[n]["kind"] != "arxiv"]:
        v = cfg[name]
        print(f"[{name}]")
        try:
            if v["kind"] == "pmlr":
                from .sources_pmlr import fetch
                _ingest(fetch(v["volume"], v["venue"], v["year"]), con)
            elif v["kind"] == "nips":
                from .sources_nips import fetch
                _ingest(fetch(v["year"]), con)
            elif v["kind"] == "openreview":
                from .sources_openreview import fetch
                _ingest(fetch(v["venueid"], v["venue"], v["year"]), con)
        except Exception as e:  # keep going on other venues (not yet published, auth missing...)
            print(f"  FAILED: {type(e).__name__}: {e}")


def cmd_arxiv(a):
    from .sources_arxiv import fetch
    cfg = tomllib.loads((ROOT / "venues.toml").read_text())["arxiv"]
    cats = a.cats.split(",") if a.cats else cfg["categories"]
    today = dt.date.today()
    d_to = a.to or today.strftime("%Y%m%d")
    d_from = a.frm or (today - dt.timedelta(days=7)).strftime("%Y%m%d")
    print(f"[arxiv] {d_from}..{d_to} {cats}")
    _ingest(fetch(cats, d_from, d_to), db.connect())


def cmd_download(a):
    con = db.connect()
    q = "SELECT * FROM papers WHERE pdf_url IS NOT NULL AND pdf_path IS NULL"
    args = []
    for col in ("source", "venue", "year"):
        if getattr(a, col):
            q += f" AND {col}=?"
            args.append(getattr(a, col))
    q += " ORDER BY published DESC, year DESC"
    if a.limit:
        q += f" LIMIT {int(a.limit)}"
    rows = con.execute(q, args).fetchall()
    print(f"{len(rows)} PDFs to fetch")
    for i, r in enumerate(rows, 1):
        safe = r["id"].split(":", 1)[1].replace("/", "_")
        rel = Path("pdfs") / r["source"] / str(r["venue"] or "x").replace("/", "_") / str(r["year"]) / f"{safe}.pdf"
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = get(r["pdf_url"], delay=3.1 if r["source"] == "arxiv" else 1.0).content
            if not data.startswith(b"%PDF"):
                raise ValueError("not a PDF")
            out.write_bytes(data)
            con.execute("UPDATE papers SET pdf_path=? WHERE id=?", (str(rel), r["id"]))
            con.commit()
            print(f"[{i}/{len(rows)}] ok {r['id']}")
        except Exception as e:
            print(f"[{i}/{len(rows)}] FAIL {r['id']}: {e}")


def summary_path(r):
    safe = r["id"].split(":", 1)[1].replace("/", "_")
    return ROOT / "summaries" / r["source"] / str(r["venue"] or "x").replace("/", "_") / str(r["year"]) / f"{safe}.md"


def cmd_pending(a):
    """List downloaded PDFs without a summary; --stubs writes the .md skeletons."""
    con = db.connect()
    rows = con.execute("SELECT * FROM papers WHERE pdf_path IS NOT NULL").fetchall()
    n = 0
    for r in rows:
        sp = summary_path(r)
        if sp.exists():
            continue
        n += 1
        if a.stubs:
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_text(f"---\nid: {r['id']}\ntitle: {r['title']}\nvenue: {r['venue']} {r['year']}\n"
                          f"pdf: {r['pdf_path']}\nurl: {r['url']}\nstatus: todo\n---\n\n# {r['title']}\n\n_TODO: summarize per CLAUDE.md_\n")
        if n <= a.show:
            print(f"{r['id']}\t{r['pdf_path']}")
    print(f"{n} papers pending summary")


def cmd_stats(a):
    con = db.connect()
    for r in con.execute("SELECT source, venue, year, COUNT(*) n, COUNT(pdf_path) pdfs FROM papers "
                         "GROUP BY 1,2,3 ORDER BY 3 DESC,2"):
        print(f"{r['source']:8} {str(r['venue']):10} {r['year']}  papers={r['n']:6} pdfs={r['pdfs']:6}")


def main():
    ap = argparse.ArgumentParser(prog="paperhub")
    sp = ap.add_subparsers(required=True)
    s = sp.add_parser("sync", help="fetch metadata for venues in venues.toml"); s.add_argument("names", nargs="*"); s.set_defaults(f=cmd_sync)
    s = sp.add_parser("arxiv", help="fetch arXiv metadata by date range")
    s.add_argument("--from", dest="frm"); s.add_argument("--to"); s.add_argument("--cats"); s.set_defaults(f=cmd_arxiv)
    s = sp.add_parser("download", help="download PDFs for papers in the DB")
    for k in ("source", "venue", "year"): s.add_argument(f"--{k}")
    s.add_argument("--limit"); s.set_defaults(f=cmd_download)
    s = sp.add_parser("pending", help="papers with PDF but no summary"); s.add_argument("--stubs", action="store_true"); s.add_argument("--show", type=int, default=20); s.set_defaults(f=cmd_pending)
    s = sp.add_parser("stats"); s.set_defaults(f=cmd_stats)
    a = ap.parse_args(); a.f(a)


main()
