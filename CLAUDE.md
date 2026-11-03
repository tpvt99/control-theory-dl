# paperhub — personal paper knowledge base

Goal: track ML/AI/robotics/control papers, summarize them into `summaries/**.md`, and let the owner
collect ideas in `notes/ideas.md` to find research directions.

## Layout
- `paperhub/` CLI (`python3 -m paperhub ...`), `venues.toml` venue registry, `data/papers.db` metadata (gitignored)
- `pdfs/` downloaded PDFs (gitignored). `summaries/<source>/<venue>/<year>/<id>.md` one file per paper.
- `notes/ideas.md` the owner's master reading/ideas file.

## When asked to "summarize pending papers" (or N of them)
1. `python3 -m paperhub pending --stubs --show N` to get paper ids + pdf paths.
2. Read each PDF (Read tool, page ranges for long ones) and fill the stub in `summaries/...` using the template below.
3. Set `status: done` in the front matter. Never invent content: if a section is not in the paper, write "not stated".
4. Do NOT edit `notes/ideas.md` — that file is the owner's.

## Summary template (keep each under ~350 words)
```
## One-line
What it does, in plain words.
## Problem & gap
What was unsolved, and what the paper claims is missing in prior work.
## Method
Core idea. Key equations/algorithms only if essential.
## Theory (if any)
Main theorem/claim in words. **Assumptions** (list them explicitly — gaps hide here). Linear-only? Asymptotic?
## Experiments
Environments/datasets, baselines, scale. Is the comparison fair? Simulation-only?
## Limitations (authors' and yours)
## Open questions / future work
## Takeaway & tags
Why it matters in 2 sentences. Tags: e.g. #control #rl #imitation #nlp #cv #optimization #theory
```
Verify claims against the paper text, not just the abstract. Flag anything in the abstract that the body doesn't support.

## Weekly update
`./weekly.sh` — syncs configured venues, pulls last 7 days of arXiv metadata, downloads new PDFs.
