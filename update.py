import os
import re
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_stats():
    token = os.environ.get('GH_TOKEN')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Consulta GraphQL para extrair todas as métricas em uma única requisição
    query = """
    query {
      user(login: "leonardolyrio") {
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            stargazerCount
          }
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    req = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    data = req.json()["data"]["user"]
    
    followers = data["followers"]["totalCount"]
    repos = data["repositories"]["totalCount"]
    stars = sum(node["stargazerCount"] for node in data["repositories"]["nodes"])
    commits = data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    
    return str(repos), str(stars), str(commits), str(followers)

def get_uptime():
    bday = datetime(2007, 3, 3)
    now = datetime.now()
    diff = relativedelta(now, bday)
    return f"{diff.years} years, {diff.months} months, {diff.days} days"

def update_svg(filename, uptime, repos, stars, commits, followers):
    with open(filename, 'r', encoding='utf-8') as f:
        svg = f.read()

    # Expressões regulares substituem o texto atual preservando as tags SVG e os espaços
    svg = re.sub(r'(id="uptime">)(.*?)(</tspan>)', rf'\g<1> {uptime}\g<3>', svg)
    svg = re.sub(r'(id="repos">)(.*?)(</tspan>)', rf'\g<1> {repos}\g<3>', svg)
    svg = re.sub(r'(id="stars">)(.*?)(</tspan>)', rf'\g<1> {stars}\g<3>', svg)
    svg = re.sub(r'(id="commits">)(.*?)(</tspan>)', rf'\g<1> {commits}\g<3>', svg)
    svg = re.sub(r'(id="followers">)(.*?)(</tspan>)', rf'\g<1> {followers}\g<3>', svg)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

if __name__ == "__main__":
    uptime = get_uptime()
    repos, stars, commits, followers = get_stats()
    
    update_svg("dark_mode.svg", uptime, repos, stars, commits, followers)
    update_svg("light_mode.svg", uptime, repos, stars, commits, followers)