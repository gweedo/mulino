import styles from './Contacts.module.css'

export default function Contacts() {
  return (
    <footer id="contatti" className={styles.footer}>
      <div className={styles.inner}>
        <h2 className={styles.heading}>Dove siamo</h2>

        <div className={styles.grid}>
          <div className={styles.col}>
            <h3>Indirizzo</h3>
            <address className={styles.address}>
              Via del Mulino, 12<br />
              00100 Roma RM
              <p>
                <a
                  href="https://maps.app.goo.gl/DB4NzLKxTB1yXaxaA"
                  className={styles.mapLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Apri in Maps
                </a>
              </p>
            </address>
          </div>

          <div className={styles.col}>
            <h3>Orari</h3>
            <ul className={styles.hours} aria-label="Orari di apertura">
              <li>Mer – Lun&ensp;19:00 – 23:00</li>
              <li>Martedì&ensp;chiuso</li>
            </ul>
          </div>

          <div className={styles.col}>
            <h3>Telefono</h3>
            <a href="tel:+390600000000" className={styles.phone}>
              +39 06 000 0000
            </a>
          </div>
        </div>

        <p className={styles.note}>
          Pizzeria il Mulino · Via del Mulino, 12 · 00100 Roma
        </p>
      </div>
    </footer>
  )
}
