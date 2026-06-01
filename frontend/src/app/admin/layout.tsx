import type { Metadata } from 'next'
import LogoutButton from '@/components/LogoutButton'
import styles from './layout.module.css'

export const metadata: Metadata = {
  title: 'Amministrazione — Pizzeria il Mulino',
  robots: { index: false, follow: false },
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <span className={styles.wordmark}>Pizzeria il Mulino</span>
        <LogoutButton />
      </header>
      <div className={styles.content}>{children}</div>
    </div>
  )
}
