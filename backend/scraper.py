import time
import yaml
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

CONFIG_PATH = Path(__file__).parent / "sources.yaml"

DEFAULT_HEADERS = {
  "User-Agent": "jp-immigration-monitor/1.0 (course project; contact: your-email@example.com)"
}

def now_iso():
  return datetime.now(timezone.utc).isoformat()

def load_sources() -> List[Dict[str, Any]]:
  data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
  return data.get("sources", [])

def fetch_html(url: str, timeout: int = 15) -> str:
  resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
  resp.raise_for_status()
  return resp.text

def parse_list_page(source: Dict[str, Any], html: str) -> List[Dict[str, Any]]:
  soup = BeautifulSoup(html, "html.parser")
  items = []

  item_sel = source["item_selector"]
  title_sel = source.get("title_selector", ":scope")
  link_sel = source.get("link_selector", ":scope")

  for node in soup.select(item_sel)[:50]:
    title_node = node.select_one(title_sel) if title_sel != ":scope" else node
    link_node = node.select_one(link_sel) if link_sel != ":scope" else node

    title = (title_node.get_text(" ", strip=True) if title_node else "").strip()
    href = (link_node.get("href") if link_node else None)

    if not title or not href:
      continue

    full_url = urljoin(source["url"], href)
    items.append({
      "source_id": source["id"],
      "category": source.get("category", "Notice"),
      "title": title[:300],
      "url": full_url,
      "published_at": None,
      "fetched_at": now_iso()
    })
  return items

def run_scrape(rate_limit_seconds: float = 1.2) -> List[Dict[str, Any]]:
  sources = load_sources()
  all_items: List[Dict[str, Any]] = []

  for s in sources:
    try:
      html = fetch_html(s["url"])
      all_items.extend(parse_list_page(s, html))
      time.sleep(rate_limit_seconds)  # 限速
    except Exception:
      continue

  return all_items
