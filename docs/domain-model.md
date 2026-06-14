# Domain model

[← Back to docs index](./README.md)

All business rules live in the backend's `domain` layer as pure Python.
They are never enforced in the API or database layer, so the same invariants
hold regardless of how a pizza is created.

## Pizza (aggregate root)

| Field          | Rule                                                      |
|----------------|-----------------------------------------------------------|
| `id`           | Unique identifier (UUID).                                 |
| `name`         | Unique across all pizzas; at most 80 characters.          |
| `description`  | Free text.                                                |
| `ingredients`  | At least one ingredient.                                  |
| `allergens`    | A subset of the EU 14 allergen enum (see below).         |
| `price`        | A Money value object; amount must be greater than zero.   |
| `available`    | Boolean. Only available pizzas appear on the public site. |

Constructing a Pizza that violates any rule raises a domain error — invalid
pizzas cannot exist in memory and are never persisted.

## Money (value object)

An immutable amount-plus-currency pair. The amount must be positive. Money
is compared and stored by value, which keeps price arithmetic exact and
avoids floating-point rounding surprises.

## Allergen (value object / enum)

The EU's 14 regulated food allergens, exactly as named in Regulation (EU)
No 1169/2011:

`gluten`, `crustaceans`, `eggs`, `fish`, `peanuts`, `soy`, `milk`, `nuts`,
`celery`, `mustard`, `sesame`, `sulphites`, `lupin`, `molluscs`.

A pizza's allergen set must be a subset of these 14 values; anything outside
the set is rejected at the domain layer.

## Owner (value object)

A frozen `Owner(id, email, password_hash)`. There is a single owner — the
pizzeria proprietor. The `AuthenticateOwner` use case depends only on the
abstract `OwnerRepository` protocol, never on the ORM directly, so
authentication logic stays free of infrastructure concerns. The owner is
created once via `python -m pizzeria.seed_owner` and can be rotated with
the `OWNER_FORCE_RESET=1` flag.

## Public vs. admin visibility

The public pizza endpoints (`GET /api/pizzas`, `GET /api/pizzas/:id`) return
only pizzas with `available = true`. The owner toggles availability and
performs full create/edit/delete through the authenticated endpoints:
`POST /api/pizzas`, `PUT /api/pizzas/:id`, `DELETE /api/pizzas/:id`. The
admin list (`GET /api/admin/pizzas`) returns all pizzas regardless of
availability.
