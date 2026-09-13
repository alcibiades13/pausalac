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

  it('does not yet allow issued to sent (Phase 2d)', () => {
    expect(canTransitionTo('issued', 'sent')).toBe(false)
  })
})
