"""Modelos de datos compartidos entre módulos."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Place(BaseModel):
    """Un negocio tal como lo devuelve Places API (New), ya aplanado."""

    place_id: str
    name: str
    address: str = ""
    lat: float | None = None
    lng: float | None = None
    national_phone: str | None = None
    intl_phone: str | None = None
    website: str | None = None
    rating: float | None = None
    rating_count: int = 0
    business_status: str | None = None
    opening_hours: list[str] = Field(default_factory=list)
    maps_url: str | None = None
    primary_type: str | None = None

    @classmethod
    def from_api(cls, raw: dict) -> "Place":
        loc = raw.get("location") or {}
        return cls(
            place_id=raw["id"],
            name=(raw.get("displayName") or {}).get("text", ""),
            address=raw.get("formattedAddress", ""),
            lat=loc.get("latitude"),
            lng=loc.get("longitude"),
            national_phone=raw.get("nationalPhoneNumber"),
            intl_phone=raw.get("internationalPhoneNumber"),
            website=raw.get("websiteUri"),
            rating=raw.get("rating"),
            rating_count=raw.get("userRatingCount", 0),
            business_status=raw.get("businessStatus"),
            opening_hours=(raw.get("regularOpeningHours") or {}).get("weekdayDescriptions", []),
            maps_url=raw.get("googleMapsUri"),
            primary_type=raw.get("primaryType"),
        )


class ScoredLead(BaseModel):
    place: Place
    rubro: str
    zona: str
    web_status: str              # none | social | own
    domain: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    wa_phone: str | None = None  # 549... si es celular
    phone_e164: str | None = None
    distance_km: float | None = None
    score: int
    score_reason: str
