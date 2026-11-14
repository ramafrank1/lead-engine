"""Clasifica el campo "website" de Google: sin web, solo redes o web propia."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

# Dominios que no cuentan como "web propia".
SOCIAL_DOMAINS = {
    "instagram.com", "facebook.com", "fb.com", "m.facebook.com", "tiktok.com",
    "linktr.ee", "linktree.com", "beacons.ai", "taplink.cc", "linkin.bio", "bio.link",
    "wa.me", "api.whatsapp.com", "whatsapp.com", "wa.link",
    "mercadolibre.com.ar", "mercadoshops.com.ar", "twitter.com", "x.com", "youtube.com",
}


@dataclass(frozen=True)
class WebInfo:
    status: str                 # none | social | own
    domain: str | None = None   # solo si es web propia
    instagram: str | None = None
    facebook: str | None = None


def _host(url: str) -> str:
    if "://" not in url:
        url = "https://" + url
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def _first_path_segment(url: str) -> str | None:
    if "://" not in url:
        url = "https://" + url
    parts = [p for p in urlparse(url).path.split("/") if p]
    return parts[0] if parts else None


def classify_website(url: str | None) -> WebInfo:
    if not url or not url.strip():
        return WebInfo(status="none")
    host = _host(url.strip())
    if not host:
        return WebInfo(status="none")
    is_social = host in SOCIAL_DOMAINS or any(host.endswith("." + d) for d in SOCIAL_DOMAINS)
    if not is_social:
        return WebInfo(status="own", domain=host)
    handle = _first_path_segment(url)
    return WebInfo(
        status="social",
        instagram=handle if host.endswith("instagram.com") else None,
        facebook=handle if "facebook.com" in host or host == "fb.com" else None,
    )
