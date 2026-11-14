"""Cliente de Google Places API (New) — Text Search. API oficial, nada de scraping."""

from __future__ import annotations

from collections.abc import Iterator

import httpx

from lead_engine.core.cost_guard import CostGuard
from lead_engine.core.models import Place

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
API_NAME = "places_text_search"
PAGE_SIZE = 20
MAX_RESULTS_PER_QUERY = 60  # límite de Google: 3 páginas de 20

# Solo los campos que usamos. Teléfono/web/rating/horarios hacen que la llamada sea SKU Enterprise.
FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.location",
        "places.nationalPhoneNumber",
        "places.internationalPhoneNumber",
        "places.websiteUri",
        "places.rating",
        "places.userRatingCount",
        "places.businessStatus",
        "places.regularOpeningHours.weekdayDescriptions",
        "places.googleMapsUri",
        "places.primaryType",
        "nextPageToken",
    ]
)


class PlacesError(RuntimeError):
    pass


class PlacesClient:
    def __init__(self, api_key: str, guard: CostGuard, http: httpx.Client | None = None):
        if not api_key:
            raise PlacesError("Falta GOOGLE_API_KEY en .env")
        self.api_key = api_key
        self.guard = guard
        self.http = http or httpx.Client(timeout=30)

    def search_text(
        self, query: str, *, lat: float, lng: float, radius_km: float, max_results: int = MAX_RESULTS_PER_QUERY
    ) -> Iterator[Place]:
        body = {
            "textQuery": query,
            "languageCode": "es",
            "regionCode": "AR",
            "pageSize": PAGE_SIZE,
            "locationBias": {
                "circle": {"center": {"latitude": lat, "longitude": lng}, "radius": radius_km * 1000}
            },
        }
        headers = {"X-Goog-Api-Key": self.api_key, "X-Goog-FieldMask": FIELD_MASK}
        returned = 0
        limit = min(max_results, MAX_RESULTS_PER_QUERY)
        while returned < limit:
            self.guard.charge(API_NAME)
            resp = self.http.post(TEXT_SEARCH_URL, json=body, headers=headers)
            if resp.status_code != 200:
                raise PlacesError(f"Places respondió {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            for raw in data.get("places", []):
                yield Place.from_api(raw)
                returned += 1
                if returned >= limit:
                    return
            token = data.get("nextPageToken")
            if not token:
                return
            body = {**body, "pageToken": token}
