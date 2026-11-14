"""Tope de consumo por API: frena el pipeline antes de salirse del plan gratis."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from lead_engine.core.config import ApiLimit


class BudgetExceeded(RuntimeError):
    pass


class UsageStore(Protocol):
    def usage_day(self, api: str, day: date) -> int: ...
    def usage_month(self, api: str, day: date) -> int: ...
    def usage_add(self, api: str, day: date, calls: int) -> None: ...


class CostGuard:
    def __init__(self, store: UsageStore, limits: dict[str, ApiLimit], today: date | None = None):
        self.store = store
        self.limits = limits
        self.today = today or date.today()
        self.session_calls: dict[str, int] = {}

    def charge(self, api: str, calls: int = 1) -> None:
        """Registra `calls` llamadas o levanta BudgetExceeded si se pasaría del tope."""
        limit = self.limits.get(api)
        if limit is not None:
            day_used = self.store.usage_day(api, self.today)
            month_used = self.store.usage_month(api, self.today)
            if day_used + calls > limit.por_dia:
                raise BudgetExceeded(f"Tope diario de {api} alcanzado ({day_used}/{limit.por_dia}).")
            if month_used + calls > limit.por_mes:
                raise BudgetExceeded(f"Tope mensual de {api} alcanzado ({month_used}/{limit.por_mes}).")
        self.store.usage_add(api, self.today, calls)
        self.session_calls[api] = self.session_calls.get(api, 0) + calls

    def summary(self) -> dict[str, dict[str, int]]:
        return {
            api: {
                "esta_corrida": n,
                "hoy": self.store.usage_day(api, self.today),
                "mes": self.store.usage_month(api, self.today),
            }
            for api, n in self.session_calls.items()
        }
