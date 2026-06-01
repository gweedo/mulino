import styles from './Hero.module.css'

export default function Hero() {
  return (
    <header className={styles.hero}>
      <nav className={styles.nav} aria-label="Navigazione principale">
        <span className={styles.navLogo} aria-hidden="true">Pizzeria il Mulino</span>
        <a href="#contatti" className={styles.navLink}>Contatti</a>
      </nav>

      <div className={styles.content}>
        <h1 className={styles.heading}>
          <span className={styles.headingLabel}>Pizzeria</span>
          il Mulino
        </h1>
        <p className={styles.tagline}>
          Pizza artigianale dal forno a legna.
        </p>
        <a href="#menu" className={styles.cta}>
          Vedi il menu
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M8 3v10M3 8l5 5 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </a>
      </div>
    </header>
  )
}
