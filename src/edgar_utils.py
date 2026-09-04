import requests
import time
import json

HEADERS = {"User-Agent": "SB826 Board Network Research Project shauryaguptaa8@gmail.com"}
SLEEP = 0.15  # stay well under SEC's 10 req/sec fair-access limit
MAX_RETRIES = 4


def get_json(url, params=None):
    """Retries transient network errors (connect timeout, connection reset)
    with exponential backoff -- these are real and expected on long-running
    scripts hitting an external API, not something to let kill the whole run."""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=30)
            time.sleep(SLEEP)
            if r.status_code != 200:
                return None, r.status_code
            return r.json(), 200
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout) as e:
            last_exc = e
            backoff = 2 ** attempt
            time.sleep(backoff)
    return None, f"NETWORK_ERROR_AFTER_{MAX_RETRIES}_RETRIES: {last_exc}"


def get_submissions(cik10):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    return get_json(url)


def cik_to_10digit(cik):
    return str(int(cik)).zfill(10)
