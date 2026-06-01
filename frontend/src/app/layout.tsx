import type { Metadata } from 'next'
import { Vollkorn } from 'next/font/google'
import './globals.css'

const vollkorn = Vollkorn({
  subsets: ['latin'],
  weight: ['400', '600', '800'],
  variable: '--font-vollkorn',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Pizzeria il Mulino',
  description: 'Pizza artigianale dal forno a legna. Vieni a trovarci.',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="it" className={vollkorn.variable}>
      <body>{children}</body>
    </html>
  )
}
