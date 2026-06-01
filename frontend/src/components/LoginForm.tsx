'use client'

import { useId, useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { loginAction } from '@/app/admin/actions'
import styles from './LoginForm.module.css'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

interface FieldErrors {
  email?: string
  password?: string
}

export default function LoginForm() {
  const router = useRouter()
  const emailId = useId()
  const passwordId = useId()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [pending, startTransition] = useTransition()

  function validate(): FieldErrors {
    const next: FieldErrors = {}
    if (!EMAIL_RE.test(email.trim())) next.email = "Inserisci un'email valida."
    if (!password) next.password = 'Inserisci la password.'
    return next
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    const errors = validate()
    setFieldErrors(errors)
    if (errors.email || errors.password) return

    startTransition(async () => {
      try {
        await loginAction(email.trim(), password)
        router.push('/admin')
        router.refresh()
      } catch (err) {
        const msg = err instanceof Error ? err.message : ''
        if (msg === '401') {
          setFormError('Email o password non corretti.')
        } else {
          setFormError('Si è verificato un problema. Riprova.')
        }
      }
    })
  }

  const emailErrorId = `${emailId}-error`
  const passwordErrorId = `${passwordId}-error`

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {formError && (
        <p className={styles.formError} role="alert">
          {formError}
        </p>
      )}

      <div className={styles.field}>
        <label className={styles.label} htmlFor={emailId}>
          Email
        </label>
        <input
          id={emailId}
          className={styles.input}
          type="email"
          name="email"
          autoComplete="username"
          autoCapitalize="none"
          spellCheck={false}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={pending}
          aria-invalid={fieldErrors.email ? true : undefined}
          aria-describedby={fieldErrors.email ? emailErrorId : undefined}
        />
        {fieldErrors.email && (
          <span id={emailErrorId} className={styles.fieldError}>
            {fieldErrors.email}
          </span>
        )}
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor={passwordId}>
          Password
        </label>
        <input
          id={passwordId}
          className={styles.input}
          type="password"
          name="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={pending}
          aria-invalid={fieldErrors.password ? true : undefined}
          aria-describedby={fieldErrors.password ? passwordErrorId : undefined}
        />
        {fieldErrors.password && (
          <span id={passwordErrorId} className={styles.fieldError}>
            {fieldErrors.password}
          </span>
        )}
      </div>

      <button className={styles.submit} type="submit" disabled={pending} aria-busy={pending}>
        {pending ? 'Accesso in corso…' : 'Accedi'}
      </button>
    </form>
  )
}
