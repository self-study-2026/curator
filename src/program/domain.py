from dataclasses import dataclass
from datetime import date
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


@dataclass
class RawEvent:
	category: EventCategory
	summary: str
	start: date
	spec_id: str | None = None


@dataclass
class Session:
	title: str
	spec_id: str | None


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
