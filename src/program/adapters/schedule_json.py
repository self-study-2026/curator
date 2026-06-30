import json
from collections.abc import Iterable
from datetime import date
from pathlib import Path

from src.program.domain import EventCategory, RawEvent


class JsonScheduleSource:
	def __init__(self, path: Path) -> None:
		self._path = path

	def events(self) -> Iterable[RawEvent]:
		data = json.loads(self._path.read_text())
		for date_str in sorted(data["schedule"]):
			event_date = date.fromisoformat(date_str)
			for item in data["schedule"][date_str]:
				yield RawEvent(
					category=EventCategory.from_str(item["category"]),
					summary=item["title"],
					start=event_date,
					spec_id=item.get("spec_id"),
				)
