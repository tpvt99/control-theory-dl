#!/usr/bin/env bash
# Weekly update: new venue papers + last 7 days of arXiv. Safe to re-run (idempotent).
# Optional cron:  0 7 * * 1 cd /home/tbaphong/a-control-theory-AI-paper && ./weekly.sh >> data/weekly.log 2>&1
set -u
cd "$(dirname "$0")"
python3 -m paperhub sync
python3 -m paperhub arxiv            # last 7 days, categories from venues.toml
# Venue PDFs: all (open access). arXiv PDFs: cap per run, raise --limit as you wish.
for s in pmlr nips openreview; do python3 -m paperhub download --source $s; done
python3 -m paperhub download --source arxiv --limit "${ARXIV_PDF_LIMIT:-300}"
python3 -m paperhub stats
