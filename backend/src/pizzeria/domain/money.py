from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("amount must be greater than 0")
        if not (isinstance(self.currency, str) and len(self.currency) == 3 and self.currency.isupper()):
            raise ValueError("currency must be 3 uppercase ISO 4217")

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
