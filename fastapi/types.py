from typing import Optional
from pydantic import BaseModel


class Result(BaseModel):
    result: str
    code: int
    message: Optional[str]
