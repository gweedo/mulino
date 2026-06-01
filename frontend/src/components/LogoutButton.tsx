'use client'

import { useState } from 'react'
import { logoutAction } from '@/app/admin/actions'
import styles from './LogoutButton.module.css'

export default function LogoutButton() {
  const [pending, setPending] = useState(false)

  async function handleClick() {
    setPending(true)
    await logoutAction()
  }

  return (
    <button
      className={styles.button}
      type="button"
      onClick={handleClick}
      disabled={pending}
      aria-busy={pending}
    >
      {pending ? 'Uscita…' : 'Esci'}
    </button>
  )
}
