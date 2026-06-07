from pydantic import BaseModel


class AssetSummary(BaseModel):
    id: str


class AssetDetail(BaseModel):
    id: str
    system_time: str
    name: str
    description: str
    attributes: dict[str, str]

    @classmethod
    def from_model(cls, m) -> "AssetDetail":
        return cls(
            id=m.id,
            system_time=m.system_date.isoformat(),
            name=m.name,
            description=m.description,
            attributes=m.attributes,
        )
