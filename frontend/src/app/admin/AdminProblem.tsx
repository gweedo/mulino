import { errorMessage, type BackendErrorKind } from '@/lib/result'
import styles from './dashboard.module.css'

/** Shown instead of admin content when FastAPI refuses or can't be reached. */
export default function AdminProblem({ kind }: { kind: BackendErrorKind }) {
  return (
    <div className={styles.empty} role="alert">
      <p>{errorMessage(kind)}</p>
      {kind === 'forbidden' && <p>Esci e accedi con un account abilitato.</p>}
    </div>
  )
}
