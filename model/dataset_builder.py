import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup

from .settings import BASE_URL, PROFILES_PATH, RAW_IMAGES_DIR
from .web_scraper import scrape_perimeter_people

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 10
RATE_LIMIT_SECONDS = 0.5


def sanitize_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def parse_people_cards(html: str) -> list[dict]:
    """Parse every person card from the listing page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.card[about]")
    people = []
    for card in cards:
        profile_path = card.get("about", "")

        img_tag = card.select_one("div.card-media img")
        img_src = img_tag.get("src", "") if img_tag else ""
        if img_src and img_src.startswith("/"):
            img_src = BASE_URL + img_src

        name_tag = card.select_one("h3.card-heading a span")
        name = name_tag.get_text(strip=True) if name_tag else ""

        role_tag = card.select_one("p.field--field-role")
        role = role_tag.get_text(" ", strip=True) if role_tag else ""

        position_tag = card.select_one("div.field--field-position")
        position = position_tag.get_text(strip=True) if position_tag else ""

        secondary_position_tag = card.select_one("div.field--field-secondary-position")
        secondary_position = secondary_position_tag.get_text(strip=True) if secondary_position_tag else ""

        research_area_tags = card.select("div.field--field-people-research-area div")
        research_areas = [t.get_text(strip=True) for t in research_area_tags]

        if not name:
            continue

        people.append({
            "name": name,
            "profile_url": BASE_URL + profile_path,
            "img_url": img_src,
            "role": role,
            "position": position,
            "secondary_position": secondary_position,
            "research_areas": research_areas,
        })
    return people


def fetch_profile_bio(profile_url: str) -> str:
    """Fetch a person's profile page and return all visible text as a single string."""
    try:
        resp = requests.get(profile_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        # Prefer <main> or <article>, fall back to <body>
        container = soup.find("main") or soup.find("article") or soup.body
        if not container:
            return ""
        text = container.get_text(" ", strip=True)
        # Collapse runs of whitespace
        text = re.sub(r"\s{2,}", " ", text)
        return text
    except requests.RequestException:
        return ""


def download_image(url: str, dest_path: str) -> bool:
    """Download an image URL to dest_path. Returns True on success."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return False
        if "image" not in resp.headers.get("Content-Type", ""):
            return False
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return True
    except requests.RequestException as e:
        print(f"    [download error] {e}")
        return False


def build_dataset(target_count: int = 100) -> None:
    print(f"Scraping Perimeter Institute people page (target: {target_count})...")
    html = scrape_perimeter_people(target_count)

    people = parse_people_cards(html)[:target_count]
    print(f"Parsed {len(people)} people from listing page.\n")

    profiles = {}

    for person in people:
        name = person["name"]
        slug = sanitize_name(name)
        print(f"[{name}]")

        # Download headshot
        os.makedirs(RAW_IMAGES_DIR, exist_ok=True)
        img_dest = os.path.join(RAW_IMAGES_DIR, f"{slug}.jpg")

        img_ok = False
        if person["img_url"]:
            img_ok = download_image(person["img_url"], img_dest)
            print(f"  image: {'saved' if img_ok else 'failed'}")
        else:
            print("  image: no URL found")

        time.sleep(RATE_LIMIT_SECONDS)

        # Fetch profile bio
        bio = ""
        if person["profile_url"]:
            bio = fetch_profile_bio(person["profile_url"])
            print(f"  bio: {len(bio)} chars")

        time.sleep(RATE_LIMIT_SECONDS)

        profiles[slug] = {
            "name": name,
            "profile_url": person["profile_url"],
            "role": person["role"],
            "position": person["position"],
            "secondary_position": person["secondary_position"],
            "research_areas": person["research_areas"],
            "bio": bio,
            "image_path": img_dest if img_ok else "",
        }

    # Write profiles.json
    os.makedirs(os.path.dirname(PROFILES_PATH), exist_ok=True)
    with open(PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

    found = sum(1 for p in profiles.values() if p["image_path"])
    print(f"\n=== Summary ===")
    print(f"  Images saved : {found} / {len(profiles)}")
    print(f"  Profiles saved to: {PROFILES_PATH}")
    print(f"  Images in: {RAW_IMAGES_DIR}")


if __name__ == "__main__":
    build_dataset()
