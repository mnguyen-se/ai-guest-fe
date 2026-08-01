"""
Kết nối tới Supabase (Postgres qua REST API).
Cần biến môi trường: SUPABASE_URL, SUPABASE_SERVICE_KEY
(dùng service_role key vì collector chạy ở backend, không phải trình duyệt)
"""
import os
from supabase import create_client, Client

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client


def upsert(table: str, rows: list[dict], on_conflict: str) -> None:
    """Ghi (insert hoặc update nếu trùng unique key) hàng loạt vào 1 bảng."""
    if not rows:
        return
    client = get_client()
    # Supabase python client giới hạn payload -> chia batch 500 dòng
    batch_size = 500
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        client.table(table).upsert(batch, on_conflict=on_conflict).execute()


def fetch_latest(table: str, order_col: str, limit: int = 100, filters: dict | None = None):
    client = get_client()
    q = client.table(table).select("*").order(order_col, desc=True).limit(limit)
    if filters:
        for k, v in filters.items():
            q = q.eq(k, v)
    return q.execute().data
