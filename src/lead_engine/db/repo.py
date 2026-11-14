"""Acceso a datos. `PgRepo` usa Supabase/Postgres; `MemoryRepo` sirve para el modo prueba y los tests."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Protocol

from lead_engine.core.models import ScoredLead

BLACKLIST_KINDS = ("phone", "domain", "place_id")


class Repo(Protocol):
    persistent: bool

    def blacklist(self) -> dict[str, set[str]]: ...
    def add_blacklist(self, kind: str, value: str, reason: str | None = None) -> None: ...
    def known_keys(self) -> dict[str, set[str]]: ...
    def save_leads(self, leads: list[ScoredLead]) -> int: ...
    def purge_place_cache(self, days: int) -> int: ...
    def usage_day(self, api: str, day: date) -> int: ...
    def usage_month(self, api: str, day: date) -> int: ...
    def usage_add(self, api: str, day: date, calls: int) -> None: ...


class MemoryRepo:
    """Nada se guarda salvo el consumo de APIs (en un JSON local, para que el tope funcione igual)."""

    persistent = False

    def __init__(self, usage_file: Path | None = None):
        self.usage_file = usage_file
        self._blacklist: dict[str, set[str]] = {k: set() for k in BLACKLIST_KINDS}
        self.leads: dict[str, ScoredLead] = {}
        self._usage: dict[str, int] = {}
        if usage_file and usage_file.exists():
            self._usage = json.loads(usage_file.read_text(encoding="utf-8"))

    def blacklist(self) -> dict[str, set[str]]:
        return self._blacklist

    def add_blacklist(self, kind: str, value: str, reason: str | None = None) -> None:
        self._blacklist[kind].add(value)

    def known_keys(self) -> dict[str, set[str]]:
        leads = self.leads.values()
        return {
            "place_id": {l.place.place_id for l in leads},
            "phone": {l.phone_e164 for l in leads if l.phone_e164},
            "domain": {l.domain for l in leads if l.domain},
        }

    def save_leads(self, leads: list[ScoredLead]) -> int:
        for lead in leads:
            self.leads[lead.place.place_id] = lead
        return len(leads)

    def purge_place_cache(self, days: int) -> int:
        return 0

    def _key(self, api: str, day: date) -> str:
        return f"{api}|{day.isoformat()}"

    def usage_day(self, api: str, day: date) -> int:
        return self._usage.get(self._key(api, day), 0)

    def usage_month(self, api: str, day: date) -> int:
        prefix = f"{api}|{day.isoformat()[:7]}"
        return sum(n for k, n in self._usage.items() if k.startswith(prefix))

    def usage_add(self, api: str, day: date, calls: int) -> None:
        key = self._key(api, day)
        self._usage[key] = self._usage.get(key, 0) + calls
        if self.usage_file:
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            self.usage_file.write_text(json.dumps(self._usage, indent=1), encoding="utf-8")


class PgRepo:
    persistent = True

    def __init__(self, dsn: str):
        import psycopg

        self.conn = psycopg.connect(dsn, autocommit=True)

    def blacklist(self) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {k: set() for k in BLACKLIST_KINDS}
        for kind, value in self.conn.execute("select kind, value from blacklist"):
            out[kind].add(value)
        return out

    def add_blacklist(self, kind: str, value: str, reason: str | None = None) -> None:
        self.conn.execute(
            "insert into blacklist (kind, value, reason) values (%s, %s, %s) on conflict do nothing",
            (kind, value, reason),
        )

    def known_keys(self) -> dict[str, set[str]]:
        place_ids = {r[0] for r in self.conn.execute("select place_id from leads where place_id is not null")}
        phones = {r[0] for r in self.conn.execute("select wa_phone from place_cache where wa_phone is not null")}
        phones |= {r[0] for r in self.conn.execute("select verified_wa from leads where verified_wa is not null")}
        domains = {r[0] for r in self.conn.execute("select domain from place_cache where domain is not null")}
        return {"place_id": place_ids, "phone": phones, "domain": domains}

    def save_leads(self, leads: list[ScoredLead]) -> int:
        with self.conn.transaction():
            for lead in leads:
                self.conn.execute(
                    """
                    insert into leads (place_id, source, rubro, zona, web_status, score, score_reason, instagram, facebook)
                    values (%s, 'maps', %s, %s, %s, %s, %s, %s, %s)
                    on conflict (place_id) do update set
                      web_status = excluded.web_status, score = excluded.score,
                      score_reason = excluded.score_reason,
                      instagram = coalesce(leads.instagram, excluded.instagram),
                      facebook = coalesce(leads.facebook, excluded.facebook)
                    """,
                    (lead.place.place_id, lead.rubro, lead.zona, lead.web_status, lead.score,
                     lead.score_reason, lead.instagram, lead.facebook),
                )
                self.conn.execute(
                    """
                    insert into place_cache (place_id, data, wa_phone, domain, fetched_at)
                    values (%s, %s, %s, %s, now())
                    on conflict (place_id) do update set
                      data = excluded.data, wa_phone = excluded.wa_phone,
                      domain = excluded.domain, fetched_at = now()
                    """,
                    (lead.place.place_id, lead.place.model_dump_json(), lead.phone_e164, lead.domain),
                )
        return len(leads)

    def purge_place_cache(self, days: int) -> int:
        cur = self.conn.execute(
            "delete from place_cache where fetched_at < now() - make_interval(days => %s)", (days,)
        )
        return cur.rowcount

    def usage_day(self, api: str, day: date) -> int:
        row = self.conn.execute("select calls from api_usage where api = %s and day = %s", (api, day)).fetchone()
        return row[0] if row else 0

    def usage_month(self, api: str, day: date) -> int:
        row = self.conn.execute(
            "select coalesce(sum(calls), 0) from api_usage where api = %s and date_trunc('month', day) = date_trunc('month', %s::date)",
            (api, day),
        ).fetchone()
        return int(row[0])

    def usage_add(self, api: str, day: date, calls: int) -> None:
        self.conn.execute(
            """
            insert into api_usage (day, api, calls) values (%s, %s, %s)
            on conflict (day, api) do update set calls = api_usage.calls + excluded.calls
            """,
            (day, api, calls),
        )


def open_repo(database_url: str, usage_file: Path) -> Repo:
    return PgRepo(database_url) if database_url else MemoryRepo(usage_file)
