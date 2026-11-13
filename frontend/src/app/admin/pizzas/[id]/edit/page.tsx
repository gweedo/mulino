import Link from 'next/link'
import { notFound, redirect } from 'next/navigation'
import type { Metadata } from 'next'
import { getAdminPizza } from '@/lib/backend'
import PizzaForm from '@/components/PizzaForm'
import { updatePizzaAction } from '../../../actions'
import AdminProblem from '../../../AdminProblem'
import styles from '../../form.module.css'

export const metadata: Metadata = { title: 'Modifica pizza — Pizzeria il Mulino' }

export default async function EditPizzaPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const result = await getAdminPizza(id)
  if (!result.ok) {
    if (result.error.kind === 'not_found') notFound()
    if (result.error.kind === 'unauthorized') redirect('/admin/login')
    return <AdminProblem kind={result.error.kind} />
  }
  const pizza = result.data

  const action = updatePizzaAction.bind(null, id)

  return (
    <div className={styles.page}>
      <nav className={styles.breadcrumb} aria-label="Navigazione">
        <Link href="/admin" className={styles.back}>
          ← Menu
        </Link>
      </nav>
      <h1 className={styles.heading}>Modifica: {pizza.name}</h1>
      <div className={styles.panel}>
        <PizzaForm initial={pizza} action={action} />
      </div>
    </div>
  )
}
