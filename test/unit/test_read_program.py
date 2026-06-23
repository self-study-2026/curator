from datetime import date, datetime

from src.program.domain import EventCategory, RawEvent
from src.program.use_cases import ProgramReader
from test.fakes import FakeCalendar, FakeSpecs

SESSION_A = RawEvent(
	category=EventCategory.SESSION,
	summary="M0: deploy the thing",
	start=datetime(2026, 6, 22, 19, 30),
	end=datetime(2026, 6, 22, 22, 0),
)
SESSION_B = RawEvent(
	category=EventCategory.SESSION,
	summary="Just reading, no spec ID",
	start=datetime(2026, 6, 23, 10, 0),
	end=datetime(2026, 6, 23, 11, 0),
)
MORNING = RawEvent(
	category=EventCategory.MORNING,
	summary="AM: Morning kata, 15m",
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
MILESTONE = RawEvent(
	category=EventCategory.MILESTONE,
	summary="Foundation done",
	start=date(2026, 7, 10),
	end=date(2026, 7, 11),
)
M0_SPEC: dict[str, str] = {
	"id": "M0",
	"file": "capstones/M0-launch.md",
	"title": "Capstone M0",
}


def test_session_time_and_budget() -> None:
	program = ProgramReader(FakeCalendar(SESSION_A), FakeSpecs()).read(
		date(2026, 6, 22)
	)
	assert len(program.sessions) == 1
	session = program.sessions[0]
	assert session.time == "19:30"
	assert session.time_budget == "2h30m"


def test_spec_join() -> None:
	program = ProgramReader(FakeCalendar(SESSION_A), FakeSpecs({"M0": M0_SPEC})).read(
		date(2026, 6, 22)
	)
	session = program.sessions[0]
	assert session.spec_id == "M0"
	assert session.spec_path == "capstones/M0-launch.md"


def test_unmatched_session_has_null_spec() -> None:
	program = ProgramReader(FakeCalendar(SESSION_B), FakeSpecs()).read(
		date(2026, 6, 23)
	)
	assert program.sessions[0].spec_id is None
	assert program.sessions[0].spec_path is None


def test_excludes_sessions_from_other_dates() -> None:
	program = ProgramReader(FakeCalendar(SESSION_A, SESSION_B), FakeSpecs()).read(
		date(2026, 6, 22)
	)
	assert all("Just reading" not in s.title for s in program.sessions)


def test_morning_habit_on_weekday() -> None:
	program = ProgramReader(FakeCalendar(MORNING), FakeSpecs()).read(date(2026, 6, 22))
	assert program.morning_habit is not None
	assert "kata" in program.morning_habit.lower()


def test_no_morning_habit_on_weekend() -> None:
	program = ProgramReader(FakeCalendar(MORNING), FakeSpecs()).read(date(2026, 6, 27))
	assert program.morning_habit is None


def test_current_phase() -> None:
	program = ProgramReader(FakeCalendar(PHASE), FakeSpecs()).read(date(2026, 6, 22))
	assert program.current_phase == "Foundation phase"


def test_next_milestone() -> None:
	program = ProgramReader(FakeCalendar(MILESTONE), FakeSpecs()).read(
		date(2026, 6, 22)
	)
	assert program.next_milestone is not None
	assert program.next_milestone.date == "2026-07-10"
	assert "Foundation done" in program.next_milestone.title


def test_program_date() -> None:
	program = ProgramReader(FakeCalendar(), FakeSpecs()).read(date(2026, 6, 22))
	assert program.date == "2026-06-22"


def test_empty_day_has_no_sessions() -> None:
	program = ProgramReader(
		FakeCalendar(SESSION_A, MORNING, PHASE, MILESTONE), FakeSpecs()
	).read(date(2099, 1, 1))
	assert program.sessions == []


def test_sub_hour_time_budget() -> None:
	session = RawEvent(
		category=EventCategory.SESSION,
		summary="Quick sync",
		start=datetime(2026, 6, 22, 9, 0),
		end=datetime(2026, 6, 22, 9, 45),
	)
	program = ProgramReader(FakeCalendar(session), FakeSpecs()).read(date(2026, 6, 22))
	assert program.sessions[0].time_budget == "45m"


def test_phase_not_active_on_end_date() -> None:
	program = ProgramReader(FakeCalendar(PHASE), FakeSpecs()).read(date(2026, 6, 29))
	assert program.current_phase is None


def test_phase_active_on_day_before_end() -> None:
	program = ProgramReader(FakeCalendar(PHASE), FakeSpecs()).read(date(2026, 6, 28))
	assert program.current_phase == "Foundation phase"


def test_nearest_of_multiple_future_milestones_selected() -> None:
	far = RawEvent(
		category=EventCategory.MILESTONE,
		summary="Far away",
		start=date(2026, 8, 1),
		end=date(2026, 8, 2),
	)
	program = ProgramReader(FakeCalendar(far, MILESTONE), FakeSpecs()).read(
		date(2026, 6, 22)
	)
	assert program.next_milestone is not None
	assert program.next_milestone.title == "Foundation done"


def test_milestone_on_target_date_not_surfaced() -> None:
	today = RawEvent(
		category=EventCategory.MILESTONE,
		summary="Shipped today",
		start=date(2026, 6, 22),
		end=date(2026, 6, 23),
	)
	program = ProgramReader(FakeCalendar(today), FakeSpecs()).read(date(2026, 6, 22))
	assert program.next_milestone is None


def test_morning_habit_on_rrule_until_date() -> None:
	morning = RawEvent(
		category=EventCategory.MORNING,
		summary="AM: kata",
		start=datetime(2026, 6, 22, 7, 0),
		end=datetime(2026, 6, 22, 7, 15),
		rrule_until=date(2026, 6, 22),
	)
	program = ProgramReader(FakeCalendar(morning), FakeSpecs()).read(date(2026, 6, 22))
	assert program.morning_habit is not None
