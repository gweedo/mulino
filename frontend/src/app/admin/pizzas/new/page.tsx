import Link from 'next/link'
import type { Metadata } from 'next'
import PizzaForm from '@/components/PizzaForm'
import { createPizzaAction } from '../../actions'
import styles from '../form.module.css'

export const metadata: Metadata = { title: 'Nuova pizza — Pizzeria il Mulino' }

export default function NewPizzaPage() {
  return (
    <div className={styles.page}>
      <nav className={styles.breadcrumb} aria-label="Navigazione">
        <Link href="/admin" className={styles.back}>
          ← Menu
        </Link>
      </nav>
      <h1 className={styles.heading}>Nuova pizza</h1>
      <div className={styles.panel}>
        <PizzaForm action={createPizzaAction} />
      </div>
    </div>
  )
}
