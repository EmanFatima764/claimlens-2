from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError
from backend.app.core.logging import get_logger
from backend.app.integrations.http import request_json

logger = get_logger(__name__)

# Shared in-memory store used when Supabase isn't configured (local dev / tests).
_MEMORY: dict[str, list[dict[str, Any]]] = {}


def reset_memory() -> None:
    _MEMORY.clear()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupabaseClient:
    """Thin async client over Supabase's PostgREST API (no raw SQL).

    If SUPABASE_URL / key are missing it falls back to a process-wide in-memory store,
    so the whole pipeline can run locally. Data is lost on restart in that mode.
    """

    def __init__(self, url: str | None = None, key: str | None = None) -> None:
        self.url = (url or settings.supabase_url).rstrip("/")
        self.key = key or settings.supabase_service_role_key or settings.supabase_anon_key
        self.use_memory = not (self.url and self.key)
        if self.use_memory:
            logger.warning("Supabase not configured - using in-memory store (data is lost on restart)")

    # ------------------------------------------------------------------ helpers
    def _headers(self, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _rest(self, table: str) -> str:
        return f"{self.url}/rest/v1/{table}"

    @staticmethod
    def _eq(filters: dict[str, Any] | None) -> list[tuple[str, str]]:
        return [(k, f"eq.{v}") for k, v in (filters or {}).items()]

    @staticmethod
    def _matches(row: dict[str, Any], filters: dict[str, Any] | None) -> bool:
        return all(str(row.get(k)) == str(v) for k, v in (filters or {}).items())

    # --------------------------------------------------------------------- CRUD
    async def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        if self.use_memory:
            new = {"id": str(uuid.uuid4()), "created_at": _now(), "updated_at": _now(), **row}
            _MEMORY.setdefault(table, []).append(new)
            return dict(new)
        data = await request_json(
            "POST", self._rest(table), service="supabase",
            headers=self._headers("return=representation"), json_body=row, timeout=8.0, retries=1,
        )
        return data[0]

    async def select(
        self,
        table: str,
        *,
        filters: dict[str, Any] | None = None,
        order: str | None = None,
        desc: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        if self.use_memory:
            rows = [dict(r) for r in _MEMORY.get(table, []) if self._matches(r, filters)]
            if order:
                rows.sort(key=lambda r: (r.get(order) is None, r.get(order)), reverse=False)
                if desc:
                    rows.reverse()
            return rows[:limit] if limit else rows
        params = [("select", "*"), *self._eq(filters)]
        if order:
            params.append(("order", f"{order}.{'desc' if desc else 'asc'}"))
        if limit:
            params.append(("limit", str(limit)))
        data = await request_json(
            "GET", self._rest(table), service="supabase", headers=self._headers(), params=params, timeout=8.0, retries=1
        )
        return data or []

    async def update(self, table: str, filters: dict[str, Any], values: dict[str, Any]) -> list[dict[str, Any]]:
        values = {**values, "updated_at": _now()} if table == "investigations" else values
        if self.use_memory:
            out = []
            for row in _MEMORY.get(table, []):
                if self._matches(row, filters):
                    row.update(values)
                    out.append(dict(row))
            return out
        data = await request_json(
            "PATCH", self._rest(table), service="supabase",
            headers=self._headers("return=representation"), json_body=values, params=self._eq(filters), timeout=8.0, retries=1,
        )
        return data or []

    async def upsert(self, table: str, row: dict[str, Any], on_conflict: str) -> dict[str, Any]:
        if self.use_memory:
            for existing in _MEMORY.get(table, []):
                if str(existing.get(on_conflict)) == str(row.get(on_conflict)):
                    existing.update(row)
                    return dict(existing)
            return await self.insert(table, row)
        data = await request_json(
            "POST", self._rest(table), service="supabase",
            headers=self._headers("resolution=merge-duplicates,return=representation"),
            json_body=row, params=[("on_conflict", on_conflict)],
        )
        return data[0]

    async def delete(self, table: str, filters: dict[str, Any]) -> None:
        if not filters:
            raise ClaimLensError("Refusing to delete without filters", code="unsafe_delete")
        if self.use_memory:
            _MEMORY[table] = [r for r in _MEMORY.get(table, []) if not self._matches(r, filters)]
            return
        await request_json(
            "DELETE", self._rest(table), service="supabase", headers=self._headers(), params=self._eq(filters)
        )

    async def health_check(self) -> dict[str, Any]:
        if self.use_memory:
            return {"status": "ok", "service": "memory"}
        await self.select("investigations", limit=1)
        return {"status": "ok", "service": "supabase"}
