from __future__ import annotations

import asyncio
import json
from typing import Any

import aiohttp

from backend.app.core.exceptions import ClaimLensError
from backend.app.core.logging import get_logger

logger = get_logger(__name__)


async def request_json(
    method: str,
    url: str,
    *,
    service: str,
    headers: dict[str, str] | None = None,
    json_body: Any = None,
    params: list[tuple[str, str]] | dict[str, str] | None = None,
    timeout: float = 20.0,
    retries: int = 1,
) -> Any:
    """HTTP call returning parsed JSON. Retries on 429/5xx/network errors with backoff."""
    last: ClaimLensError | None = None
    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.request(method, url, headers=headers, json=json_body, params=params) as resp:
                    text = await resp.text()
                    if resp.status == 429 or resp.status >= 500:
                        last = ClaimLensError(
                            f"{service} HTTP {resp.status}: {text[:300]}", code=f"{service}_http_{resp.status}"
                        )
                        logger.warning("%s (attempt %s/%s)", last.message, attempt, retries)
                    elif resp.status >= 400:
                        raise ClaimLensError(
                            f"{service} HTTP {resp.status}: {text[:300]}", code=f"{service}_http_{resp.status}"
                        )
                    else:
                        return json.loads(text) if text.strip() else None
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            last = ClaimLensError(f"{service} request failed: {exc}", code=f"{service}_network")
            logger.warning("%s (attempt %s/%s)", last.message, attempt, retries)
        if attempt < retries:
            await asyncio.sleep(min(0.5 * 2**attempt, 8))
    raise last or ClaimLensError(f"{service} request failed", code=f"{service}_failed")
