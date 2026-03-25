import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

INPUT_PATH = Path("data/raw/links.json")
OUTPUT_PATH = Path("data/raw/articles_raw.json")


HEADERS = {
    "User-Agent": "NewsCrawler/1.0"
}

def ensure_output_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    
def load_links(input_path: Path) -> list[dict]:
    if not input_path.exists():
        print(f"Filen finns inte: {input_path}")
        return []

    with input_path.open("r", encoding="utf-8") as f:
        return json.load(f)
    
# Get the HTML code of a url
def fetch_html(url: str) -> str | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Kunde inte hämta artikel {url}: {e}")
        return None
    
def extract_title(soup: BeautifulSoup) -> str:
    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)

    # fallback
    h1_tag = soup.find("h1")
    if h1_tag and h1_tag.get_text(strip=True):
        return h1_tag.get_text(strip=True)

    return ""

def extract_paragraphs_from_article(soup: BeautifulSoup) -> list[str]:
    # try to find <article>
    article_tag = soup.find("article")

    if article_tag:
        paragraphs = article_tag.find_all("p")
    else:
        paragraphs = soup.find_all("p")

    texts = []
    for p in paragraphs:
        text = p.get_text(" ", strip=True)
        if text:
            texts.append(text)

    return texts

def clean_whitespace(text: str) -> str:
    return " ".join(text.split())

def extract_article_data(link_item: dict) -> dict | None:
    url = link_item["url"]
    html = fetch_html(url)

    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = extract_title(soup)
    paragraphs = extract_paragraphs_from_article(soup)
    content = clean_whitespace(" ".join(paragraphs))

    if not title:
        print(f"Hoppar över {url}: ingen titel hittades")
        return None

    if len(content) < 200:
        print(f"Hoppar över {url}: för kort innehåll")
        return None

    domain = urlparse(url).netloc

    article = {
        "url": url,
        "title": title,
        "content": content,
        "content_length": len(content),
        "source_domain": domain,
        "source_feed": link_item.get("source_feed", ""),
        "rss_title": link_item.get("title", ""),
        "published": link_item.get("published", "")
    }

    return article

def save_articles(articles: list[dict], output_path: Path) -> None:
    ensure_output_directory(output_path)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        
def main():
    links = load_links(INPUT_PATH)
    if not links:
        print("No links")
        return

    articles = []

    for i, link_item in enumerate(links, start=1):
        url = link_item["url"]
        print(f"[{i}/{len(links)}] getting article: {url}")

        article = extract_article_data(link_item)
        if article:
            articles.append(article)
            print(f"  saved: {article['title']}")

    save_articles(articles, OUTPUT_PATH)
    print(f"\nSaved {len(articles)} articles to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()