from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.application.ports.owner_repository import OwnerRepository
from pizzeria.domain.owner import Owner
from pizzeria.infrastructure.mappers import owner_from_orm
from pizzeria.infrastructure.models import OwnerORM


class SqlOwnerRepository(OwnerRepository):
    """PostgreSQL-backed OwnerRepository.

    Single read method today (`get_by_email`); the only writer is the seed
    script in step 10 which talks to the ORM directly.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_email(self, email: str) -> Owner | None:
        stmt = select(OwnerORM).where(OwnerORM.email == email)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return owner_from_orm(orm) if orm else None
