"""
Acceptance tests for the read_program tool.
Each test corresponds to one acceptance criterion and may be red until the
implementation catches up — that is intentional.
"""

from datetime import date, datetime
from pathlib import Path

import pytest

import src.tools.read_program as adapter_module
from src.program.domain import EventCategory, RawEvent
from src.program.use_cases import ProgramReader
from src.tools.read_program import read_program
from test.fakes import FakeCalendar, FakeSpecs

# ── shared fixtures ───────────────────────────────────────────────────────────

SPEC_INDEX: dict[str, dict[str, str]] = {
	"M0": {"id": "M0", "file": "capstones/M0-launch.md", "title": "Capstone M0"},
	"CF1": {"id": "CF1", "file": "curator/CF1-feeds.md", "title": "CF1"},
}

# Three sessions on the same day, intentionally supplied out of time order
SESSION_8AM = RawEvent(
	category=EventCategory.SESSION,
	summary="CF1: feeds CLI work",
	start=datetime(2026, 6, 22, 8, 0),
	end=datetime(2026, 6, 22, 9, 0),
)
SESSION_2PM = RawEvent(
	category=EventCategory.SESSION,
	summary="Just reading, no spec id",
	start=datetime(2026, 6, 22, 14, 0),
	end=datetime(2026, 6, 22, 15, 0),
)
SESSION_7PM = RawEvent(
	category=EventCategory.SESSION,
	summary="M0: deploy the thing",
	start=datetime(2026, 6, 22, 19, 30),
	end=datetime(2026, 6, 22, 22, 0),
)

MORNING = RawEvent(
	category=EventCategory.MORNING,
	summary="AM: kata",
	start=datetime(2026, 6, 22, 7, 0),
	end=datetime(2026, 6, 22, 7, 15),
	rrule_until=date(2026, 6, 26),
)
PHASE = RawEvent(
	category=EventCategory.PHASE,
	summary="Foundation phase",
	start=date(2026, 6, 22),
	end=date(2026, 6, 29),
)
PAST_MILESTONE = RawEvent(
	category=EventCategory.MILESTONE,
	summary="Already shipped",
	start=date(2026, 6, 1),
	end=date(2026, 6, 2),
)
FUTURE_MILESTONE = RawEvent(
	category=EventCategory.MILESTONE,
	summary="Foundation done",
	start=date(2026, 7, 10),
	end=date(2026, 7, 11),
)

MINIMAL_ICS = b"""\
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20260622T193000
DTEND:20260622T220000
SUMMARY:M0: deploy
CATEGORIES:SESSION
END:VEVENT
END:VCALENDAR
"""

# ── acceptance tests ──────────────────────────────────────────────────────────


def test_three_sessions_in_time_order_with_spec_join() -> None:
	"""Sessions come back sorted by time regardless of calendar iteration order,
	and titles carrying a known spec id are joined to their path and budget."""
	program = ProgramReader(
		FakeCalendar(SESSION_7PM, SESSION_2PM, SESSION_8AM),  # reverse order
		FakeSpecs(SPEC_INDEX),
	).read(date(2026, 6, 22))

	assert len(program.sessions) == 3
	assert [s.time for s in program.sessions] == ["08:00", "14:00", "19:30"]

	cf1, reading, m0 = program.sessions
	assert cf1.spec_id == "CF1"
	assert cf1.spec_path == "curator/CF1-feeds.md"
	assert cf1.time_budget == "1h"

	assert reading.spec_id is None

	assert m0.spec_id == "M0"
	assert m0.time_budget == "2h30m"


def test_break_day_returns_empty_plan() -> None:
	"""A date marked BREAK (or any day with no sessions) returns an empty
	sessions list and no morning habit — the digest renders 'rest day'."""
	break_event = RawEvent(
		category=EventCategory.BREAK,
		summary="Thanksgiving",
		start=date(2026, 11, 26),
		end=date(2026, 11, 28),
	)
	program = ProgramReader(
		FakeCalendar(SESSION_7PM, MORNING, break_event, FUTURE_MILESTONE),
		FakeSpecs(),
	).read(date(2026, 11, 27))  # Thursday inside the break window

	assert program.sessions == []
	assert program.morning_habit is None


def test_missing_spec_sidecar_returns_structured_error(
	tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
	"""When syllabus.json is absent the tool still returns a Program with
	the calendar sessions intact; plan_error is set so the digest can render
	a visible 'plan unavailable' note instead of crashing."""
	ics = tmp_path / "calendar.ics"
	ics.write_bytes(MINIMAL_ICS)
	monkeypatch.setattr(adapter_module, "CALENDAR_PATH", ics)
	monkeypatch.setattr(adapter_module, "SYLLABUS_PATH", tmp_path / "missing.json")

	program = read_program(date(2026, 6, 22))

	assert len(program.sessions) == 1  # calendar still parsed
	assert program.plan_error is not None  # structured error, not an exception


def test_next_milestone_is_never_past() -> None:
	"""next_milestone is the nearest *future* milestone; past milestones are
	never surfaced regardless of how close they are to the target date."""
	program = ProgramReader(
		FakeCalendar(PAST_MILESTONE, FUTURE_MILESTONE),
		FakeSpecs(),
	).read(date(2026, 6, 22))

	assert program.next_milestone is not None
	assert program.next_milestone.title == "Foundation done"
	assert program.next_milestone.date == "2026-07-10"
