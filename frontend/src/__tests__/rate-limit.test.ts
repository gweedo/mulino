import { createRateLimiter } from '@/lib/rate-limit'

describe('createRateLimiter', () => {
  it('allows up to the limit within the window, then blocks', () => {
    const limiter = createRateLimiter({ limit: 2, windowMs: 60_000 })
    expect(limiter.allow('1.2.3.4', 0)).toBe(true)
    expect(limiter.allow('1.2.3.4', 10)).toBe(true)
    expect(limiter.allow('1.2.3.4', 20)).toBe(false)
  })

  it('tracks each key separately', () => {
    const limiter = createRateLimiter({ limit: 1, windowMs: 60_000 })
    expect(limiter.allow('a', 0)).toBe(true)
    expect(limiter.allow('b', 0)).toBe(true)
    expect(limiter.allow('a', 0)).toBe(false)
  })

  it('allows again once the window has passed', () => {
    const limiter = createRateLimiter({ limit: 1, windowMs: 60_000 })
    expect(limiter.allow('a', 0)).toBe(true)
    expect(limiter.allow('a', 59_999)).toBe(false)
    expect(limiter.allow('a', 60_000)).toBe(true)
  })
})
