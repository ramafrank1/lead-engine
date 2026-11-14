import csv
import json

import httpx
import pytest

from conftest import api_place
from lead_engine.core.cost_guard import BudgetExceeded, CostGuard
from lead_engine.core.config import ApiLimit
from lead_engine.db.repo import MemoryRepo
from lead_engine.hunt.export import export_csv
from lead_engine.hunt.places import FIELD_MASK, PlacesClient
from lead_engine.hunt.service import run_hunt


def fake_places(pages):
    """Transport que devuelve `pages` en orden y registra los requests."""
    calls = []

    def handler(request: httpx.Request):
        calls.append(request)
        body = json.loads(request.content)
        idx = int(body.get("pageToken", "0"))
        page = {"places": pages[idx]}
        if idx + 1 < len(pages):
            page["nextPageToken"] = str(idx + 1)
        return httpx.Response(200, json=page)

    return httpx.Client(transport=httpx.MockTransport(handler)), calls


def make_client(pages, limit=50):
    http, calls = fake_places(pages)
    guard = CostGuard(MemoryRepo(), {"places_text_search": ApiLimit(por_dia=limit, por_mes=900)})
    return PlacesClient("test-key", guard, http=http), calls, guard


def test_places_pagina_y_manda_field_mask():
    pages = [[api_place(f"p{i}", f"Negocio {i}") for i in range(20)], [api_place("p20", "Último")]]
    client, calls, guard = make_client(pages)
    places = list(client.search_text("corralón en San Miguel", lat=-34.5, lng=-58.7, radius_km=4))
    assert len(places) == 21
    assert len(calls) == 2
    assert calls[0].headers["X-Goog-FieldMask"] == FIELD_MASK
    assert json.loads(calls[1].content)["pageToken"] == "1"
    assert guard.session_calls["places_text_search"] == 2


def test_places_respeta_tope():
    pages = [[api_place("a", "A")], [api_place("b", "B")]]
    client, _, _ = make_client(pages, limit=1)
    with pytest.raises(BudgetExceeded):
        list(client.search_text("x", lat=0, lng=0, radius_km=1))


def test_hunt_filtra_deduplica_y_ordena(cfg):
    pages = [[
        api_place("ok1", "Corralón Los Andes", phone="+54 9 11 5555-4444", count=230, rating=4.6),
        api_place("ok2", "Materiales Pepe", phone="+54 11 4666-7777", website="https://pepe.com.ar", count=10),
        api_place("dup", "Los Andes Sucursal", phone="+54 9 11 5555-4444"),       # mismo teléfono
        api_place("closed", "Cerrado SA", status="CLOSED_PERMANENTLY"),
        api_place("far", "Corralón Lejano", lat=-34.9, lng=-58.4),               # fuera de zona
        api_place("ban", "No Molestar", phone="+54 9 11 4444-3333"),
        api_place("ig", "Corralón IG", phone="+54 9 11 3333-2222", website="https://instagram.com/corralonig"),
    ]]
    client, _, _ = make_client(pages)
    repo = MemoryRepo()
    repo.add_blacklist("phone", "+5491144443333")

    result = run_hunt(rubro=cfg.rubro("corralones"), zona=cfg.zona("San Miguel"), max_leads=60,
                      cfg=cfg, repo=repo, search=client.search_text)

    ids = [l.place.place_id for l in result.leads]
    assert set(ids) == {"ok1", "ok2", "ig"}
    assert ids[0] == "ok1"  # el de mayor score primero
    s = result.stats
    assert (s.duplicados, s.cerrados, s.lejos, s.blacklist) == (1, 1, 1, 1)
    ig = next(l for l in result.leads if l.place.place_id == "ig")
    assert ig.web_status == "social" and ig.instagram == "corralonig"


def test_hunt_no_repite_leads_ya_guardados(cfg):
    pages = [[api_place("ok1", "Corralón Los Andes", phone="+54 9 11 5555-4444")]]
    repo = MemoryRepo()
    for _ in range(2):
        client, _, _ = make_client(pages)
        result = run_hunt(rubro=cfg.rubro("corralones"), zona=cfg.zona("san-miguel"), max_leads=10,
                          cfg=cfg, repo=repo, search=client.search_text)
        repo.save_leads(result.leads)
    assert result.stats.nuevos == 0 and result.stats.duplicados == 1


def test_export_csv_sin_datos_google_por_defecto(cfg, tmp_path):
    client, _, _ = make_client([[api_place("ok1", "Corralón Los Andes", phone="+54 9 11 5555-4444")]])
    result = run_hunt(rubro=cfg.rubro("corralones"), zona=cfg.zona("san-miguel"), max_leads=10,
                      cfg=cfg, repo=MemoryRepo(), search=client.search_text)
    path = export_csv(result.leads, tmp_path / "a.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    assert rows[0]["place_id"] == "ok1" and "nombre" not in rows[0]
    path = export_csv(result.leads, tmp_path / "b.csv", include_google_data=True)
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    assert rows[0]["whatsapp"] == "5491155554444"
