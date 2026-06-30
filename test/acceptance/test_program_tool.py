"""
Acceptance tests for the read_program tool.
Each test corresponds to one acceptance criterion.
"""

import json
from datetime import date
from pathlib import Path

import src.tools.read_program as adapter_module
from src.program.domain import EventCategory, RawEvent
from src.program.use_cases import ProgramReader
from src.tools.read_program import read_program
from test.fakes import FakeCalendar

# ── shared fixtures ───────────────────────────────────────────────────────────

SESSION_8AM = RawEvent(
	category=EventCategory.SESSION,
	summary="CF1: feeds CLI work",
	start=date(2026, 6, 22),
	spec_id="CF1-feed-management",
)
SESSION_2PM = RawEvent(
	category=EventCategory.SESSION,
	summary="Just reading, no spec",
	start=date(2026, 6, 22),
)
SESSION_7PM = RawEvent(
	category=EventCategory.SESSION,
	summary="M0: deploy the thing",
	start=date(2026, 6, 22),
	spec_id="M0-curator-v0",
)
MORNING = RawEvent(
	category=EventCategory.MORNING,
	summary="AM: kata",
	start=date(2026, 6, 22),
)
PAST_MILESTONE = RawEvent(
	category=EventCategory.MILESTONE,
	summary="Already shipped",
	start=date(2026, 6, 1),
)
FUTURE_MILESTONE = RawEvent(
	category=EventCategory.MILESTONE,
	summary="Foundation done",
	start=date(2026, 7, 10),
)
MINIMAL_SCHEDULE = {
	"schedule": {
		"2026-06-22": [
			{
				"uid": "s0@test",
				"title": "M0: deploy",
				"type": "build",
				"spec_id": "M0-curator-v0",
				"code": "M0",
				"category": "SESSION",
			}
		]
	}
}

# ── acceptance tests ──────────────────────────────────────────────────────────


def test_three_sessions_with_spec_id() -> None:
	"""Sessions are collected for the target date and spec_id is propagated
	directly from the schedule data."""
	program = ProgramReader(
		FakeCalendar(SESSION_7PM, SESSION_2PM, SESSION_8AM),
	).read(date(2026, 6, 22))

	assert len(program.sessions) == 3
	titles = [s.title for s in program.sessions]
	assert "CF1: feeds CLI work" in titles
	assert "Just reading, no spec" in titles
	assert "M0: deploy the thing" in titles

	cf1 = next(s for s in program.sessions if s.spec_id == "CF1-feed-management")
	assert cf1.spec_id == "CF1-feed-management"

	reading = next(s for s in program.sessions if s.spec_id is None)
	assert reading.spec_id is None

	m0 = next(s for s in program.sessions if s.spec_id == "M0-curator-v0")
	assert m0.spec_id == "M0-curator-v0"


def test_break_day_returns_empty_sessions() -> None:
	"""A date with no sessions returns an empty sessions list."""
	program = ProgramReader(
		FakeCalendar(SESSION_7PM, FUTURE_MILESTONE),
	).read(date(2026, 11, 27))

	assert program.sessions == []


def test_read_program_end_to_end(tmp_path: Path) -> None:
	"""read_program() wires the schedule source end-to-end and returns a
	Program with sessions parsed from the JSON file."""
	schedule_file = tmp_path / "schedule.json"
	schedule_file.write_text(json.dumps(MINIMAL_SCHEDULE))
	original = adapter_module.SCHEDULE_PATH
	adapter_module.SCHEDULE_PATH = schedule_file
	try:
		program = read_program(date(2026, 6, 22))
	finally:
		adapter_module.SCHEDULE_PATH = original

	assert len(program.sessions) == 1
	assert program.sessions[0].spec_id == "M0-curator-v0"


def test_next_milestone_is_never_past() -> None:
	"""next_milestone is the nearest *future* milestone; past milestones are
	never surfaced regardless of how close they are to the target date."""
	program = ProgramReader(
		FakeCalendar(PAST_MILESTONE, FUTURE_MILESTONE),
	).read(date(2026, 6, 22))

	assert program.next_milestone is not None
	assert program.next_milestone.title == "Foundation done"
	assert program.next_milestone.date == "2026-07-10"
