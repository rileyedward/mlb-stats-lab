"""Custom exceptions for the data layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    """A possible match when resolving a player name."""

    id: int
    first: str
    last: str
    debut_year: int | None
    last_year: int | None


class AmbiguousPlayerError(Exception):
    """Multiple players matched the given name."""

    def __init__(self, name: str, candidates: list[Candidate]):
        self.name = name
        self.candidates = candidates
        lines = [f"Multiple players match {name!r}:"]
        for c in candidates:
            span = f"{c.debut_year or '?'}–{c.last_year or '?'}"
            lines.append(f"  - {c.first} {c.last} (id={c.id}, {span})")
        super().__init__("\n".join(lines))


class UnknownPlayerError(Exception):
    """No player matched the given name."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"No player found for {name!r}.")


class UnknownTeamError(Exception):
    """Team value could not be normalized to a known abbreviation."""

    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Unknown team {value!r}.")
