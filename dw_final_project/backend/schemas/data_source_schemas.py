from pydantic import BaseModel


class DataSourceSummary(BaseModel):
    id: str


class DataSourceDetail(BaseModel):
    id: str
    system_time: str
    name: str
    description: str
    attributes: list[str]

    @classmethod
    def from_model(cls, m) -> "DataSourceDetail":
        return cls(
            id=m.id,
            system_time=m.system_date.isoformat(),
            name=m.name,
            description=m.description,
            attributes=sorted(m.attributes) if m.attributes else [],
        )
