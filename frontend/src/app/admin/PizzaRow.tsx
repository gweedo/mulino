'use client'

import { useState, useTransition } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
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
  const [confirmDelete, setConfirmDelete] = useState(false)

  function handleToggle() {
    startToggle(async () => {
      await toggleAvailabilityAction(pizza.id, !pizza.available)
      router.refresh()
    })
  }

  function handleDeleteClick() {
    if (!confirmDelete) {
      setConfirmDelete(true)
      setTimeout(() => setConfirmDelete(false), 4000)
      return
    }
    startDelete(async () => {
      await deletePizzaAction(pizza.id)
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
          className={`${styles.deleteBtn} ${confirmDelete ? styles.deleteBtnConfirm : ''}`}
          type="button"
          onClick={handleDeleteClick}
          disabled={deleting}
          aria-busy={deleting}
        >
          {deleting ? 'Eliminazione…' : confirmDelete ? 'Sei sicuro?' : 'Elimina'}
        </button>
      </div>
    </div>
  )
}
