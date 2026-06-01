import type { PizzaItem } from '@/lib/types'
import { allergenLabel } from '@/lib/allergens'
import styles from './PizzaCard.module.css'

function formatPrice(amount: string, currency: string): string {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(parseFloat(amount))
}

interface Props {
  pizza: PizzaItem
}

export default function PizzaCard({ pizza }: Props) {
  const formattedIngredients = pizza.ingredients.join(', ')

  return (
    <li className={styles.item}>
      <span className={styles.name}>{pizza.name}</span>
      <span className={styles.price} aria-label={`Prezzo: ${formatPrice(pizza.price.amount, pizza.price.currency)}`}>
        {formatPrice(pizza.price.amount, pizza.price.currency)}
      </span>

      {pizza.description && (
        <p className={styles.description}>{pizza.description}</p>
      )}

      {pizza.ingredients.length > 0 && (
        <p className={styles.ingredients}>
          <span aria-hidden="true">Ingredienti: </span>
          {formattedIngredients}
        </p>
      )}

      {pizza.allergens.length > 0 && (
        <ul className={styles.allergens} aria-label="Allergeni">
          {pizza.allergens.map((key) => (
            <li key={key} className={styles.allergenBadge}>
              {allergenLabel[key] ?? key}
            </li>
          ))}
        </ul>
      )}
    </li>
  )
}
