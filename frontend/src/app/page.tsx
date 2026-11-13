import { listMenu } from '@/lib/backend'
import Hero from '@/components/Hero'
import PizzaList from '@/components/PizzaList'
import Contacts from '@/components/Contacts'

export default async function HomePage() {
  const menu = await listMenu()

  return (
    <>
      <Hero />
      <main>
        <PizzaList pizzas={menu.ok ? menu.data : []} unavailable={!menu.ok} />
      </main>
      <Contacts />
    </>
  )
}
