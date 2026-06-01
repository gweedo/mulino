import Link from 'next/link'
import { notFound } from 'next/navigation'
import { cookies } from 'next/headers'
import type { Metadata } from 'next'
import type { PizzaOut } from '@/lib/types'
import PizzaForm from '@/components/PizzaForm'
import { updatePizzaAction } from '../../../actions'
import styles from '../../form.module.css'

export const metadata: Metadata = { title: 'Modifica pizza — Pizzeria il Mulino' }

async function fetchPizza(id: string): Promise<PizzaOut | null> {
  const store = await cookies()
  const session = store.get('session')
  const backend = process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'

  try {
    const res = await fetch(`${backend}/api/admin/pizzas/${id}`, {
      headers: session ? { Cookie: `session=${session.value}` } : {},
      cache: 'no-store',
    })
    if (res.status === 404) return null
    if (!res.ok) return null
    return res.json()
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
