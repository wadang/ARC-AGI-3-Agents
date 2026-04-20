import json
import logging
import os
import re
from typing import Any, Iterable

from openai import OpenAI

_IMAGE_DATA_URL_RE = re.compile(
    r"data:(image/[-+.a-zA-Z0-9]+);base64,([A-Za-z0-9+/=\r\n]+)"
)


def _first_env(names: Iterable[str], default: str = "") -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


def get_openai_base_url() -> str | None:
    return os.environ.get("OPENAI_BASE_URL") or os.environ.get("openai_base_url")


def create_openai_client(
    api_key_env_vars: tuple[str, ...] = ("OPENAI_API_KEY",),
) -> OpenAI:
    client_kwargs: dict[str, Any] = {
        "api_key": _first_env(api_key_env_vars),
    }
    base_url = get_openai_base_url()
    if base_url:
        client_kwargs["base_url"] = base_url
    return OpenAI(**client_kwargs)


def sanitize_for_logging(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        value = value.model_dump()

    if isinstance(value, dict):
        return {key: sanitize_for_logging(val) for key, val in value.items()}
    if isinstance(value, list):
        return [sanitize_for_logging(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_logging(item) for item in value]
    if isinstance(value, str):
        return _IMAGE_DATA_URL_RE.sub(_replace_image_data_url, value)
    return value


def dump_for_logging(value: Any) -> str:
    return json.dumps(
        sanitize_for_logging(value),
        ensure_ascii=False,
        indent=2,
        default=str,
    )


def log_openai_request(logger: logging.Logger, label: str, payload: Any) -> None:
    logger.info("%s request:\n%s", label, dump_for_logging(payload))


def log_openai_response(logger: logging.Logger, label: str, payload: Any) -> None:
    logger.info("%s response:\n%s", label, dump_for_logging(payload))


def _replace_image_data_url(match: re.Match[str]) -> str:
    mime_type = match.group(1)
    payload = match.group(2).replace("\n", "").replace("\r", "")
    return f"data:{mime_type};base64,<omitted {len(payload)} chars>"
