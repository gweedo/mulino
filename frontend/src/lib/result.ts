/**
 * What every call to FastAPI (src/lib/backend.ts) and every server action returns.
 * Client-safe: components import these types and messages; backend.ts stays server-only.
 */

export type BackendErrorKind =
  | 'unauthorized' // no session or an expired one: go to /admin/login
  | 'forbidden' // signed in, but not a Menu Manager
  | 'not_found'
  | 'conflict' // duplicate pizza name, or a stale Menu Order
  | 'validation'
  | 'unavailable' // FastAPI unreachable or failing (network error, 5xx)

/** `detail` is FastAPI's English message, kept for logs and never shown to users. */
export interface BackendError {
  kind: BackendErrorKind
  detail?: string
}

export type Result<T> = { ok: true; data: T } | { ok: false; error: BackendError }

/** What the user was doing, where an error kind means different things. */
export type Operation = 'save' | 'toggle' | 'delete' | 'reorder'

const MESSAGES: Record<BackendErrorKind, string> = {
  unauthorized: 'La sessione è scaduta. Accedi di nuovo.',
  forbidden: 'Questo account non è abilitato a gestire il menu.',
  not_found: 'Questa pizza non esiste più. Ricarica la pagina.',
  conflict: 'Il menu è cambiato nel frattempo. Ricarica la pagina.',
  validation: 'Dati non validi. Controlla i campi e riprova.',
  unavailable: 'Il menu non è raggiungibile. Riprova tra poco.',
}

const BY_OPERATION: Partial<Record<Operation, Partial<Record<BackendErrorKind, string>>>> = {
  save: { conflict: 'Esiste già una pizza con questo nome.' },
  reorder: { conflict: "Il menu è cambiato nel frattempo: ricarico l'ordine attuale." },
}

/** The Italian message for an error the user should read. */
export function errorMessage(kind: BackendErrorKind, operation?: Operation): string {
  return (operation && BY_OPERATION[operation]?.[kind]) ?? MESSAGES[kind]
}
