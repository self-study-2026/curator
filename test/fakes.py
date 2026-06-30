from src.program.domain import RawEvent


class FakeCalendar:
	def __init__(self, *events: RawEvent) -> None:
		self._events = events

	def events(self) -> tuple[RawEvent, ...]:
		return self._events
