from dataclasses import dataclass, field


@dataclass
class Book:
    id: int = field(init=False)
    tittle: str
    author: str
