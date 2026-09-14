import { describe, it, expect } from 'vitest'
import { canTransitionTo, isPayable } from '../invoiceStatus'

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

  it('does not transition sent directly to paid — payment recording resolves that, not TRANSITIONS', () => {
    expect(canTransitionTo('sent', 'paid')).toBe(false)
  })

  it('allows an overdue invoice to still be cancelled', () => {
    expect(canTransitionTo('overdue', 'cancelled')).toBe(true)
  })

  it('does not allow cancelling a partially paid or fully paid invoice', () => {
    expect(canTransitionTo('partially_paid', 'cancelled')).toBe(false)
    expect(canTransitionTo('paid', 'cancelled')).toBe(false)
  })
})

describe('isPayable', () => {
  it('is true for issued, sent, partially_paid, and overdue', () => {
    expect(isPayable('issued')).toBe(true)
    expect(isPayable('sent')).toBe(true)
    expect(isPayable('partially_paid')).toBe(true)
    expect(isPayable('overdue')).toBe(true)
  })

  it('is false for draft, paid, and cancelled', () => {
    expect(isPayable('draft')).toBe(false)
    expect(isPayable('paid')).toBe(false)
    expect(isPayable('cancelled')).toBe(false)
  })
})
