from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

from icalendar import Calendar

from src.program.domain import EventCategory, RawEvent, to_date


def _get_category(component: Any) -> EventCategory:
	cats = component.get("categories")
	if cats is None:
		return EventCategory.UNKNOWN
	if hasattr(cats, "__iter__") and not isinstance(cats, str | bytes):
		raw = next(iter(cats), "")
	else:
		raw = cats
	return EventCategory.from_str(str(raw))


class IcsCalendarSource:
	def __init__(self, path: Path) -> None:
		self._path = path

	def events(self) -> Iterable[RawEvent]:
		with self._path.open("rb") as f:
			cal = Calendar.from_ical(f.read())

		for component in cal.walk():
			if component.name != "VEVENT":
				continue
			dtstart = component.get("dtstart")
			if not dtstart:
				continue
			dtend = component.get("dtend")

			rrule_until: date | None = None
			rrule = component.get("rrule")
			if rrule:
				until_list = rrule.get("UNTIL", [])
				if until_list:
					rrule_until = to_date(until_list[0])

			yield RawEvent(
				category=_get_category(component),
				summary=str(component.get("summary", "")),
				start=dtstart.dt,
				end=dtend.dt if dtend else None,
				rrule_until=rrule_until,
			)
