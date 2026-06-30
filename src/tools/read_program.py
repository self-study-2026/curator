from datetime import date
from pathlib import Path

from pydantic import BaseModel, field_validator

from src.program.adapters.schedule_json import JsonScheduleSource
from src.program.domain import Program
from src.program.use_cases import ProgramReader

SCHEDULE_PATH = Path(__file__).parents[2] / "resources" / "schedule.json"


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
	milestone.
	"""
	return read_program(_parse_date(inp.date))


def read_program(target_date: date) -> Program:
	return ProgramReader(JsonScheduleSource(SCHEDULE_PATH)).read(target_date)
