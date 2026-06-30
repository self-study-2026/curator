from datetime import date

from src.program.domain import EventCategory, RawEvent
from src.program.use_cases import ProgramReader
from test.fakes import FakeCalendar

SESSION_A = RawEvent(
	category=EventCategory.SESSION,
	summary="M0: deploy the thing",
	start=date(2026, 6, 22),
	spec_id="M0-curator-v0",
)
SESSION_B = RawEvent(
	category=EventCategory.SESSION,
	summary="Just reading, no spec",
	start=date(2026, 6, 23),
)
MORNING = RawEvent(
	category=EventCategory.MORNING,
	summary="AM: Morning kata, 15m",
	start=date(2026, 6, 22),
)
PHASE = RawEvent(
	category=EventCategory.PHASE,
	summary="Foundation phase",
	start=date(2026, 6, 22),
)
MILESTONE = RawEvent(
	category=EventCategory.MILESTONE,
	summary="Foundation done",
	start=date(2026, 7, 10),
)


def test_session_title_and_spec_id() -> None:
	program = ProgramReader(FakeCalendar(SESSION_A)).read(date(2026, 6, 22))
	assert len(program.sessions) == 1
	assert program.sessions[0].title == "M0: deploy the thing"
	assert program.sessions[0].spec_id == "M0-curator-v0"


def test_null_spec_id_session() -> None:
	program = ProgramReader(FakeCalendar(SESSION_B)).read(date(2026, 6, 23))
	assert program.sessions[0].spec_id is None


def test_excludes_sessions_from_other_dates() -> None:
	program = ProgramReader(FakeCalendar(SESSION_A, SESSION_B)).read(date(2026, 6, 22))
	assert all("Just reading" not in s.title for s in program.sessions)


def test_morning_habit_on_weekday() -> None:
	program = ProgramReader(FakeCalendar(MORNING)).read(date(2026, 6, 22))
	assert program.morning_habit is not None
	assert "kata" in program.morning_habit.lower()


def test_no_morning_habit_on_weekend() -> None:
	program = ProgramReader(FakeCalendar(MORNING)).read(date(2026, 6, 27))
	assert program.morning_habit is None


def test_current_phase() -> None:
	program = ProgramReader(FakeCalendar(PHASE)).read(date(2026, 6, 22))
	assert program.current_phase == "Foundation phase"


def test_phase_active_after_start() -> None:
	program = ProgramReader(FakeCalendar(PHASE)).read(date(2026, 7, 1))
	assert program.current_phase == "Foundation phase"


def test_most_recent_phase_wins() -> None:
	earlier = RawEvent(
		category=EventCategory.PHASE,
		summary="Foundation phase",
		start=date(2026, 6, 1),
	)
	later = RawEvent(
		category=EventCategory.PHASE,
		summary="Build phase",
		start=date(2026, 6, 20),
	)
	program = ProgramReader(FakeCalendar(earlier, later)).read(date(2026, 6, 22))
	assert program.current_phase == "Build phase"


def test_next_milestone() -> None:
	program = ProgramReader(FakeCalendar(MILESTONE)).read(date(2026, 6, 22))
	assert program.next_milestone is not None
	assert program.next_milestone.date == "2026-07-10"
	assert "Foundation done" in program.next_milestone.title


def test_program_date() -> None:
	program = ProgramReader(FakeCalendar()).read(date(2026, 6, 22))
	assert program.date == "2026-06-22"


def test_empty_day_has_no_sessions() -> None:
	program = ProgramReader(FakeCalendar(SESSION_A, MORNING, PHASE, MILESTONE)).read(
		date(2099, 1, 1)
	)
	assert program.sessions == []


def test_nearest_of_multiple_future_milestones_selected() -> None:
	far = RawEvent(
		category=EventCategory.MILESTONE,
		summary="Far away",
		start=date(2026, 8, 1),
	)
	program = ProgramReader(FakeCalendar(far, MILESTONE)).read(date(2026, 6, 22))
	assert program.next_milestone is not None
	assert program.next_milestone.title == "Foundation done"


def test_milestone_on_target_date_not_surfaced() -> None:
	today = RawEvent(
		category=EventCategory.MILESTONE,
		summary="Shipped today",
		start=date(2026, 6, 22),
	)
	program = ProgramReader(FakeCalendar(today)).read(date(2026, 6, 22))
	assert program.next_milestone is None


def test_morning_last_wins_when_multiple() -> None:
	early = RawEvent(
		category=EventCategory.MORNING,
		summary="AM: old habit",
		start=date(2026, 6, 1),
	)
	later = RawEvent(
		category=EventCategory.MORNING,
		summary="AM: new habit",
		start=date(2026, 6, 20),
	)
	program = ProgramReader(FakeCalendar(early, later)).read(date(2026, 6, 22))
	assert program.morning_habit == "AM: new habit"
