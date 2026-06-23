from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class EventCategory(Enum):
	SESSION = "SESSION"
	MORNING = "MORNING"
	PHASE = "PHASE"
	MILESTONE = "MILESTONE"
	BREAK = "BREAK"
	UNKNOWN = "UNKNOWN"

	@classmethod
	def from_str(cls, value: str) -> "EventCategory":
		try:
			return cls(value.upper())
		except ValueError:
			return cls.UNKNOWN


def to_date(dt: datetime | date) -> date:
	return dt.date() if isinstance(dt, datetime) else dt


@dataclass
class RawEvent:
	category: EventCategory
	summary: str
	start: datetime | date
	end: datetime | date | None
	rrule_until: date | None = None


@dataclass
class Session:
	time: str
	title: str
	spec_id: str | None
	spec_path: str | None
	time_budget: str | None


@dataclass
class Milestone:
	date: str
	title: str


@dataclass
class Program:
	date: str
	sessions: list[Session]
	morning_habit: str | None
	next_milestone: Milestone | None
	current_phase: str | None
	plan_error: str | None = None
