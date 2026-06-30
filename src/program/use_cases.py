from datetime import date

from src.program.domain import EventCategory, Milestone, Program, Session
from src.program.ports import CalendarSource


class ProgramReader:
	def __init__(self, calendar: CalendarSource) -> None:
		self._calendar = calendar

	def read(self, target_date: date) -> Program:
		sessions: list[Session] = []
		morning_habit: str | None = None
		current_phase: str | None = None
		milestones_ahead: list[tuple[date, str]] = []

		for event in self._calendar.events():
			match event.category:
				case EventCategory.SESSION:
					if event.start == target_date:
						sessions.append(
							Session(title=event.summary, spec_id=event.spec_id)
						)
				case EventCategory.MORNING:
					if event.start <= target_date and target_date.weekday() < 5:
						morning_habit = event.summary
				case EventCategory.PHASE:
					if event.start <= target_date:
						current_phase = event.summary
				case EventCategory.MILESTONE:
					if event.start > target_date:
						milestones_ahead.append((event.start, event.summary))
				case _:
					pass

		next_milestone: Milestone | None = None
		if milestones_ahead:
			ms_date, ms_title = min(milestones_ahead)
			next_milestone = Milestone(date=ms_date.isoformat(), title=ms_title)

		return Program(
			date=target_date.isoformat(),
			sessions=sessions,
			morning_habit=morning_habit,
			next_milestone=next_milestone,
			current_phase=current_phase,
		)
