import json 
import requests
import xml.etree.ElementTree as ET #read and interprete XML (RSS in XML)
from pathlib import Path
from urllib.parse import urlparse

# get more from here if needed https://www.nytimes.com/rss
RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Africa.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Education.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/EnergyEnvironment.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/SmallBusiness.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/DealBook.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/MediaandAdvertising.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/YourMoney.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
    
]

# For implementing web crawler without RSS
START_URLS = [
    "https://www.bbc.com",
    "https://www.reuters.com",
]

MAX_PAGES_PER_DOMAIN = 30
DELAY_S = 1.0

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "links.json"

def ensure_output_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    
def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False

def fetch_rss_content(feed_url: str) -> str | None:
    headers = {
        "User-Agent": "NewsCrawler/1.0"
    }
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"couldnt fetch RSS-feed {feed_url}: {e}")
        return None

def parse_rss_links(xml_text: str, source_feed: str) -> list[dict]:
    links = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"couldnt parse XML from {source_feed}: {e}")
        return links
    
    # channel -> item structure assumed
    for item in root.findall(".//item"):
        link_elem = item.find("link")
        title_elem = item.find("title")
        pubdate_elem = item.find("pubDate")
        
        url = link_elem.text.strip() if link_elem is not None and link_elem.text else None
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
        published = pubdate_elem.text.strip() if pubdate_elem is not None and pubdate_elem.text else ""

        if url and is_valid_url(url):
            links.append({
                "url": url,
                "title": title,
                "published": published,
                "source_feed": source_feed
            })
    return links

def deduplicate_links(links: list[dict]) -> list[dict]:
    seen = set()
    unique_links = []
    for item in links:
        url = item["url"]
        if url not in seen:
            seen.add(url)
            unique_links.append(item)
    return unique_links

def save_links(links: list[dict], output_path: Path) -> None:
    ensure_output_directory(output_path)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)
        
def main():
    all_links = []
    for feed_url in RSS_FEEDS:
        print(f"fetching RSS feed: {feed_url}")
        xml_text = fetch_rss_content(feed_url)
        if xml_text is None:
            continue
        parsed_links = parse_rss_links(xml_text, feed_url)
        print(f"found {len(parsed_links)} links in {feed_url}")
        all_links.extend(parsed_links)
    
    unique_links = deduplicate_links(all_links)
    print(f"tot number of unique links: {len(unique_links)}")
    
    save_links(unique_links, OUTPUT_PATH)
    print(f"saved links to {OUTPUT_PATH}")
    
if __name__ == "__main__":
    main()