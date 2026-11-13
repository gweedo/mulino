import Link from 'next/link'
import { redirect } from 'next/navigation'
import { listAdminPizzas } from '@/lib/backend'
import AdminProblem from './AdminProblem'
import SortablePizzaList from './SortablePizzaList'
import styles from './dashboard.module.css'

export default async function AdminDashboard() {
  const result = await listAdminPizzas()
  if (!result.ok && result.error.kind === 'unauthorized') redirect('/admin/login')

  return (
    <div className={styles.page}>
      <div className={styles.toolbar}>
        <h1 className={styles.heading}>Menu</h1>
        <Link href="/admin/pizzas/new" className={styles.addButton}>
          + Nuova pizza
        </Link>
      </div>

      {!result.ok ? (
        <AdminProblem kind={result.error.kind} />
      ) : result.data.length === 0 ? (
        <div className={styles.empty}>
          <p>Nessuna pizza nel menu.</p>
          <Link href="/admin/pizzas/new" className={styles.emptyLink}>
            Aggiungi la prima pizza
          </Link>
        </div>
      ) : (
        <SortablePizzaList pizzas={result.data} />
      )}
    </div>
  )
}
