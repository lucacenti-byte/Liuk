from __future__ import annotations


def strip_prefix(
    raw: str,
    *,
    strip_through_dash: bool = True,
    require_dash: bool = True,
) -> str | None:
    """
    Rimuove tutto fino al primo '-' (incluso) e restituisce il resto.
    None = lasciare passare la lettura invariata.
    """
    raw = raw.strip()
    if not raw:
        return None

    if strip_through_dash:
        if "-" not in raw:
            return None if require_dash else raw
        return raw.split("-", 1)[1]

    if len(raw) <= 7:
        return None if require_dash else raw
    return raw[7:]
