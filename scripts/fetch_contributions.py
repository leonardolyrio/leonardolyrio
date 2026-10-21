import os
import json
import requests
from bs4 import BeautifulSoup

USERNAME = "leonardolyrio"
OUTPUT = "data/contributions.json"

GRAPHQL_URL = "https://api.github.com/graphql"
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount contributionLevel }
        }
      }
    }
  }
}
"""
LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


def fetch_graphql(token):
    """Fonte principal: API oficial. Traz a contagem real de cada dia."""
    response = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [
        {
            "date": d["date"],
            "count": d["contributionCount"],
            "level": LEVELS.get(d["contributionLevel"], 0),
        }
        for week in calendar["weeks"]
        for d in week["contributionDays"]
    ]
    return {"total": calendar["totalContributions"], "days": days}


def fetch_scrape():
    """Plano B: le a pagina publica (so traz o nivel de cor, sem contagem)."""
    url = f"https://github.com/users/{USERNAME}/contributions"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    days = []
    for cell in soup.find_all("td", class_="ContributionCalendar-day"):
        date_str = cell.get("data-date")
        if not date_str:
            continue
        days.append({
            "date": date_str,
            "count": None,
            "level": int(cell.get("data-level", "0")),
        })
    return {"total": None, "days": days}


def fetch_contributions():
    print(f"Buscando contribuições públicas para {USERNAME}...")
    token = os.environ.get("GITHUB_TOKEN")
    data = None
    if token:
        try:
            data = fetch_graphql(token)
            print("Dados obtidos pela API GraphQL.")
        except Exception as exc:  # noqa: BLE001
            print(f"Aviso: GraphQL falhou ({exc}). Usando o plano B.")
    if data is None:
        data = fetch_scrape()
        print("Dados obtidos pela página pública (sem contagem por dia).")

    # A página lista os dias por linha (domingos, depois segundas...). Ordena por data.
    data["days"].sort(key=lambda d: d["date"])

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Salvo {len(data['days'])} dias em {OUTPUT}")


if __name__ == "__main__":
    fetch_contributions()
