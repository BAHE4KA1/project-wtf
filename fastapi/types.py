from typing import Optional, List
from pydantic import BaseModel
from fastapi import WebSocket


class Result(BaseModel):
    result: str
    code: int
    message: Optional[str]
