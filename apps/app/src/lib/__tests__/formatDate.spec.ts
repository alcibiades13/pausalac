import { describe, it, expect } from 'vitest'
import { formatDate, formatDateTime } from '../formatDate'

describe('formatDate', () => {
  it('formats an ISO date string using the sr-RS locale', () => {
    expect(formatDate('2026-01-01')).toBe('1. 1. 2026.')
  })

  it('formats an ISO datetime string using only the date part', () => {
    expect(formatDate('2026-10-01T00:00:00Z')).toBe('1. 10. 2026.')
  })

  it('returns an em dash for null', () => {
    expect(formatDate(null)).toBe('—')
  })

  it('returns an em dash for undefined', () => {
    expect(formatDate(undefined)).toBe('—')
  })

  it('returns an em dash for an empty string', () => {
    expect(formatDate('')).toBe('—')
  })
})

describe('formatDateTime', () => {
  it('formats an ISO datetime string using the sr-RS locale', () => {
    expect(formatDateTime('2026-01-01T12:30:00Z')).toContain('2026.')
  })

  it('returns an em dash for null', () => {
    expect(formatDateTime(null)).toBe('—')
  })

  it('returns an em dash for undefined', () => {
    expect(formatDateTime(undefined)).toBe('—')
  })

  it('returns an em dash for an empty string', () => {
    expect(formatDateTime('')).toBe('—')
  })
})
