from datetime import date
from pathlib import Path

from pydantic import BaseModel, field_validator

from src.program.adapters.ics_calendar import IcsCalendarSource
from src.program.adapters.json_spec import JsonSpecSource
from src.program.domain import Program
from src.program.use_cases import ProgramReader

CALENDAR_PATH = Path(__file__).parents[2] / "resources" / "calendar.ics"
SYLLABUS_PATH = Path(__file__).parents[2] / "resources" / "syllabus.json"


def _parse_date(s: str) -> date:
	if s == "today":
		return date.today()
	return date.fromisoformat(s)


class ReadProgramInput(BaseModel):
	date: str

	@field_validator("date")
	@classmethod
	def validate_date(cls, v: str) -> str:
		_parse_date(v)
		return v


def handle_read_program(inp: ReadProgramInput) -> Program:
	"""Return the study program for a given date.

	Use this when the user asks what they are studying or what is on their
	schedule. Pass date="today" for the current day or date="YYYY-MM-DD" for
	a specific date. Returns sessions, morning habit, current phase, and next
	milestone. If the spec sidecar is missing, sessions are still returned and
	plan_error is set.
	"""
	return read_program(_parse_date(inp.date))


def read_program(target_date: date) -> Program:
	return ProgramReader(
		IcsCalendarSource(CALENDAR_PATH),
		JsonSpecSource(SYLLABUS_PATH),
	).read(target_date)
