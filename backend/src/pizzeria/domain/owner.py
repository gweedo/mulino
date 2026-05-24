from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Owner:
    id: UUID
    email: str
    password_hash: str

    def __post_init__(self):
        if not self.email:
            raise ValueError("email must be non-empty")
        if "@" not in self.email:
            raise ValueError("email must contain '@'")
        if not self.password_hash:
            raise ValueError("password_hash must be non-empty")
