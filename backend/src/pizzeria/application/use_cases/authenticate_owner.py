"""AuthenticateOwner use case."""

from collections.abc import Callable

from pizzeria.application.errors import InvalidCredentials
from pizzeria.application.ports.owner_repository import OwnerRepository


class AuthenticateOwner:
    """Use case: authenticate a pizzeria owner and return a JWT."""

    def __init__(
        self,
        owner_repository: OwnerRepository,
        verify_password: Callable[[str, str], bool],
        encode_token: Callable[[str], str],
    ) -> None:
        self._owner_repository = owner_repository
        self._verify_password = verify_password
        self._encode_token = encode_token

    async def execute(self, email: str, password: str) -> str:
        """Return a JWT token on valid credentials.

        Raises:
            InvalidCredentials: for both unknown email and wrong password,
                so callers cannot distinguish which check failed.
        """
        owner = await self._owner_repository.get_by_email(email)
        if owner is None or not self._verify_password(password, owner.password_hash):
            raise InvalidCredentials
        return self._encode_token(owner.email)
