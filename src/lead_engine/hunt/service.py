"""`lead hunt`: busca, filtra, deduplica y puntúa negocios de un rubro y una zona."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

from lead_engine.core.config import BusinessConfig, Rubro, Zona
from lead_engine.core.models import Place, ScoredLead
from lead_engine.core.phone import normalize_ar
from lead_engine.db.repo import Repo
from lead_engine.hunt.scoring import haversine_km, score_lead
from lead_engine.hunt.web import classify_website

SearchFn = Callable[..., Iterator[Place]]


@dataclass
class HuntStats:
    vistos: int = 0
    cerrados: int = 0
    lejos: int = 0
    duplicados: int = 0
    blacklist: int = 0
    nuevos: int = 0
    queries: list[str] = field(default_factory=list)


@dataclass
class HuntResult:
    leads: list[ScoredLead]
    stats: HuntStats


def build_lead(place: Place, rubro: Rubro, zona: Zona, cfg: BusinessConfig) -> ScoredLead:
    web = classify_website(place.website)
    phone = normalize_ar(place.intl_phone or place.national_phone)
    base = cfg.base
    distance = (
        haversine_km(base.lat, base.lng, place.lat, place.lng) if place.lat is not None and place.lng is not None else None
    )
    score, reason = score_lead(
        web_status=web.status,
        rating=place.rating,
        rating_count=place.rating_count,
        ticket_alto=rubro.ticket_alto,
        rubro_label=rubro.label,
        has_phone=phone is not None,
        is_mobile=bool(phone and phone.is_mobile),
        distance_km=distance,
        w=cfg.scoring,
    )
    return ScoredLead(
        place=place,
        rubro=rubro.key,
        zona=zona.key,
        web_status=web.status,
        domain=web.domain,
        instagram=web.instagram,
        facebook=web.facebook,
        wa_phone=phone.wa_number if phone else None,
        phone_e164=phone.e164 if phone else None,
        distance_km=round(distance, 1) if distance is not None else None,
        score=score,
        score_reason=reason,
    )


def run_hunt(
    *, rubro: Rubro, zona: Zona, max_leads: int, cfg: BusinessConfig, repo: Repo, search: SearchFn
) -> HuntResult:
    stats = HuntStats()
    known = repo.known_keys()
    banned = repo.blacklist()
    seen = {k: set(v) for k, v in known.items()}
    leads: list[ScoredLead] = []
    processed: set[str] = set()

    for q in rubro.queries:
        if len(leads) >= max_leads:
            break
        query = f"{q} en {zona.label}, Buenos Aires"
        stats.queries.append(query)
        for place in search(query, lat=zona.lat, lng=zona.lng, radius_km=zona.radius_km):
            # El mismo negocio suele aparecer en varias búsquedas sinónimas: se procesa una sola vez.
            if place.place_id in processed:
                continue
            processed.add(place.place_id)
            stats.vistos += 1
            if place.business_status == "CLOSED_PERMANENTLY":
                stats.cerrados += 1
                continue
            if place.lat is not None and haversine_km(zona.lat, zona.lng, place.lat, place.lng) > zona.max_km:
                stats.lejos += 1
                continue
            lead = build_lead(place, rubro, zona, cfg)
            if (
                place.place_id in banned["place_id"]
                or (lead.phone_e164 and lead.phone_e164 in banned["phone"])
                or (lead.domain and lead.domain in banned["domain"])
            ):
                stats.blacklist += 1
                continue
            if (
                place.place_id in seen["place_id"]
                or (lead.phone_e164 and lead.phone_e164 in seen["phone"])
                or (lead.domain and lead.domain in seen["domain"])
            ):
                stats.duplicados += 1
                continue
            seen["place_id"].add(place.place_id)
            if lead.phone_e164:
                seen["phone"].add(lead.phone_e164)
            if lead.domain:
                seen["domain"].add(lead.domain)
            leads.append(lead)
            if len(leads) >= max_leads:
                break

    leads.sort(key=lambda l: l.score, reverse=True)
    stats.nuevos = len(leads)
    return HuntResult(leads=leads, stats=stats)
