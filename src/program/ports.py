from collections.abc import Iterable
from typing import Protocol

from src.program.domain import RawEvent


class SpecSourceError(Exception):
	pass


class CalendarSource(Protocol):
	def events(self) -> Iterable[RawEvent]: ...


class SpecSource(Protocol):
	def get(self, spec_id: str) -> dict[str, str] | None: ...
