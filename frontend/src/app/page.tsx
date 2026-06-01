import type { PizzaItem } from '@/lib/types'
import Hero from '@/components/Hero'
import PizzaList from '@/components/PizzaList'
import Contacts from '@/components/Contacts'

async function fetchPizzas(): Promise<PizzaItem[]> {
  const base = process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'
  try {
    const res = await fetch(`${base}/api/pizzas`, {
      next: { tags: ['pizzas'], revalidate: 60 },
    })
    if (!res.ok) return []
    return res.json()
  } catch {
    return []
  }
}

export default async function HomePage() {
  const pizzas = await fetchPizzas()

  return (
    <>
      <Hero />
      <main>
        <PizzaList pizzas={pizzas} />
      </main>
      <Contacts />
    </>
  )
}
