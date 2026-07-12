#!/usr/bin/env python3
"""
generate_readme.py

Fetches live GitHub stats for a user (repos, stars, commits, followers,
lines of code contributed) and writes them into README.md between the
markers:
    <!--START_SECTION:stats-->
    <!--END_SECTION:stats-->

Requires an environment variable GH_TOKEN (a GitHub Personal Access Token
with 'repo' and 'read:user' scopes) and GH_USERNAME (your GitHub username).
Both are supplied automatically by the included GitHub Actions workflow.
"""

import os
import re
import sys
import time
import requests

GITHUB_USERNAME = os.environ.get("GH_USERNAME", "sanjus-robotic-studio")
GITHUB_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("ERROR: GH_TOKEN (or GITHUB_TOKEN) environment variable is required.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"


def graphql_query(query, variables=None):
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def get_user_overview():
    """Basic counts: followers, public repos, repos contributed to, account created year."""
    query = """
    query($login: String!) {
      user(login: $login) {
        followers { totalCount }
        repositories(ownerAffiliations: OWNER, isFork: false) { totalCount }
        repositoriesContributedTo(includeUserRepositories: true, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
        }
        createdAt
      }
    }
    """
    data = graphql_query(query, {"login": GITHUB_USERNAME})
    return data["user"]


def get_total_stars():
    """Sum stargazerCount across all owned, non-fork repos (paginated)."""
    total_stars = 0
    cursor = None
    while True:
        query = """
        query($login: String!, $cursor: String) {
          user(login: $login) {
            repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
              nodes { stargazerCount }
              pageInfo { hasNextPage endCursor }
            }
          }
        }
        """
        data = graphql_query(query, {"login": GITHUB_USERNAME, "cursor": cursor})
        repos = data["user"]["repositories"]
        total_stars += sum(r["stargazerCount"] for r in repos["nodes"])
        if repos["pageInfo"]["hasNextPage"]:
            cursor = repos["pageInfo"]["endCursor"]
        else:
            break
    return total_stars


def get_total_commits(created_at):
    """
    contributionsCollection only covers one year at a time, so loop from
    account creation year through the current year and sum commit contributions.
    """
    from datetime import datetime, timezone

    start_year = int(created_at[:4])
    current_year = datetime.now(timezone.utc).year
    total_commits = 0

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """

    for year in range(start_year, current_year + 1):
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"
        data = graphql_query(query, {"login": GITHUB_USERNAME, "from": from_date, "to": to_date})
        cc = data["user"]["contributionsCollection"]
        total_commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]

    return total_commits


def get_lines_of_code():
    """
    Sums additions/deletions attributed to GITHUB_USERNAME across all owned,
    non-fork repos using the REST 'stats/contributors' endpoint.
    GitHub computes these stats asynchronously; if a repo's stats aren't
    cached yet (202 response) we retry briefly, then move on.
    """
    additions_total = 0
    deletions_total = 0

    repos = []
    page = 1
    while True:
        resp = requests.get(
            f"{REST_URL}/users/{GITHUB_USERNAME}/repos",
            headers=HEADERS,
            params={"type": "owner", "per_page": 100, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(r for r in batch if not r.get("fork"))
        page += 1

    for repo in repos:
        owner = repo["owner"]["login"]
        name = repo["name"]
        url = f"{REST_URL}/repos/{owner}/{name}/stats/contributors"

        for attempt in range(3):
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 202:
                # Stats are being computed; wait and retry once or twice.
                time.sleep(2)
                continue
            if resp.status_code != 200:
                break
            contributors = resp.json() or []
            for c in contributors:
                if c.get("author") and c["author"].get("login") == GITHUB_USERNAME:
                    for week in c.get("weeks", []):
                        additions_total += week.get("a", 0)
                        deletions_total += week.get("d", 0)
            break

    return additions_total, deletions_total


def format_number(n):
    return f"{n:,}"


def build_stats_block():
    overview = get_user_overview()
    followers = overview["followers"]["totalCount"]
    public_repos = overview["repositories"]["totalCount"]
    contributed_to = overview["repositoriesContributedTo"]["totalCount"]
    created_at = overview["createdAt"]

    total_stars = get_total_stars()
    total_commits = get_total_commits(created_at)
    additions, deletions = get_lines_of_code()
    total_loc = additions + deletions

    lines = [
        f"  Repos:       {public_repos} {{Contributed: {contributed_to}}}  |  Stars: {format_number(total_stars)}",
        f"  Commits:     {format_number(total_commits)}  |  Followers: {format_number(followers)}",
        f"  Lines of Code:  {format_number(total_loc)} ( +{format_number(additions)}, -{format_number(deletions)} )",
    ]
    return "\n".join(lines)


def update_readme(stats_block, readme_path="README.md"):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(<!--START_SECTION:stats-->\n)(.*?)(\n<!--END_SECTION:stats-->)",
        re.DOTALL,
    )

    if not pattern.search(content):
        print("ERROR: Could not find stats markers in README.md")
        sys.exit(1)

    new_content = pattern.sub(lambda m: m.group(1) + stats_block + m.group(3), content)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README.md updated successfully.")


if __name__ == "__main__":
    stats_block = build_stats_block()
    update_readme(stats_block)
