import json
from pathlib import Path

from src.program.ports import SpecSourceError


class JsonSpecSource:
	def __init__(self, path: Path) -> None:
		self._path = path
		self._index: dict[str, dict[str, str]] | None = None

	def _load(self) -> dict[str, dict[str, str]]:
		if self._index is None:
			try:
				data = json.loads(self._path.read_text())
			except FileNotFoundError as e:
				raise SpecSourceError(f"spec sidecar not found: {self._path}") from e
			self._index = {s["id"]: s for s in data["specs"]}
		return self._index

	def get(self, spec_id: str) -> dict[str, str] | None:
		return self._load().get(spec_id)
