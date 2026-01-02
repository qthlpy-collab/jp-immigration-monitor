from fastapi import FastAPI, Query
from db import init_db, upsert_items, search_items
from scraper import run_scrape

app = FastAPI(title="jp-immigration-monitor API", version="1.0")

@app.on_event("startup")
def startup():
  init_db()

@app.get("/api/health")
def health():
  return {"ok": True}

@app.post("/api/scrape")
def scrape_once():
  items = run_scrape()
  inserted = upsert_items(items)
  return {"fetched": len(items), "inserted": inserted}

@app.get("/api/search")
def search(
  q: str = Query(default=""),
  category: str = Query(default="ALL"),
  source_id: str = Query(default="ALL"),
  limit: int = Query(default=50, ge=1, le=200),
):
  results = search_items(q=q, category=category, source_id=source_id, limit=limit)
  return {"count": len(results), "items": results}
