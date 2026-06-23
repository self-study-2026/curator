import re
from datetime import date, datetime

from src.program.domain import (
	EventCategory,
	Milestone,
	Program,
	RawEvent,
	Session,
	to_date,
)
from src.program.ports import CalendarSource, SpecSource, SpecSourceError


def _parse_times(event: RawEvent) -> tuple[str, str | None]:
	start, end = event.start, event.end
	time_str = start.strftime("%H:%M") if isinstance(start, datetime) else ""
	if isinstance(start, datetime) and isinstance(end, datetime):
		time_budget: str | None = _format_budget(start, end)
	else:
		time_budget = None
	return time_str, time_budget


def _format_budget(start: datetime, end: datetime) -> str:
	minutes = int((end - start).total_seconds() // 60)
	h, m = divmod(minutes, 60)
	if h and m:
		return f"{h}h{m:02d}m"
	return f"{h}h" if h else f"{m}m"


def _extract_spec_id(title: str, specs: SpecSource) -> str | None:
	m = re.search(r"(?:^|[\s])([A-Z][A-Z0-9]*(?:[-\.][A-Z0-9]+)*):", title)
	if m and specs.get(m.group(1)) is not None:
		return m.group(1)
	return None


def _morning_covers(event: RawEvent, target_date: date) -> bool:
	if to_date(event.start) > target_date or target_date.weekday() >= 5:
		return False
	if event.rrule_until is not None and target_date > event.rrule_until:
		return False
	return True


class ProgramReader:
	def __init__(self, calendar: CalendarSource, specs: SpecSource) -> None:
		self._calendar = calendar
		self._specs = specs

	def _build_session(self, event: RawEvent) -> Session:
		time_str, time_budget = _parse_times(event)
		spec_id = _extract_spec_id(event.summary, self._specs)
		spec = self._specs.get(spec_id) if spec_id else None
		return Session(
			time=time_str,
			title=event.summary,
			spec_id=spec_id,
			spec_path=spec["file"] if spec else None,
			time_budget=time_budget,
		)

	def read(self, target_date: date) -> Program:
		sessions: list[Session] = []
		morning_habit: str | None = None
		current_phase: str | None = None
		plan_error: str | None = None
		milestones_ahead: list[tuple[date, str]] = []

		for event in self._calendar.events():
			match event.category:
				case EventCategory.SESSION:
					if to_date(event.start) == target_date:
						try:
							sessions.append(self._build_session(event))
						except SpecSourceError as e:
							time_str, time_budget = _parse_times(event)
							sessions.append(
								Session(
									time=time_str,
									title=event.summary,
									spec_id=None,
									spec_path=None,
									time_budget=time_budget,
								)
							)
							plan_error = str(e)
				case EventCategory.MORNING:
					if morning_habit is None and _morning_covers(event, target_date):
						morning_habit = event.summary
				case EventCategory.PHASE:
					phase_end = to_date(event.end) if event.end else None
					before_end = phase_end is None or target_date < phase_end
					if to_date(event.start) <= target_date and before_end:
						current_phase = event.summary
				case EventCategory.MILESTONE:
					ms_date = to_date(event.start)
					if ms_date > target_date:
						milestones_ahead.append((ms_date, event.summary))
				case _:
					pass

		next_milestone: Milestone | None = None
		if milestones_ahead:
			ms_date, ms_title = min(milestones_ahead)
			next_milestone = Milestone(date=ms_date.isoformat(), title=ms_title)

		return Program(
			date=target_date.isoformat(),
			sessions=sorted(sessions, key=lambda s: s.time),
			morning_habit=morning_habit,
			next_milestone=next_milestone,
			current_phase=current_phase,
			plan_error=plan_error,
		)
