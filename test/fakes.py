from src.program.domain import RawEvent


class FakeCalendar:
	def __init__(self, *events: RawEvent) -> None:
		self._events = events

	def events(self) -> tuple[RawEvent, ...]:
		return self._events


class FakeSpecs:
	def __init__(self, index: dict[str, dict[str, str]] | None = None) -> None:
		self._index = index or {}

	def get(self, spec_id: str) -> dict[str, str] | None:
		return self._index.get(spec_id)
