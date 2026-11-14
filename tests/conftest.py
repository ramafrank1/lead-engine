import pytest

from lead_engine.core.config import load_business_config


@pytest.fixture
def cfg():
    return load_business_config()


def api_place(pid, name, *, phone=None, website=None, rating=4.5, count=120, status="OPERATIONAL",
              lat=-34.5430, lng=-58.7120):
    """Arma un resultado con la forma que devuelve Places API (New)."""
    raw = {
        "id": pid,
        "displayName": {"text": name, "languageCode": "es"},
        "formattedAddress": f"{name} 123, San Miguel, Provincia de Buenos Aires",
        "location": {"latitude": lat, "longitude": lng},
        "rating": rating,
        "userRatingCount": count,
        "businessStatus": status,
        "googleMapsUri": f"https://maps.google.com/?cid={pid}",
    }
    if phone:
        raw["internationalPhoneNumber"] = phone
    if website:
        raw["websiteUri"] = website
    return raw
