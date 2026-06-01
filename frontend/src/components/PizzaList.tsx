'use client'

import { motion, useReducedMotion } from 'motion/react'
import type { PizzaItem } from '@/lib/types'
import PizzaCard from './PizzaCard'
import styles from './PizzaList.module.css'

interface AnimatedItemProps {
  children: React.ReactNode
  index: number
}

function AnimatedItem({ children, index }: AnimatedItemProps) {
  const shouldReduce = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduce ? 0 : 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{
        duration: shouldReduce ? 0.1 : 0.45,
        delay: shouldReduce ? 0 : index * 0.06,
        ease: [0, 0, 0.2, 1],
      }}
      viewport={{ once: true, margin: '-40px' }}
    >
      {children}
    </motion.div>
  )
}

interface Props {
  pizzas: PizzaItem[]
}

export default function PizzaList({ pizzas }: Props) {
  return (
    <section id="menu" className={styles.section} aria-label="Menu">
      <h2 className={styles.heading}>Menu</h2>

      {pizzas.length === 0 ? (
        <p className={styles.empty}>Nessuna pizza disponibile al momento.</p>
      ) : (
        <ul className={styles.list}>
          {pizzas.map((pizza, i) => (
            <AnimatedItem key={pizza.id} index={i}>
              <PizzaCard pizza={pizza} />
            </AnimatedItem>
          ))}
        </ul>
      )}
    </section>
  )
}
