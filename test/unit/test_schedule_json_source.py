import json
from datetime import date
from pathlib import Path

from src.program.adapters.schedule_json import JsonScheduleSource
from src.program.domain import EventCategory

MINIMAL_SCHEDULE = {
	"generated": "2026-06-18",
	"schedule": {
		"2026-06-22": [
			{
				"uid": "s0-0@test",
				"title": "Build the thing",
				"type": "build",
				"spec_id": "M0-curator-v0",
				"code": "M0",
				"category": "SESSION",
			},
			{
				"uid": "am-0@test",
				"title": "AM: kata",
				"type": "habit",
				"spec_id": None,
				"code": None,
				"category": "MORNING",
			},
		],
		"2026-06-23": [
			{
				"uid": "ms-1@test",
				"title": "Foundation done",
				"type": "milestone",
				"spec_id": "M0-curator-v0",
				"code": "M0",
				"category": "MILESTONE",
			},
		],
	},
}


def test_yields_events_from_all_dates(tmp_path: Path) -> None:
	f = tmp_path / "schedule.json"
	f.write_text(json.dumps(MINIMAL_SCHEDULE))
	events = list(JsonScheduleSource(f).events())
	assert len(events) == 3


def test_session_category_and_title(tmp_path: Path) -> None:
	f = tmp_path / "schedule.json"
	f.write_text(json.dumps(MINIMAL_SCHEDULE))
	session = next(
		e for e in JsonScheduleSource(f).events() if e.category == EventCategory.SESSION
	)
	assert session.summary == "Build the thing"
	assert session.start == date(2026, 6, 22)


def test_spec_id_propagated(tmp_path: Path) -> None:
	f = tmp_path / "schedule.json"
	f.write_text(json.dumps(MINIMAL_SCHEDULE))
	session = next(
		e for e in JsonScheduleSource(f).events() if e.category == EventCategory.SESSION
	)
	assert session.spec_id == "M0-curator-v0"


def test_null_spec_id_propagated(tmp_path: Path) -> None:
	f = tmp_path / "schedule.json"
	f.write_text(json.dumps(MINIMAL_SCHEDULE))
	morning = next(
		e for e in JsonScheduleSource(f).events() if e.category == EventCategory.MORNING
	)
	assert morning.spec_id is None


def test_events_yielded_in_date_order(tmp_path: Path) -> None:
	f = tmp_path / "schedule.json"
	f.write_text(json.dumps(MINIMAL_SCHEDULE))
	events = list(JsonScheduleSource(f).events())
	dates = [e.start for e in events]
	assert dates == sorted(dates)


def test_unknown_category_mapped(tmp_path: Path) -> None:
	schedule = {
		"schedule": {
			"2026-06-22": [
				{
					"uid": "x",
					"title": "note",
					"type": "note",
					"spec_id": None,
					"code": None,
					"category": "NOTE",
				},
			]
		}
	}
	f = tmp_path / "schedule.json"
	f.write_text(json.dumps(schedule))
	events = list(JsonScheduleSource(f).events())
	assert events[0].category == EventCategory.UNKNOWN
