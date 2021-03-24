__all__ = [
    "ensure_nl",
]


def ensure_nl(s: str) -> str:
    return s.rstrip() + "\n"
