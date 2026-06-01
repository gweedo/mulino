/**
 * Consumer-facing type aliases over the generated api-types.ts.
 * Import from here, not from api-types.ts directly.
 */
import type { components } from './api-types'

export type PizzaOut = components['schemas']['PizzaOut']
export type PizzaItem = components['schemas']['PizzaOut']
export type PizzaIn = components['schemas']['PizzaIn']
export type PizzaUpdate = components['schemas']['PizzaUpdate']
export type Money = components['schemas']['MoneyOut']
export type MoneyOut = components['schemas']['MoneyOut']
export type MeResponse = components['schemas']['MeResponse']
export type LoginRequest = components['schemas']['LoginRequest']
