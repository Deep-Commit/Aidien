from pydantic import BaseModel
from typing import List

class CodeInstruction(BaseModel):
    type: str
    filename: str
    find: str 
    replace: str 
    write: str 
    delete: str

class CodeModification(BaseModel):
    instructions: List[CodeInstruction]
