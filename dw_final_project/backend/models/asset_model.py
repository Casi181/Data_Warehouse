from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AssetModel:
    id: str
    system_date: datetime
    name: str = ""
    description: str = ""
    attributes: dict[str, str] = field(default_factory=dict)

    @property
    def is_deleted(self) -> bool:
        return self.attributes.get("deleted") == "true"
