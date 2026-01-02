import sqlite3
from pathlib import Path
from typing import Iterable, Dict, Any, List, Optional

DB_PATH = Path(__file__).parent / "data.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL,
  category TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  published_at TEXT,
  fetched_at TEXT NOT NULL,
  UNIQUE(source_id, url)
);

CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_items_source ON items(source_id);
CREATE INDEX IF NOT EXISTS idx_items_fetched ON items(fetched_at);
"""

def get_conn():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn

def init_db():
  conn = get_conn()
  try:
    conn.executescript(SCHEMA)
    conn.commit()
  finally:
    conn.close()

def upsert_items(rows: Iterable[Dict[str, Any]]) -> int:
  conn = get_conn()
  inserted = 0
  try:
    cur = conn.cursor()
    for r in rows:
      try:
        cur.execute(
          """
          INSERT OR IGNORE INTO items
          (source_id, category, title, url, published_at, fetched_at)
          VALUES (?, ?, ?, ?, ?, ?)
          """,
          (r["source_id"], r["category"], r["title"], r["url"], r.get("published_at"), r["fetched_at"])
        )
        if cur.rowcount == 1:
          inserted += 1
      except Exception:
        continue
    conn.commit()
    return inserted
  finally:
    conn.close()

def search_items(q: str = "", category: Optional[str] = None, source_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
  conn = get_conn()
  try:
    sql = "SELECT source_id, category, title, url, published_at, fetched_at FROM items WHERE 1=1"
    params = []

    if q.strip():
      sql += " AND (title LIKE ? OR url LIKE ?)"
      like = f"%{q.strip()}%"
      params += [like, like]

    if category and category != "ALL":
      sql += " AND category = ?"
      params.append(category)

    if source_id and source_id != "ALL":
      sql += " AND source_id = ?"
      params.append(source_id)

    sql += " ORDER BY fetched_at DESC LIMIT ?"
    params.append(int(limit))

    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]
  finally:
    conn.close()
