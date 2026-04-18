from __future__ import annotations

import pickle
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def _coerce_to_dict(obj: Any) -> dict[str, Any]:
    """Best-effort conversion of a deserialized HL7-related object into a plain dict."""
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, Mapping):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)

    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return dict(to_dict())

    model_dump = getattr(obj, "model_dump", None)
    if callable(model_dump):
        return dict(model_dump())

    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        return dict(vars(obj))

    msg = f"cannot represent cached HL7 object {type(obj).__name__!r} as a dict"
    raise TypeError(msg)


def load_cached_hl7_message(cache_path: str | Path) -> dict[str, Any]:
    """Load a pickle-serialized HL7 message object from disk and return it as a dict.

    The on-disk format is expected to be ``pickle`` bytes (e.g. written with
    ``pickle.dump``). The unpickled value is normalized for downstream parsers
    that expect a mapping.

    .. warning::

        Only load caches produced by trusted code; unpickling can execute arbitrary
        Python if the file was tampered with.
    """
    path = Path(cache_path)
    raw = path.read_bytes()
    obj = pickle.loads(raw)
    return _coerce_to_dict(obj)
