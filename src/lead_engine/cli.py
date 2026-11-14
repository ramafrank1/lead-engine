"""CLI `lead`. Correr `lead --help` para ver todos los comandos."""

from __future__ import annotations

import os
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table

from lead_engine.core.config import DATA_DIR, OUT_DIR, ROOT, get_settings, load_business_config
from lead_engine.core.cost_guard import BudgetExceeded, CostGuard
from lead_engine.core.phone import normalize_ar
from lead_engine.db.repo import open_repo
from lead_engine.hunt.export import export_csv
from lead_engine.hunt.places import PlacesClient, PlacesError
from lead_engine.hunt.service import run_hunt
from lead_engine.hunt.web import classify_website
from lead_engine.mail.gmail import GmailClient, GmailError, build_message, run_auth_flow

app = typer.Typer(help="Lead Engine: captación de clientes para tu negocio web.", no_args_is_help=True)
console = Console()


def _repo():
    settings = get_settings()
    repo = open_repo(settings.database_url, DATA_DIR / "usage.json")
    if not repo.persistent:
        console.print("[yellow]Modo prueba: no hay DATABASE_URL, no se guarda nada en la base.[/]")
    return repo


@app.command()
def hunt(
    rubro: str = typer.Option(..., help="Rubro (ej: corralones, 'concesionarias')"),
    zona: str = typer.Option(..., help="Zona (ej: 'San Miguel', bella-vista)"),
    max: int = typer.Option(60, "--max", help="Cantidad máxima de leads nuevos"),
    csv_google: bool = typer.Option(
        False, "--csv-con-datos-google", help="Incluir nombre/teléfono/web en el CSV (ver README: términos de Google)"
    ),
    mostrar: int = typer.Option(15, help="Cuántos mostrar en la tabla"),
):
    """Busca negocios en Google Maps (API oficial), los puntúa y los guarda."""
    settings = get_settings()
    cfg = load_business_config()
    try:
        r, z = cfg.rubro(rubro), cfg.zona(zona)
    except KeyError as e:
        console.print(f"[red]{e.args[0]}[/]")
        raise typer.Exit(1)

    repo = _repo()
    guard = CostGuard(repo, cfg.limits.apis)
    try:
        client = PlacesClient(settings.google_api_key, guard)
        result = run_hunt(rubro=r, zona=z, max_leads=max, cfg=cfg, repo=repo, search=client.search_text)
    except (PlacesError, BudgetExceeded) as e:
        console.print(f"[red]{e}[/]")
        raise typer.Exit(1)

    saved = repo.save_leads(result.leads)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    csv_path = export_csv(result.leads, OUT_DIR / f"hunt-{r.key}-{z.key}-{stamp}.csv", include_google_data=csv_google)

    table = Table(title=f"{r.label} — {z.label}", caption="Datos: Google Maps")
    for col in ("Score", "Negocio", "Motivo", "WhatsApp"):
        table.add_column(col)
    for lead in result.leads[:mostrar]:
        table.add_row(str(lead.score), lead.place.name, lead.score_reason, lead.wa_phone or "—")
    console.print(table)

    s = result.stats
    console.print(
        f"Vistos: {s.vistos} · nuevos: [bold green]{s.nuevos}[/] · duplicados: {s.duplicados} · "
        f"cerrados: {s.cerrados} · fuera de zona: {s.lejos} · blacklist: {s.blacklist}"
    )
    console.print(f"Guardados en la base: {saved if repo.persistent else 0} · CSV: {csv_path}")
    for api, u in guard.summary().items():
        lim = cfg.limits.apis[api]
        console.print(f"Consumo {api}: {u['esta_corrida']} llamadas (hoy {u['hoy']}/{lim.por_dia}, mes {u['mes']}/{lim.por_mes})")


@app.command()
def opciones():
    """Lista rubros y zonas configurados."""
    cfg = load_business_config()
    console.print("[bold]Rubros:[/] " + ", ".join(f"{k} ({v.label})" for k, v in cfg.rubros.items()))
    console.print("[bold]Zonas:[/] " + ", ".join(f"{k} ({v.label})" for k, v in cfg.zonas.items()))


@app.command("blacklist")
def blacklist_add(
    valor: str = typer.Argument(..., help="Teléfono, dominio o place_id"),
    motivo: str = typer.Option("pidió no ser contactado", help="Motivo"),
):
    """Agrega un opt-out permanente (teléfono, dominio o place_id)."""
    repo = _repo()
    phone = normalize_ar(valor)
    if phone:
        kind, value = "phone", phone.e164
    elif "." in valor:
        kind, value = "domain", classify_website(valor).domain or valor.lower()
    else:
        kind, value = "place_id", valor
    repo.add_blacklist(kind, value, motivo)
    console.print(f"[green]Bloqueado para siempre:[/] {kind} = {value}")


