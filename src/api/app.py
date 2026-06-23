from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Query, status
from pydantic import BaseModel

from src.program.domain import Program
from src.tools.read_program import ReadProgramInput, handle_read_program

app = FastAPI()


class HealthResult(BaseModel):
	status: str
	last_digest: datetime | None


@app.get("/health", status_code=status.HTTP_200_OK)
def health() -> HealthResult:
	return HealthResult(status="ok", last_digest=None)


@app.get("/program", status_code=status.HTTP_200_OK)
async def test_program(date: Annotated[str, Query()] = "today") -> Program:
	return handle_read_program(ReadProgramInput(date=date))
