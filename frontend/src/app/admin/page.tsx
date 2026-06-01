import Link from 'next/link'
import { cookies } from 'next/headers'
import type { PizzaOut } from '@/lib/types'
import PizzaRow from './PizzaRow'
import styles from './dashboard.module.css'

async function fetchAdminPizzas(): Promise<PizzaOut[]> {
  const store = await cookies()
  const session = store.get('session')
  const backend = process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'

  try {
    const res = await fetch(`${backend}/api/admin/pizzas`, {
      headers: session ? { Cookie: `session=${session.value}` } : {},
      cache: 'no-store',
    })
    if (!res.ok) return []
    return res.json()
  } catch {
    return []
  }
}

export default async function AdminDashboard() {
  const pizzas = await fetchAdminPizzas()

  return (
    <div className={styles.page}>
      <div className={styles.toolbar}>
        <h1 className={styles.heading}>Menu</h1>
        <Link href="/admin/pizzas/new" className={styles.addButton}>
          + Nuova pizza
        </Link>
      </div>

      {pizzas.length === 0 ? (
        <div className={styles.empty}>
          <p>Nessuna pizza nel menu.</p>
          <Link href="/admin/pizzas/new" className={styles.emptyLink}>
            Aggiungi la prima pizza
          </Link>
        </div>
      ) : (
        <ul className={styles.list} role="list">
          {pizzas.map((pizza) => (
            <li key={pizza.id}>
              <PizzaRow pizza={pizza} />
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