@app.command("purge-cache")
def purge_cache():
    """Borra la copia temporal de datos de Google más vieja que PLACES_CACHE_DAYS."""
    settings = get_settings()
    n = _repo().purge_place_cache(settings.places_cache_days)
    console.print(f"Borrados {n} registros de place_cache (> {settings.places_cache_days} días).")


# Cuentas que nunca se usan para enviar en frío: si se queman, se pierde el email personal.
CUENTAS_PROTEGIDAS = {c.strip().lower() for c in os.environ.get("CUENTAS_PROTEGIDAS", "").split(",") if c.strip()}


def _set_env_value(key: str, value: str) -> None:
    """Escribe o reemplaza `KEY=valor` en .env sin mostrar el valor en pantalla."""
    path = ROOT / ".env"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _gmail() -> GmailClient:
    s = get_settings()
    return GmailClient(s.gmail_client_id, s.gmail_client_secret, s.gmail_refresh_token)


@app.command("gmail-auth")
def gmail_auth():
    """Autoriza la cuenta de Gmail de envío (una sola vez) y guarda el token en .env."""
    s = get_settings()
    console.print("Se abre el navegador. Entrá con la [bold]cuenta de Gmail NUEVA[/] (no la personal).")
    try:
        token = run_auth_flow(s.gmail_client_id, s.gmail_client_secret)
        email = GmailClient(s.gmail_client_id, s.gmail_client_secret, token).profile()["emailAddress"]
    except GmailError as e:
        console.print(f"[red]{e}[/]")
        raise typer.Exit(1)
    if email.lower() in CUENTAS_PROTEGIDAS:
        console.print(f"[red]{email} es tu cuenta personal: no se usa para enviar. Repetí con la cuenta nueva.[/]")
        raise typer.Exit(1)
    _set_env_value("GMAIL_REFRESH_TOKEN", token)
    console.print(f"[green]Listo:[/] {email} autorizada. El token quedó en .env (GMAIL_REFRESH_TOKEN).")
    console.print("Para GitHub Actions: copiá ese mismo valor como secret GMAIL_REFRESH_TOKEN del repo.")


@app.command("gmail-check")
def gmail_check(
    enviar_prueba: str = typer.Option(None, "--enviar-prueba", help="Manda un email de prueba a esta dirección (una tuya)"),
):
    """Verifica que Gmail esté conectado y, opcionalmente, manda un email de prueba."""
    s = get_settings()
    try:
        gmail = _gmail()
        prof = gmail.profile()
    except GmailError as e:
        console.print(f"[red]{e}[/]")
        raise typer.Exit(1)
    email = prof["emailAddress"]
    console.print(f"[green]Conectado:[/] {email} · mensajes: {prof.get('messagesTotal', 0)} · hilos: {prof.get('threadsTotal', 0)}")
    if email.lower() in CUENTAS_PROTEGIDAS:
        console.print("[red]Ojo: es tu cuenta personal. No se va a usar para enviar en frío.[/]")
        raise typer.Exit(1)
    faltan = [k for k, v in {"OWNER_WHATSAPP": s.owner_whatsapp, "OWNER_POSTAL_ADDRESS": s.owner_postal_address}.items() if not v]
    if faltan:
        console.print(f"[yellow]Para la firma faltan en .env: {', '.join(faltan)}[/]")
    if enviar_prueba:
        firma = "\n".join(x for x in (s.owner_name, "Páginas web y sistemas a medida", s.owner_portfolio,
                                      f"WhatsApp {s.owner_whatsapp}" if s.owner_whatsapp else "", s.owner_postal_address) if x)
        msg = build_message(
            sender_name=s.owner_name, sender_email=email, to=enviar_prueba, subject="Prueba de Lead Engine",
            body=f"Hola,\n\nEsto es una prueba de envío por la API de Gmail.\n\n--\n{firma}\n\n"
                 "Si no querés recibir más emails, respondé \"no\" y no te escribo más.",
        )
        try:
            sent = gmail.send(msg)
        except GmailError as e:
            console.print(f"[red]{e}[/]")
            raise typer.Exit(1)
        console.print(f"[green]Enviado[/] a {enviar_prueba} (id {sent['id']}). Revisá si llegó a Recibidos o a Spam.")


if __name__ == "__main__":
    app()
