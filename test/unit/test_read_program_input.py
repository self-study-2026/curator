from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.tools.read_program import ReadProgramInput, _parse_date, handle_read_program


def test_iso_date_string_parsed() -> None:
	assert _parse_date("2026-06-22") == date(2026, 6, 22)


def test_today_resolves_to_current_date() -> None:
	assert _parse_date("today") == date.today()


def test_invalid_date_string_raises() -> None:
	with pytest.raises(ValueError):
		_parse_date("not-a-date")


def test_input_model_accepts_iso_date() -> None:
	inp = ReadProgramInput(date="2026-06-22")
	assert inp.date == "2026-06-22"


def test_input_model_accepts_today() -> None:
	inp = ReadProgramInput(date="today")
	assert inp.date == "today"


def test_input_model_rejects_invalid_date() -> None:
	with pytest.raises(ValueError):
		ReadProgramInput(date="not-a-date")


def test_handle_passes_parsed_date_to_read_program() -> None:
	with patch("src.tools.read_program.read_program") as mock_rp:
		mock_rp.return_value = MagicMock()
		handle_read_program(ReadProgramInput(date="2026-06-22"))
		mock_rp.assert_called_once_with(date(2026, 6, 22))


def test_handle_resolves_today() -> None:
	with patch("src.tools.read_program.read_program") as mock_rp:
		mock_rp.return_value = MagicMock()
		handle_read_program(ReadProgramInput(date="today"))
		mock_rp.assert_called_once_with(date.today())
