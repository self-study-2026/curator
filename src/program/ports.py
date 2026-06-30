from collections.abc import Iterable
from typing import Protocol

from src.program.domain import RawEvent


class CalendarSource(Protocol):
	def events(self) -> Iterable[RawEvent]: ...
