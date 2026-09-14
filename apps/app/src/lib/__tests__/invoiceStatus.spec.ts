import { describe, it, expect } from 'vitest'
import { canTransitionTo } from '../invoiceStatus'

describe('canTransitionTo', () => {
  it('allows draft to issued', () => {
    expect(canTransitionTo('draft', 'issued')).toBe(true)
  })

  it('allows draft to cancelled', () => {
    expect(canTransitionTo('draft', 'cancelled')).toBe(true)
  })

  it('allows issued to cancelled', () => {
    expect(canTransitionTo('issued', 'cancelled')).toBe(true)
  })

  it('does not allow issued back to draft', () => {
    expect(canTransitionTo('issued', 'draft')).toBe(false)
  })

  it('does not allow any transition out of cancelled', () => {
    expect(canTransitionTo('cancelled', 'draft')).toBe(false)
    expect(canTransitionTo('cancelled', 'issued')).toBe(false)
  })

  it('allows issued to sent (Phase 2d)', () => {
    expect(canTransitionTo('issued', 'sent')).toBe(true)
  })

  it('allows a sent invoice to still be cancelled', () => {
    expect(canTransitionTo('sent', 'cancelled')).toBe(true)
  })

  it('does not yet allow sent to paid (Phase 2e)', () => {
    expect(canTransitionTo('sent', 'paid')).toBe(false)
  })
})
