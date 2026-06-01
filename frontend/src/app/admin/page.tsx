'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { logout } from '@/lib/api'
import styles from './admin.module.css'

// Placeholder landing for the authenticated admin area. Step 15 replaces this
// with the pizza CRUD dashboard; for now it confirms the session and offers a
// way back out, completing the login/logout loop.
export default function AdminHome() {
  const router = useRouter()
  const [signingOut, setSigningOut] = useState(false)

  async function handleLogout() {
    setSigningOut(true)
    try {
      await logout()
    } finally {
      router.push('/admin/login')
      router.refresh()
    }
  }

  return (
    <main className={styles.screen}>
      <div className={styles.panel}>
        <p className={styles.wordmark}>Pizzeria il Mulino</p>
        <h1 className={styles.heading}>Amministrazione</h1>
        <p className={styles.subtitle}>
          La gestione del menu arriva nel prossimo passo. Per ora hai effettuato
          l&apos;accesso.
        </p>
        <button
          className={styles.logout}
          type="button"
          onClick={handleLogout}
          disabled={signingOut}
          aria-busy={signingOut}
        >
          {signingOut ? 'Disconnessione…' : 'Esci'}
        </button>
      </div>
    </main>
  )
}
