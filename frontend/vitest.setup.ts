import '@testing-library/jest-dom'

// jsdom doesn't implement IntersectionObserver; motion/react's whileInView requires it.
class MockIntersectionObserver {
  readonly root = null
  readonly rootMargin = ''
  readonly thresholds: ReadonlyArray<number> = []
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
  takeRecords = vi.fn(() => [] as IntersectionObserverEntry[])
}

vi.stubGlobal('IntersectionObserver', MockIntersectionObserver)
