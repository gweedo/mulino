/**
 * Generated from /openapi.json — run `npm run types:gen` to refresh.
 * Manually written to match backend Pydantic schemas.
 */

export interface MoneyOut {
  /** Decimal serialised as string by Pydantic v2. */
  amount: string
  currency: string
}

export interface PizzaOut {
  id: string
  name: string
  description: string
  ingredients: string[]
  /** EU 14 allergen keys (e.g. "gluten", "milk"). */
  allergens: string[]
  price: MoneyOut
  available: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface MeResponse {
  id: string
  email: string
}

export interface PizzaIn {
  name: string
  description: string
  ingredients: string[]
  allergens: string[]
  price_amount: string
  price_currency: string
}

export interface PizzaUpdate {
  name?: string
  description?: string
  ingredients?: string[]
  allergens?: string[]
  price_amount?: string
  price_currency?: string
  available?: boolean
}
