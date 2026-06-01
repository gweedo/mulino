import type { Metadata } from 'next'
import LoginForm from '@/components/LoginForm'
import styles from './login.module.css'

export const metadata: Metadata = {
  title: 'Area riservata — Pizzeria il Mulino',
  robots: { index: false, follow: false },
}

export default function LoginPage() {
  return (
    <main className={styles.screen}>
      <div className={styles.panel}>
        <p className={styles.wordmark}>Pizzeria il Mulino</p>
        <h1 className={styles.heading}>Area riservata</h1>
        <p className={styles.subtitle}>Accedi per gestire il menu.</p>
        <LoginForm />
      </div>
    </main>
  )
}
