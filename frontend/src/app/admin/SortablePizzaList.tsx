'use client'

import { useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type Announcements,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { errorMessage } from '@/lib/result'
import type { PizzaOut } from '@/lib/types'
import { reorderPizzasAction } from './actions'
import PizzaRow from './PizzaRow'
import styles from './dashboard.module.css'

const SCREEN_READER_INSTRUCTIONS =
  'Per spostare una pizza, premi spazio o invio, usa le frecce su e giù, ' +
  'poi premi di nuovo spazio o invio per lasciarla. Esc annulla.'

function SortableItem({ pizza }: { pizza: PizzaOut }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: pizza.id })

  return (
    <li
      ref={setNodeRef}
      data-pizza-id={pizza.id}
      className={`${styles.sortableItem} ${isDragging ? styles.sortableItemDragging : ''}`}
      style={{ transform: CSS.Translate.toString(transform), transition }}
    >
      <button
        ref={setActivatorNodeRef}
        type="button"
        className={styles.dragHandle}
        aria-label={`Riordina ${pizza.name}`}
        {...attributes}
        {...listeners}
      >
        <svg width="12" height="18" viewBox="0 0 12 18" aria-hidden="true">
          {[3, 9].map((cx) =>
            [3, 9, 15].map((cy) => <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="1.6" />),
          )}
        </svg>
      </button>
      <div className={styles.sortableRow}>
        <PizzaRow pizza={pizza} />
      </div>
    </li>
  )
}

export default function SortablePizzaList({ pizzas }: { pizzas: PizzaOut[] }) {
  const router = useRouter()
  const [saving, startSaving] = useTransition()
  const [error, setError] = useState<string | null>(null)

  // Optimistic Menu Order, reset whenever the server sends a different list.
  const serverOrder = pizzas.map((p) => p.id)
  const serverKey = serverOrder.join(',')
  const [syncedKey, setSyncedKey] = useState(serverKey)
  const [order, setOrder] = useState(serverOrder)
  if (serverKey !== syncedKey) {
    setSyncedKey(serverKey)
    setOrder(serverOrder)
  }

  const byId = new Map(pizzas.map((p) => [p.id, p]))
  const items = order.filter((id) => byId.has(id))

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  const nameOf = (id: string | number) => byId.get(String(id))?.name ?? ''
  const placeOf = (id: string | number) => items.indexOf(String(id)) + 1
  const announcements: Announcements = {
    onDragStart: ({ active }) => `Hai preso ${nameOf(active.id)}.`,
    onDragOver: ({ active, over }) =>
      over ? `${nameOf(active.id)} è in posizione ${placeOf(over.id)} di ${items.length}.` : undefined,
    onDragEnd: ({ active, over }) =>
      over
        ? `${nameOf(active.id)} lasciata in posizione ${placeOf(over.id)} di ${items.length}.`
        : `${nameOf(active.id)} lasciata.`,
    onDragCancel: ({ active }) => `Spostamento annullato. ${nameOf(active.id)} è tornata al suo posto.`,
  }

  function handleDragEnd({ active, over }: DragEndEvent) {
    if (!over || active.id === over.id) return
    const previous = items
    const next = arrayMove(items, items.indexOf(String(active.id)), items.indexOf(String(over.id)))
    setOrder(next)
    setError(null)
    startSaving(async () => {
      const result = await reorderPizzasAction(next)
      if (!result.ok) {
        setOrder(previous)
        if (result.error.kind === 'unauthorized') {
          router.push('/admin/login')
          return
        }
        setError(errorMessage(result.error.kind, 'reorder'))
      }
      router.refresh()
    })
  }

  return (
    <>
      {error && (
        <p className={styles.orderError} role="alert">
          {error}
        </p>
      )}
      <DndContext
        id="admin-menu-order"
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
        accessibility={{
          announcements,
          screenReaderInstructions: { draggable: SCREEN_READER_INSTRUCTIONS },
        }}
      >
        <SortableContext items={items} strategy={verticalListSortingStrategy}>
          <ul className={styles.list} role="list" aria-busy={saving}>
            {items.map((id) => (
              <SortableItem key={id} pizza={byId.get(id)!} />
            ))}
          </ul>
        </SortableContext>
      </DndContext>
    </>
  )
}
