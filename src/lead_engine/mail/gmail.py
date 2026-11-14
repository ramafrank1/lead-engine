"""Gmail por API con OAuth de usuario: autorización única, armado de mensajes y envío.

Se usa el scope `gmail.modify` (leer, etiquetar, crear borradores y enviar; nunca borra para siempre).
El refresh token vive en `.env` (local) o en los secrets de GitHub Actions, nunca en el código.
"""

from __future__ import annotations

import base64
import time
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

import httpx

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_URL = "https://oauth2.googleapis.com/token"
API_URL = "https://gmail.googleapis.com/gmail/v1/users/me"


class GmailError(RuntimeError):
    pass


def run_auth_flow(client_id: str, client_secret: str) -> str:
    """Abre el navegador para autorizar la cuenta y devuelve el refresh token."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not client_id or not client_secret:
        raise GmailError("Faltan GMAIL_CLIENT_ID y GMAIL_CLIENT_SECRET en .env (ver docs/email/fase-2-gmail-google-cloud.md).")
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": TOKEN_URL,
                "redirect_uris": ["http://localhost"],
            }
        },
        SCOPES,
    )
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline", open_browser=True)
    if not creds.refresh_token:
        raise GmailError("Google no devolvió refresh token. Revocá el acceso en myaccount.google.com/permissions y repetí.")
    return creds.refresh_token


def build_message(
    *,
    sender_name: str,
    sender_email: str,
    to: str,
    subject: str,
    body: str,
    unsubscribe_url: str | None = None,
    in_reply_to: str | None = None,
) -> EmailMessage:
    """Email en texto plano con List-Unsubscribe; `in_reply_to` encadena los seguimientos en el mismo hilo."""
    msg = EmailMessage()
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=sender_email.split("@")[-1])
    unsubscribe = [f"<mailto:{sender_email}?subject=baja>"]
    if unsubscribe_url:
        unsubscribe.append(f"<{unsubscribe_url}>")
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg["List-Unsubscribe"] = ", ".join(unsubscribe)
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to
    msg.set_content(body, charset="utf-8")
    return msg


class GmailClient:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, http: httpx.Client | None = None):
        if not (client_id and client_secret and refresh_token):
            raise GmailError("Gmail no está configurado: corré `lead gmail-auth` (ver docs/email/fase-2-gmail-google-cloud.md).")
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._http = http or httpx.Client(timeout=30)
        self._access_token: str | None = None
        self._expires_at = 0.0

    def _token(self) -> str:
        if self._access_token and time.time() < self._expires_at - 60:
            return self._access_token
        r = self._http.post(
            TOKEN_URL,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if r.status_code != 200:
            raise GmailError(
                f"No se pudo renovar el acceso a Gmail ({r.status_code}). Si la app de Google Cloud sigue en "
                "'Prueba', el token vence a los 7 días: publicala ('En producción') y corré `lead gmail-auth` de nuevo."
            )
        data = r.json()
        self._access_token = data["access_token"]
        self._expires_at = time.time() + int(data.get("expires_in", 3600))
        return self._access_token

    def _request(self, method: str, path: str, **kwargs) -> dict:
        r = self._http.request(method, f"{API_URL}{path}", headers={"Authorization": f"Bearer {self._token()}"}, **kwargs)
        if r.status_code >= 400:
            raise GmailError(f"Gmail API {method} {path}: {r.status_code} {r.text[:300]}")
        return r.json()

    def profile(self) -> dict:
        """Email de la cuenta y totales de mensajes/hilos."""
        return self._request("GET", "/profile")

    def send(self, msg: EmailMessage, thread_id: str | None = None) -> dict:
        """Envía y devuelve {id, threadId}."""
        payload: dict = {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}
        if thread_id:
            payload["threadId"] = thread_id
        return self._request("POST", "/messages/send", json=payload)
