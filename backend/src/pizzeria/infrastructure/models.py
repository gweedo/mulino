from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    CHAR,
    CheckConstraint,
    DateTime,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PizzaORM(Base):
    __tablename__ = "pizzas"
    __table_args__ = (
        CheckConstraint("array_length(ingredients, 1) >= 1", name="ck_pizzas_ingredients_nonempty"),
        CheckConstraint("price_amount > 0", name="ck_pizzas_price_amount_positive"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    ingredients: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    allergens: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    available: Mapped[bool] = mapped_column(nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class OwnerORM(Base):
    __tablename__ = "owners"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
