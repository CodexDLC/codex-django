from typing import Any


class DjangoArqClient:
    """Wrapper around codex_platform ARQ client to provide both sync and async methods."""

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Enqueue task synchronously."""
        return None

    async def aenqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Enqueue task asynchronously."""
        return None
