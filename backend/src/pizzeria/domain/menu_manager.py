from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class MenuManager:
    """A person allowed to change the Menu (see CONTEXT.md).

    Identity comes from Supabase Auth: `id` is the Supabase user id (`sub` claim).
    """

    id: UUID
    email: str

    def __post_init__(self):
        if not self.email:
            raise ValueError("email must be non-empty")
        if "@" not in self.email:
            raise ValueError("email must contain '@'")
