"""Export a CSV. Por defecto solo datos propios + link a Maps (cumple los términos de Google)."""

from __future__ import annotations

import csv
from pathlib import Path

from lead_engine.core.models import ScoredLead

OWN_COLUMNS = ["place_id", "rubro", "zona", "score", "motivo", "web_status", "distancia_km", "maps_url"]
GOOGLE_COLUMNS = ["nombre", "direccion", "telefono", "whatsapp", "web", "rating", "resenas"]


def export_csv(leads: list[ScoredLead], path: Path, include_google_data: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = OWN_COLUMNS + (GOOGLE_COLUMNS if include_google_data else [])
    # utf-8-sig para que Excel muestre bien los acentos
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for lead in leads:
            p = lead.place
            row = {
                "place_id": p.place_id,
                "rubro": lead.rubro,
                "zona": lead.zona,
                "score": lead.score,
                "motivo": lead.score_reason,
                "web_status": lead.web_status,
                "distancia_km": lead.distance_km,
                "maps_url": p.maps_url or f"https://www.google.com/maps/place/?q=place_id:{p.place_id}",
            }
            if include_google_data:
                row |= {
                    "nombre": p.name,
                    "direccion": p.address,
                    "telefono": p.intl_phone or p.national_phone,
                    "whatsapp": lead.wa_phone,
                    "web": p.website,
                    "rating": p.rating,
                    "resenas": p.rating_count,
                }
            writer.writerow(row)
    return path
