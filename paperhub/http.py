import time
import requests

UA = "paperhub/0.1 (personal research tool; mailto:scholaraskswhy@gmail.com)"
_last = {}


def get(url, delay=1.0, stream=False, **kw):
    """Polite GET: per-host minimum delay, retries on 429/5xx."""
    host = url.split("/")[2]
    for attempt in range(5):
        wait = delay - (time.time() - _last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60, stream=stream, **kw)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(5 * (attempt + 1))
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()
