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

			index: dict[str, dict[str, str]] = {}
			dupes: set[str] = set()
			for s in data.get("specs", []):
				spec_id = s.get("id")
				if not isinstance(spec_id, str):
					continue
				if spec_id in index:
					dupes.add(spec_id)
				index[spec_id] = s
			if dupes:
				raise SpecSourceError(f"duplicate spec ids in sidecar: {sorted(dupes)}")
			self._index = index
		return self._index

	def get(self, spec_id: str) -> dict[str, str] | None:
		return self._load().get(spec_id)
