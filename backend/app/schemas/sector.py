from pydantic import BaseModel, ConfigDict


class SectorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
