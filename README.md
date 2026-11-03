# paperhub
```
python3 -m paperhub sync [names]        # venue metadata from venues.toml
python3 -m paperhub arxiv [--from YYYYMMDD --to YYYYMMDD --cats cs.LG,...]
python3 -m paperhub download [--source pmlr|nips|openreview|arxiv] [--venue ICML] [--year 2024] [--limit N]
python3 -m paperhub pending --stubs     # create summary skeletons for downloaded PDFs
python3 -m paperhub stats
```
ICLR/TMLR need `pip install openreview-py` plus `OPENREVIEW_USER` / `OPENREVIEW_PASS` env vars.
