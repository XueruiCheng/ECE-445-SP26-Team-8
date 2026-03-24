import math

from scrapling.fetchers import StealthySession
from .settings import PERIMETER_PEOPLE_URL
from bs4 import BeautifulSoup


def scrape_perimeter_people(target_count: int = 100) -> str:
    """Scrape the Perimeter Institute people listing page"""
    pages_needed = math.ceil(target_count / 12)
    all_cards = []
    seen = set()

    with StealthySession(headless=True, solve_cloudflare=True) as session:
        for page_num in range(pages_needed):

            if page_num == 0:
                url = PERIMETER_PEOPLE_URL
            else:
                url = f"{PERIMETER_PEOPLE_URL}?page={page_num}"

            response = session.fetch(url)
            html = response.body.decode("utf-8", errors="replace")

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.card[about]")
            
            if not cards:
                raise ValueError(f"No cards found on page {page_num}")

            for card in cards:
                about = card.get("about", "")
                if about and about not in seen:
                    seen.add(about)
                    all_cards.append(str(card))
        
            if len(all_cards) >= target_count:
                break

    return "<div>" + "".join(all_cards) + "</div>"


def scrape_quantum_people(url: str) -> str:
    """Web scrapes a URL and returns the body html"""
    if not url:
        return
    
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch(url)
        html = page.body.decode("utf-8", errors="replace")

    return html