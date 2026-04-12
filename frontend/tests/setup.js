/**
 * Vitest setup file - Apple Design System compliant test environment
 */

// Mock Pinia store for testing (minimal setup)
import { createPinia, setActivePinia } from 'pinia'

beforeEach(() => {
  // Set up fresh pinia instance for each test
  setActivePinia(createPinia())
})

afterEach(() => {
  // Cleanup after each test
  vi.clearAllMocks()
})

// Mock window.matchMedia (iOS Safari compatibility)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated but still used in old code
    removeListener: vi.fn(), // deprecated but still used in old code
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})

// Mock scroll behavior (iOS smooth scrolling)
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: vi.fn()
})
