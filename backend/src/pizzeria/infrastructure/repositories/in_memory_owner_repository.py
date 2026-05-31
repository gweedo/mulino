"""In-memory OwnerRepository for testing and local development."""

from pizzeria.application.ports.owner_repository import OwnerRepository
from pizzeria.domain.owner import Owner


class InMemoryOwnerRepository(OwnerRepository):  # type: ignore[misc]
    def __init__(self) -> None:
        self._owners: dict[str, Owner] = {}

    async def get_by_email(self, email: str) -> Owner | None:
        return self._owners.get(email)

    async def add(self, owner: Owner) -> None:
        self._owners[owner.email] = owner
