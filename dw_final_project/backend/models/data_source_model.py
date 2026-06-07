from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DataSourceModel:
    id: str
    system_date: datetime
    name: str = ""
    description: str = ""
    attributes: set[str] = field(default_factory=set)
