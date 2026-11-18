from pydantic import BaseModel, ConfigDict


class CountyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: int
    name: str
