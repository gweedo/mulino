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

## MenuManager (value object)

A frozen `MenuManager(id, email)`: a person allowed to change the Menu —
today the pizzeria's owner, later possibly staff. Identity comes from
Supabase Auth (`id` is the Supabase user id), so there is no owners table and
no password in our code. Access is granted by the `menu_manager` role in the
user's `app_metadata` ([ADR 0003](./adr/0003-menu-manager-role-claim.md)).
Vocabulary is defined in the root `CONTEXT.md`.

## Public vs. admin visibility

The public pizza endpoints (`GET /api/pizzas`, `GET /api/pizzas/:id`) return
only pizzas with `available = true`. A Menu Manager toggles availability and
performs full create/edit/delete through the authenticated endpoints:
`POST /api/pizzas`, `PUT /api/pizzas/:id`, `DELETE /api/pizzas/:id`. The
admin list (`GET /api/admin/pizzas`) returns all pizzas regardless of
availability.
