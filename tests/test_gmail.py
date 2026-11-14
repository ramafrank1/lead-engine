import base64
import json
from email import message_from_bytes

import httpx
import pytest

from lead_engine.mail.gmail import GmailClient, GmailError, build_message


def test_build_message_headers():
    msg = build_message(
        sender_name="Ramiro Frank", sender_email="ramiro.web@gmail.com", to="info@corralon.com.ar",
        subject="Una idea para su web", body="Hola, ¿cómo están?", unsubscribe_url="https://x.pages.dev/baja?t=abc",
    )
    assert msg["From"] == "Ramiro Frank <ramiro.web@gmail.com>"
    assert msg["List-Unsubscribe"] == "<mailto:ramiro.web@gmail.com?subject=baja>, <https://x.pages.dev/baja?t=abc>"
    assert msg["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
    assert msg.get_content_type() == "text/plain"
    assert "¿cómo están?" in msg.get_content()


def test_build_message_followup_threads():
    msg = build_message(sender_name="R", sender_email="a@gmail.com", to="b@x.com", subject="Re: hola",
                        body="seguimiento", in_reply_to="<abc@gmail.com>")
    assert msg["In-Reply-To"] == msg["References"] == "<abc@gmail.com>"
    assert msg["List-Unsubscribe-Post"] is None


def _client(handler):
    return GmailClient("cid", "secret", "refresh", http=httpx.Client(transport=httpx.MockTransport(handler)))


def test_send_refreshes_token_and_posts_raw():
    calls = []

    def handler(request: httpx.Request):
        calls.append(request)
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        assert request.headers["Authorization"] == "Bearer tok"
        payload = json.loads(request.content)
        raw = message_from_bytes(base64.urlsafe_b64decode(payload["raw"]))
        assert raw["To"] == "b@x.com"
        assert payload["threadId"] == "t1"
        return httpx.Response(200, json={"id": "m1", "threadId": "t1"})

    gmail = _client(handler)
    msg = build_message(sender_name="R", sender_email="a@gmail.com", to="b@x.com", subject="s", body="b")
    assert gmail.send(msg, thread_id="t1") == {"id": "m1", "threadId": "t1"}
    gmail.send(msg, thread_id="t1")
    assert sum(c.url.host == "oauth2.googleapis.com" for c in calls) == 1  # el token se reutiliza


def test_expired_refresh_token_explains_fix():
    gmail = _client(lambda r: httpx.Response(400, json={"error": "invalid_grant"}))
    with pytest.raises(GmailError, match="7 días"):
        gmail.profile()


def test_missing_config():
    with pytest.raises(GmailError, match="gmail-auth"):
        GmailClient("", "", "")
