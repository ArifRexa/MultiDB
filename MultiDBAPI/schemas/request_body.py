from pydantic import BaseModel
from typing import Optional
from dataclasses import dataclass


@dataclass
class RequestBody(BaseModel):
    database_info: dict
    data: Optional[list]
