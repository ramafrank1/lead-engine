"""Normalización de teléfonos argentinos para WhatsApp (+549...)."""

from __future__ import annotations

from dataclasses import dataclass

import phonenumbers
from phonenumbers import PhoneNumberType


@dataclass(frozen=True)
class PhoneInfo:
    e164: str          # +5491155554444 / +541146667777
    is_mobile: bool
    wa_number: str | None  # 5491155554444 (formato wa.me), solo si es celular


def normalize_ar(raw: str | None) -> PhoneInfo | None:
    """Devuelve None si el número no es válido. Los fijos no tienen WhatsApp detectable."""
    if not raw:
        return None
    try:
        num = phonenumbers.parse(raw, "AR")
    except phonenumbers.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(num):
        return None
    e164 = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    kind = phonenumbers.number_type(num)
    is_mobile = kind in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE) and e164.startswith("+549")
    return PhoneInfo(e164=e164, is_mobile=is_mobile, wa_number=e164.lstrip("+") if is_mobile else None)
