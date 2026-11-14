"""Configuración: secretos desde `.env` y parámetros de negocio desde `config/*.yaml`."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "out"
DATA_DIR = ROOT / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    google_api_key: str = ""
    database_url: str = ""
    places_cache_days: int = 30
    ai_provider: str = "none"
    owner_name: str = "Ramiro Frank"
    owner_whatsapp: str = ""
    owner_portfolio: str = "https://ramirofrank.pages.dev/"
    owner_postal_address: str = ""
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_refresh_token: str = ""


class Zona(BaseModel):
    key: str
    label: str
    lat: float
    lng: float
    radius_km: float
    max_km: float


class Rubro(BaseModel):
    key: str
    label: str
    queries: list[str]
    ticket_alto: bool = False


class ScoringWeights(BaseModel):
    sin_web: int
    solo_redes: int
    web_mala_min: int
    web_mala_max: int
    resenas_max: int
    resenas_saturacion: int
    rating_minimo: float
    rating_bonus: int
    ticket_alto: int
    celular: int
    sin_telefono: int
    cercania_max: int
    cercania_km_max: float


class ApiLimit(BaseModel):
    por_dia: int
    por_mes: int
    usd_por_1000: float = 0.0


class Limits(BaseModel):
    apis: dict[str, ApiLimit]
    contactos_nuevos_por_dia: int = 20


class BusinessConfig(BaseModel):
    zonas: dict[str, Zona]
    base_zona: str
    rubros: dict[str, Rubro]
    scoring: ScoringWeights
    limits: Limits

    @property
    def base(self) -> Zona:
        return self.zonas[self.base_zona]

    def zona(self, key_or_label: str) -> Zona:
        return _lookup(self.zonas, key_or_label, "zona")

    def rubro(self, key_or_label: str) -> Rubro:
        return _lookup(self.rubros, key_or_label, "rubro")


def _slug(text: str) -> str:
    import unicodedata

    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "-".join(plain.lower().replace(".", " ").split())


def _lookup(items: dict, key_or_label: str, what: str):
    wanted = _slug(key_or_label)
    for key, item in items.items():
        if wanted in (key, _slug(item.label)):
            return item
    options = ", ".join(items)
    raise KeyError(f"No conozco la {what} '{key_or_label}'. Opciones: {options}")


def _read_yaml(name: str, config_dir: Path) -> dict:
    with open(config_dir / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_business_config(config_dir: Path = CONFIG_DIR) -> BusinessConfig:
    zonas_raw = _read_yaml("zonas.yaml", config_dir)
    rubros_raw = _read_yaml("rubros.yaml", config_dir)
    return BusinessConfig(
        zonas={k: Zona(key=k, **v) for k, v in zonas_raw["zonas"].items()},
        base_zona=zonas_raw["base"],
        rubros={k: Rubro(key=k, **v) for k, v in rubros_raw["rubros"].items()},
        scoring=ScoringWeights(**_read_yaml("scoring.yaml", config_dir)),
        limits=Limits(**_read_yaml("limites.yaml", config_dir)),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
