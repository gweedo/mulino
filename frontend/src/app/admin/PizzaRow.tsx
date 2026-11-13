'use client'

import { useEffect, useId, useRef, useState, useTransition } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { errorMessage } from '@/lib/result'
import type { PizzaOut } from '@/lib/types'
import { toggleAvailabilityAction, deletePizzaAction } from './actions'
import styles from './dashboard.module.css'

function formatPrice(amount: string): string {
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(
    parseFloat(amount),
  )
}

export default function PizzaRow({ pizza }: { pizza: PizzaOut }) {
  const router = useRouter()
  const [toggling, startToggle] = useTransition()
  const [deleting, startDelete] = useTransition()
  const [confirming, setConfirming] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [toggleError, setToggleError] = useState<string | null>(null)
  const dialogRef = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const bodyId = useId()

  useEffect(() => {
    if (confirming) dialogRef.current?.showModal()
  }, [confirming])

  function handleToggle() {
    setToggleError(null)
    startToggle(async () => {
      const result = await toggleAvailabilityAction(pizza.id, !pizza.available)
      if (!result.ok) {
        if (result.error.kind === 'unauthorized') router.push('/admin/login')
        else setToggleError(errorMessage(result.error.kind, 'toggle'))
        return
      }
      router.refresh()
    })
  }

  function openConfirm() {
    setDeleteError(null)
    setConfirming(true)
  }

  function closeConfirm() {
    if (!deleting) dialogRef.current?.close()
  }

  function handleConfirmDelete() {
    setDeleteError(null)
    startDelete(async () => {
      const result = await deletePizzaAction(pizza.id)
      if (!result.ok) {
        if (result.error.kind === 'unauthorized') router.push('/admin/login')
        else setDeleteError(errorMessage(result.error.kind, 'delete'))
        return
      }
      dialogRef.current?.close()
      router.refresh()
    })
  }

  return (
    <div className={styles.row}>
      <div className={styles.rowMain}>
        <span className={styles.pizzaName}>{pizza.name}</span>
        <span className={styles.pizzaPrice}>{formatPrice(pizza.price.amount)}</span>
      </div>

      <p className={styles.pizzaDesc}>{pizza.description}</p>

      {pizza.ingredients.length > 0 && (
        <p className={styles.pizzaIngredients}>
          <span className={styles.pizzaIngredientsLabel}>Ingredienti: </span>
          {pizza.ingredients.join(', ')}
        </p>
      )}

      <div className={styles.rowActions}>
        <button
          className={`${styles.toggle} ${pizza.available ? styles.toggleOn : styles.toggleOff}`}
          type="button"
          onClick={handleToggle}
          disabled={toggling}
          aria-pressed={pizza.available}
          aria-label={pizza.available ? 'Disattiva pizza' : 'Attiva pizza'}
        >
          <span className={styles.toggleDot} />
          {pizza.available ? 'Attiva' : 'Non attiva'}
        </button>

        <Link href={`/admin/pizzas/${pizza.id}/edit`} className={styles.editLink}>
          Modifica
        </Link>

        <button
          className={styles.deleteBtn}
          type="button"
          onClick={openConfirm}
          aria-haspopup="dialog"
        >
          Elimina
        </button>
      </div>

      {toggleError && (
        <p className={styles.orderError} role="alert">
          {toggleError}
        </p>
      )}

      {confirming && (
        <dialog
          ref={dialogRef}
          className={styles.dialog}
          aria-labelledby={titleId}
          aria-describedby={bodyId}
          onClose={() => setConfirming(false)}
          onCancel={(e) => {
            if (deleting) e.preventDefault()
          }}
          onClick={(e) => {
            // A click on the backdrop lands on the <dialog> element itself.
            if (e.target === e.currentTarget) closeConfirm()
          }}
        >
          <h2 id={titleId} className={styles.dialogTitle}>
            Eliminare «{pizza.name}»?
          </h2>
          <p id={bodyId} className={styles.dialogBody}>
            La pizza verrà rimossa dal menu. L’operazione non si può annullare.
          </p>

          {deleteError && (
            <p className={styles.dialogError} role="alert">
              {deleteError}
            </p>
          )}

          <div className={styles.dialogActions}>
            <button
              className={styles.dialogCancel}
              type="button"
              onClick={closeConfirm}
              disabled={deleting}
              autoFocus
            >
              Annulla
            </button>
            <button
              className={styles.dialogConfirm}
              type="button"
              onClick={handleConfirmDelete}
              disabled={deleting}
              aria-busy={deleting}
            >
              {deleting ? 'Eliminazione…' : 'Elimina'}
            </button>
          </div>
        </dialog>
      )}
    </div>
  )
}
