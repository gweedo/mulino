import Link from 'next/link'
import { notFound } from 'next/navigation'
import { cookies } from 'next/headers'
import type { Metadata } from 'next'
import type { PizzaOut } from '@/lib/types'
import PizzaForm from '@/components/PizzaForm'
import { updatePizzaAction } from '../../../actions'
import styles from '../../form.module.css'

export const metadata: Metadata = { title: 'Modifica pizza — Pizzeria il Mulino' }

// The backend has no GET /api/admin/pizzas/:id endpoint — only a full list.
// Fetch the list and find by ID.
async function fetchPizza(id: string): Promise<PizzaOut | null> {
  const store = await cookies()
  const session = store.get('session')
  const backend = process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'

  try {
    const res = await fetch(`${backend}/api/admin/pizzas`, {
      headers: session ? { Cookie: `session=${session.value}` } : {},
      cache: 'no-store',
    })
    if (!res.ok) return null
    const pizzas: PizzaOut[] = await res.json()
    return pizzas.find((p) => p.id === id) ?? null
  } catch {
    return null
  }
}

export default async function EditPizzaPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const pizza = await fetchPizza(id)
  if (!pizza) notFound()

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
