'use client'

import { useState, useTransition } from 'react'
import Link from 'next/link'
import { allergenLabel } from '@/lib/allergens'
import type { PizzaOut } from '@/lib/types'
import type { PizzaFormValues } from '@/app/admin/actions'
import styles from './PizzaForm.module.css'

const ALL_ALLERGENS = Object.keys(allergenLabel)

interface PizzaFormProps {
  initial?: PizzaOut
  action: (data: PizzaFormValues) => Promise<void>
}

interface FieldErrors {
  name?: string
  description?: string
  ingredients?: string
  price_amount?: string
}

export default function PizzaForm({ initial, action }: PizzaFormProps) {
  const [name, setName] = useState(initial?.name ?? '')
  const [description, setDescription] = useState(initial?.description ?? '')
  const [ingredients, setIngredients] = useState(
    initial?.ingredients.join(', ') ?? '',
  )
  const [allergens, setAllergens] = useState<string[]>(initial?.allergens ?? [])
  const [priceAmount, setPriceAmount] = useState(
    initial?.price.amount ?? '',
  )
  const [available, setAvailable] = useState(initial?.available ?? true)
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [pending, startTransition] = useTransition()

  function toggleAllergen(key: string) {
    setAllergens((prev) =>
      prev.includes(key) ? prev.filter((a) => a !== key) : [...prev, key],
    )
  }

  function validate(): FieldErrors {
    const errors: FieldErrors = {}
    if (!name.trim()) errors.name = 'Il nome è obbligatorio.'
    else if (name.trim().length > 80) errors.name = 'Massimo 80 caratteri.'
    if (!description.trim()) errors.description = 'La descrizione è obbligatoria.'
    const parsedIngredients = ingredients
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    if (parsedIngredients.length === 0)
      errors.ingredients = 'Inserisci almeno un ingrediente.'
    const price = parseFloat(priceAmount)
    if (!priceAmount || isNaN(price) || price <= 0)
      errors.price_amount = 'Inserisci un prezzo valido maggiore di zero.'
    return errors
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    const errors = validate()
    setFieldErrors(errors)
    if (Object.keys(errors).length > 0) return

    const parsedIngredients = ingredients
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)

    const payload: PizzaFormValues = {
      name: name.trim(),
      description: description.trim(),
      ingredients: parsedIngredients,
      allergens,
      price_amount: parseFloat(priceAmount).toFixed(2),
      price_currency: 'EUR',
      ...(initial !== undefined ? { available } : {}),
    }

    startTransition(async () => {
      try {
        await action(payload)
      } catch (err) {
        setServerError(
          err instanceof Error ? err.message : 'Si è verificato un errore. Riprova.',
        )
      }
    })
  }

  const isEdit = initial !== undefined

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {serverError && (
        <p className={styles.formError} role="alert">
          {serverError}
        </p>
      )}

      <Field label="Nome" error={fieldErrors.name}>
        <input
          className={styles.input}
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={80}
          disabled={pending}
          aria-invalid={fieldErrors.name ? true : undefined}
        />
      </Field>

      <Field label="Descrizione" error={fieldErrors.description}>
        <textarea
          className={styles.textarea}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          disabled={pending}
          aria-invalid={fieldErrors.description ? true : undefined}
        />
      </Field>

      <Field
        label="Ingredienti"
        hint="Separati da virgola"
        error={fieldErrors.ingredients}
      >
        <input
          className={styles.input}
          type="text"
          value={ingredients}
          onChange={(e) => setIngredients(e.target.value)}
          placeholder="farina 00, pomodoro, mozzarella"
          disabled={pending}
          aria-invalid={fieldErrors.ingredients ? true : undefined}
        />
      </Field>

      <fieldset className={styles.fieldset}>
        <legend className={styles.legend}>Allergeni</legend>
        <div className={styles.allergenGrid}>
          {ALL_ALLERGENS.map((key) => (
            <label key={key} className={styles.allergenLabel}>
              <input
                className={styles.checkbox}
                type="checkbox"
                checked={allergens.includes(key)}
                onChange={() => toggleAllergen(key)}
                disabled={pending}
              />
              {allergenLabel[key]}
            </label>
          ))}
        </div>
      </fieldset>

      <Field label="Prezzo (€)" error={fieldErrors.price_amount}>
        <input
          className={`${styles.input} ${styles.inputPrice}`}
          type="number"
          min="0.01"
          step="0.50"
          value={priceAmount}
          onChange={(e) => setPriceAmount(e.target.value)}
          disabled={pending}
          aria-invalid={fieldErrors.price_amount ? true : undefined}
        />
      </Field>

      {isEdit && (
        <label className={styles.availableRow}>
          <input
            className={styles.checkbox}
            type="checkbox"
            checked={available}
            onChange={(e) => setAvailable(e.target.checked)}
            disabled={pending}
          />
          <span className={styles.availableLabel}>Pizza disponibile</span>
        </label>
      )}

      <div className={styles.formActions}>
        <Link href="/admin" className={styles.cancelLink}>
          Annulla
        </Link>
        <button className={styles.submit} type="submit" disabled={pending} aria-busy={pending}>
          {pending
            ? 'Salvataggio…'
            : isEdit
              ? 'Salva modifiche'
              : 'Aggiungi pizza'}
        </button>
      </div>
    </form>
  )
}

function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string
  hint?: string
  error?: string
  children: React.ReactNode
}) {
  return (
    <div className={styles.field}>
      <label className={styles.label}>
        {label}
        {hint && <span className={styles.hint}>{hint}</span>}
      </label>
      {children}
      {error && <span className={styles.fieldError}>{error}</span>}
    </div>
  )
}
