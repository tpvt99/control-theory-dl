import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "papers.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
  id TEXT PRIMARY KEY,          -- e.g. arxiv:2401.01234, pmlr:v235/abe24a, nips:2024/abc
  source TEXT NOT NULL,         -- arxiv | pmlr | nips | openreview | ...
  venue TEXT,                   -- e.g. ICML, NeurIPS, cs.LG
  year INTEGER,
  title TEXT NOT NULL,
  authors TEXT,
  abstract TEXT,
  url TEXT,
  pdf_url TEXT,                 -- NULL when paywalled / unavailable
  categories TEXT,
  published TEXT,
  pdf_path TEXT,                -- relative to repo root once downloaded
  added_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_venue_year ON papers(venue, year);
"""


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def upsert(con, p: dict) -> bool:
    """Insert a paper; return True if new. Existing rows keep pdf_path."""
    cols = ["id", "source", "venue", "year", "title", "authors", "abstract",
            "url", "pdf_url", "categories", "published"]
    vals = [p.get(c) for c in cols]
    cur = con.execute("SELECT 1 FROM papers WHERE id=?", (p["id"],))
    if cur.fetchone():
        return False
    con.execute(f"INSERT INTO papers ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})", vals)
    return True
