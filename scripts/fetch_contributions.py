import os
import json
import requests
from bs4 import BeautifulSoup

USERNAME = "leonardolyrio"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch_contributions():
    print(f"Buscando contribuições públicas para {USERNAME}...")
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    # No HTML do GitHub, cada quadradinho tem a classe 'ContributionCalendar-day'
    days = soup.find_all("td", class_="ContributionCalendar-day")

    contributions = []
    for day in days:
        date_str = day.get("data-date")
        if not date_str:
            continue
        # O nível de contribuição vai de 0 a 4 (usado para decidir a cor)
        level = int(day.get("data-level", "0"))
        
        contributions.append({
            "date": date_str,
            "level": level
        })
    
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump({"days": contributions}, f, indent=2)
    
    print(f"Salvo {len(contributions)} dias no arquivo data/contributions.json")

if __name__ == "__main__":
    fetch_contributions()
