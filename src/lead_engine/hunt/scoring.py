"""Score 0–100 de cada lead, con pesos de `config/scoring.yaml`."""

from __future__ import annotations

import math

from lead_engine.core.config import ScoringWeights


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def score_lead(
    *,
    web_status: str,
    rating: float | None,
    rating_count: int,
    ticket_alto: bool,
    rubro_label: str,
    has_phone: bool,
    is_mobile: bool,
    distance_km: float | None,
    w: ScoringWeights,
    web_penalty: int = 0,
) -> tuple[int, str]:
    """Devuelve (score, motivo legible). `web_penalty` lo aporta la auditoría (Fase 2)."""
    points = 0
    reasons: list[str] = []

    if web_status == "none":
        points += w.sin_web
        reasons.append("Sin web")
    elif web_status == "social":
        points += w.solo_redes
        reasons.append("Solo redes")
    elif web_penalty:
        points += max(w.web_mala_min, min(w.web_mala_max, web_penalty))
        reasons.append("Web mala")
    else:
        reasons.append("Tiene web")

    if rating_count > 0:
        ratio = math.log10(rating_count + 1) / math.log10(w.resenas_saturacion + 1)
        points += round(w.resenas_max * min(1.0, ratio))
        reasons.append(f"{rating_count} reseñas")

    if rating is not None and rating >= w.rating_minimo:
        points += w.rating_bonus
        reasons.append(f"{rating:.1f}★")

    if ticket_alto:
        points += w.ticket_alto
        reasons.append(rubro_label.lower())

    if not has_phone:
        points += w.sin_telefono
        reasons.append("sin teléfono")
    elif is_mobile:
        points += w.celular
        reasons.append("celular")
    else:
        reasons.append("teléfono fijo")

    if distance_km is not None:
        closeness = max(0.0, 1 - distance_km / w.cercania_km_max)
        points += round(w.cercania_max * closeness)

    return max(0, min(100, points)), ", ".join(reasons)
