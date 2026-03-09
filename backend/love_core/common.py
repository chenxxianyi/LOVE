from __future__ import annotations

import hashlib
import os
import random
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict

from pydantic import BaseModel

DT_FMT = "%Y-%m-%d %H:%M:%S"
DATE_FMT = "%Y-%m-%d"
PASSWORD_SALT = os.getenv("LOVE_PASSWORD_SALT", "love-p0-salt")


def now_dt() -> datetime:
    return datetime.now()


def now_str() -> str:
    return now_dt().strftime(DT_FMT)


def plus_str(**kwargs: Any) -> str:
    return (now_dt() + timedelta(**kwargs)).strftime(DT_FMT)


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, DT_FMT)


def to_date(value: str) -> datetime.date:
    return datetime.strptime(value, DATE_FMT).date()


def hash_password(raw: str) -> str:
    return hashlib.sha256(f"{PASSWORD_SALT}:{raw}".encode("utf-8")).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def generate_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def random_size_bytes() -> int:
    return random.randint(1_400_000, 28_000_000)


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()  # type: ignore[attr-defined]
    return model.dict()  # type: ignore[attr-defined]
