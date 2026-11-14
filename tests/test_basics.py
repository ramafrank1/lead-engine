from datetime import date

import pytest

from lead_engine.core.config import ApiLimit
from lead_engine.core.cost_guard import BudgetExceeded, CostGuard
from lead_engine.core.phone import normalize_ar
from lead_engine.db.repo import MemoryRepo
from lead_engine.hunt.scoring import score_lead
from lead_engine.hunt.web import classify_website


@pytest.mark.parametrize(
    "raw, wa",
    [
        ("+54 9 11 5555-4444", "5491155554444"),
        ("011 15-5555-4444", "5491155554444"),
        ("11 5555-4444", None),            # sin 15/9 es fijo de CABA/GBA
        ("+54 11 4666-7777", None),
    ],
)
def test_normalize_ar(raw, wa):
    info = normalize_ar(raw)
    assert info is not None
    assert info.wa_number == wa
    assert info.is_mobile == (wa is not None)


def test_normalize_invalid():
    assert normalize_ar("") is None
    assert normalize_ar("123") is None


@pytest.mark.parametrize(
    "url, status, domain, ig",
    [
        (None, "none", None, None),
        ("https://www.instagram.com/corralon.losandes/", "social", None, "corralon.losandes"),
        ("linktr.ee/gymfuerte", "social", None, None),
        ("https://wa.me/5491155554444", "social", None, None),
        ("http://www.corralonlosandes.com.ar/contacto", "own", "corralonlosandes.com.ar", None),
    ],
)
def test_classify_website(url, status, domain, ig):
    info = classify_website(url)
    assert (info.status, info.domain, info.instagram) == (status, domain, ig)


def test_score_sin_web_constructora(cfg):
    score, reason = score_lead(
        web_status="none", rating=4.6, rating_count=230, ticket_alto=True, rubro_label="Constructora",
        has_phone=True, is_mobile=True, distance_km=0, w=cfg.scoring,
    )
    # 40 sin web + ~19 reseñas + 10 rating + 10 ticket + 10 celular + 5 cercanía
    assert 90 <= score <= 100
    assert reason == "Sin web, 230 reseñas, 4.6★, constructora, celular"


def test_score_sin_telefono_queda_bajo(cfg):
    score, _ = score_lead(
        web_status="own", rating=3.9, rating_count=3, ticket_alto=False, rubro_label="Gimnasio",
        has_phone=False, is_mobile=False, distance_km=40, w=cfg.scoring,
    )
    assert score == 0


def test_cost_guard_frena(cfg):
    guard = CostGuard(MemoryRepo(), {"x": ApiLimit(por_dia=2, por_mes=10)}, today=date(2026, 10, 28))
    guard.charge("x")
    guard.charge("x")
    with pytest.raises(BudgetExceeded):
        guard.charge("x")
    assert guard.summary()["x"]["hoy"] == 2


def test_cost_guard_mensual_persistido(tmp_path):
    usage = tmp_path / "usage.json"
    limits = {"x": ApiLimit(por_dia=100, por_mes=3)}
    CostGuard(MemoryRepo(usage), limits, today=date(2026, 10, 1)).charge("x", 2)
    guard = CostGuard(MemoryRepo(usage), limits, today=date(2026, 10, 28))
    guard.charge("x")
    with pytest.raises(BudgetExceeded):
        guard.charge("x")
    # otro mes arranca de cero
    CostGuard(MemoryRepo(usage), limits, today=date(2026, 11, 1)).charge("x", 3)
