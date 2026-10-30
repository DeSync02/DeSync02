"""Generates assets/stats.svg from live GitHub data. Run by the nightly workflow."""
import json, os, urllib.request, datetime

USER = os.environ.get("GH_USER", "DeSync02")
TOKEN = os.environ["GITHUB_TOKEN"]

def gql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]

u = gql("""{ user(login: "%s") {
  followers { totalCount }
  pullRequests { totalCount }
  repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
    totalCount nodes { stargazerCount } }
  contributionsCollection { totalCommitContributions
    contributionCalendar { totalContributions } }
} }""" % USER)

stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
cc = u["contributionsCollection"]
stats = [
    (cc["contributionCalendar"]["totalContributions"], "CONTRIB · 1Y"),
    (cc["totalCommitContributions"], "COMMITS · 1Y"),
    (u["repositories"]["totalCount"], "REPOS"),
    (stars, "STARS"),
    (u["pullRequests"]["totalCount"], "PULL REQS"),
    (u["followers"]["totalCount"], "FOLLOWERS"),
]

today = datetime.datetime.utcnow().strftime("%b %d, %Y").upper()
w, gap = 150, 14
cards = ""
for i, (val, label) in enumerate(stats):
    x = 20 + i * (w + gap)
    cards += f'''<g transform="translate({x},60)">
  <rect width="{w}" height="84" rx="10" fill="#0d1120" stroke="#f5c518" stroke-opacity=".4"/>
  <text x="{w/2}" y="43" text-anchor="middle" font-family="Impact, sans-serif" font-size="34" fill="#fff">{val}</text>
  <text x="{w/2}" y="66" text-anchor="middle" font-family="monospace" font-size="11" letter-spacing="2" fill="#f5c518">{label}</text>
</g>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 170" width="100%">
<rect width="1000" height="170" rx="12" fill="#07090f"/>
<rect x="20" y="22" width="5" height="22" fill="#f5c518"/>
<text x="36" y="40" font-family="monospace" font-size="16" font-weight="bold" letter-spacing="4" fill="#fff">GOTHAM GAZETTE // GITHUB STATS</text>
<text x="980" y="40" text-anchor="end" font-family="monospace" font-size="12" letter-spacing="2" fill="#6b7a99">UPDATED {today}</text>
{cards}
</svg>'''
open("assets/stats.svg", "w").write(svg)
print("stats.svg written")
