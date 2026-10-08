"""Fetches GitHub stats for USER and writes them into dark_mode.svg and light_mode.svg.

Needs a token in the ACCESS_TOKEN environment variable. Only the text inside the
<tspan id="<stat>_data"> and <tspan id="<stat>_dots"> elements changes; each line keeps
its length, so values stay right-aligned. If anything fails, the SVGs are left untouched.
"""
import os
import re
import sys
from pathlib import Path

import requests

USER = "RowaimSafdar"
SVGS = [Path("dark_mode.svg"), Path("light_mode.svg")]
API = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { stargazerCount }
    }
    repositoriesContributedTo(
      contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, PULL_REQUEST_REVIEW, REPOSITORY]
      first: 1
    ) { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
  }
}
"""


def graphql(token: str, variables: dict) -> dict:
    r = requests.post(API, json={"query": QUERY, "variables": variables},
                      headers={"Authorization": f"bearer {token}"}, timeout=30)
    r.raise_for_status()
    body = r.json()
    if body.get("errors"):
        raise RuntimeError(body["errors"][0].get("message", body["errors"]))
    if not body.get("data", {}).get("user"):
        raise RuntimeError(f"user {USER!r} not found")
    return body["data"]["user"]


def fetch_stats(token: str) -> dict:
    user = graphql(token, {"login": USER, "cursor": None})
    stars = sum(n["stargazerCount"] for n in user["repositories"]["nodes"])
    page = user["repositories"]["pageInfo"]
    while page["hasNextPage"]:
        more = graphql(token, {"login": USER, "cursor": page["endCursor"]})["repositories"]
        stars += sum(n["stargazerCount"] for n in more["nodes"])
        page = more["pageInfo"]
    contrib = user["contributionsCollection"]
    return {
        "repos": user["repositories"]["totalCount"],
        "contributed": user["repositoriesContributedTo"]["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": contrib["totalCommitContributions"],
        "contributions": contrib["contributionCalendar"]["totalContributions"],
    }


def apply(svg: str, stats: dict) -> str:
    for name, number in stats.items():
        value = f"{number:,}"
        pattern = re.compile(
            rf'(<tspan[^>]*id="{name}_dots"[^>]*>)([^<]*)(</tspan>\s*<tspan[^>]*id="{name}_data"[^>]*>)([^<]*)(</tspan>)'
        )
        m = pattern.search(svg)
        if not m:
            raise RuntimeError(f"no {name}_dots/{name}_data tspans in SVG")
        w = re.search(r'data-w="(\d+)"', m.group(1))
        width = int(w.group(1)) if w else len(m.group(2)) + len(m.group(4))  # dots + value fill this many chars
        dots = " " + "." * max(width - len(value) - 2, 1) + " "
        svg = svg[:m.start()] + m.group(1) + dots + m.group(3) + value + m.group(5) + svg[m.end():]
    return svg


def main() -> int:
    token = os.environ.get("ACCESS_TOKEN")
    if not token:
        print("error: set the ACCESS_TOKEN environment variable", file=sys.stderr)
        return 1
    try:
        stats = fetch_stats(token)
        updated = {path: apply(path.read_text(encoding="utf-8"), stats) for path in SVGS}
    except (requests.RequestException, RuntimeError, KeyError, OSError) as e:
        print(f"error: {e} (SVGs left unchanged)", file=sys.stderr)
        return 1
    for path, svg in updated.items():
        path.write_text(svg, encoding="utf-8")
    print("updated:", ", ".join(f"{k}={v:,}" for k, v in stats.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
