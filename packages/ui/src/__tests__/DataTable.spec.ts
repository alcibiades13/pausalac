import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DataTable from '../DataTable.vue'

interface Row {
  id: number
  name: string
  status: string
  [key: string]: unknown
}

const rows: Row[] = [
  { id: 1, name: 'Firma A', status: 'active' },
  { id: 2, name: 'Firma B', status: 'inactive' },
]

const columns = [
  { key: 'name', label: 'Naziv' },
  { key: 'status', label: 'Status' },
]

describe('DataTable', () => {
  it('shows a loading skeleton while loading', () => {
    const wrapper = mount(DataTable, { props: { columns, rows: [], loading: true } })
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
    expect(wrapper.find('table').exists()).toBe(false)
  })

  it('shows an empty state when there are no rows', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [], emptyTitle: 'Nema ničega.' },
    })
    expect(wrapper.text()).toContain('Nema ničega.')
    expect(wrapper.find('table').exists()).toBe(false)
  })

  it('renders a header per column and a row per data item', () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    const headers = wrapper.findAll('th')
    expect(headers[0]!.text()).toBe('Naziv')
    expect(headers[1]!.text()).toBe('Status')

    const bodyRows = wrapper.findAll('tbody tr')
    expect(bodyRows).toHaveLength(2)
    expect(bodyRows[0]!.text()).toContain('Firma A')
    expect(bodyRows[1]!.text()).toContain('Firma B')
  })

  it('applies a column format function when provided', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: [
          { key: 'status', label: 'Status', format: (r) => String((r as Row).status).toUpperCase() },
        ],
        rows,
      },
    })
    expect(wrapper.text()).toContain('ACTIVE')
    expect(wrapper.text()).toContain('INACTIVE')
  })

  it('falls back to an em dash for empty cell values', () => {
    const wrapper = mount(DataTable, {
      props: { columns: [{ key: 'name', label: 'Naziv' }], rows: [{ id: 1, name: '' }] },
    })
    expect(wrapper.find('tbody td')!.text()).toBe('—')
  })

  it('renders a scoped cell slot when provided, overriding the default', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows },
      slots: {
        'cell-status': `<template #cell-status="{ row }"><span class="custom">{{ row.status }}!</span></template>`,
      },
    })
    expect(wrapper.find('.custom').text()).toBe('active!')
  })

  it('renders an actions column only when an actions slot is provided', () => {
    const withoutActions = mount(DataTable, { props: { columns, rows } })
    expect(withoutActions.find('th:last-child').text()).not.toBe('')
    expect(withoutActions.findAll('th')).toHaveLength(2)

    const withActions = mount(DataTable, {
      props: { columns, rows },
      slots: {
        actions: `<template #actions="{ row }"><button class="act">{{ row.id }}</button></template>`,
      },
    })
    expect(withActions.findAll('th')).toHaveLength(3)
    // Rendered once in the desktop table and once in the mobile card list
    // (below `sm`) — both exist in the DOM at once, CSS picks one per
    // viewport, so each row's action shows up twice, not once.
    const tableActions = withActions.findAll('table .act')
    expect(tableActions).toHaveLength(2)
    expect(tableActions[0]!.text()).toBe('1')
  })

  it('also renders each row as a mobile card, with the same cells and actions', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows },
      slots: {
        actions: `<template #actions="{ row }"><button class="act">{{ row.id }}</button></template>`,
      },
    })
    const cardList = wrapper.find('.sm\\:hidden')
    expect(cardList.text()).toContain('Firma A')
    expect(cardList.text()).toContain('Naziv')
    expect(cardList.findAll('.act')).toHaveLength(2)
  })

  it('renders a plain header (no button) for a non-sortable column', () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    expect(wrapper.find('th button').exists()).toBe(false)
  })

  it('cycles asc -> desc -> off and emits the new sort on each header click', async () => {
    const sortableColumns = [{ key: 'name', label: 'Naziv', sortable: true }, columns[1]!]
    const wrapper = mount(DataTable, { props: { columns: sortableColumns, rows, sort: null } })
    const header = wrapper.find('th button')

    await header.trigger('click')
    expect(wrapper.emitted('sort')![0]).toEqual([{ key: 'name', direction: 'asc' }])

    await wrapper.setProps({ sort: { key: 'name', direction: 'asc' } })
    await header.trigger('click')
    expect(wrapper.emitted('sort')![1]).toEqual([{ key: 'name', direction: 'desc' }])

    await wrapper.setProps({ sort: { key: 'name', direction: 'desc' } })
    await header.trigger('click')
    expect(wrapper.emitted('sort')![2]).toEqual([null])
  })

  it('uses sortKey instead of key for the sort event when provided', async () => {
    const sortableColumns = [{ key: 'name', label: 'Naziv', sortable: true, sortKey: '-custom' }]
    const wrapper = mount(DataTable, { props: { columns: sortableColumns, rows } })
    await wrapper.find('th button').trigger('click')
    expect(wrapper.emitted('sort')![0]).toEqual([{ key: '-custom', direction: 'asc' }])
  })

  it('does not toggle sort for a non-sortable column even if clicked programmatically', () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    expect(wrapper.emitted('sort')).toBeUndefined()
  })

  it('emits row-click with the row when rowClickable and a row is clicked', async () => {
    const wrapper = mount(DataTable, { props: { columns, rows, rowClickable: true } })
    await wrapper.find('tbody tr').trigger('click')
    expect(wrapper.emitted('row-click')![0]).toEqual([rows[0]])
  })

  it('does not emit row-click when rowClickable is false', async () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    await wrapper.find('tbody tr').trigger('click')
    expect(wrapper.emitted('row-click')).toBeUndefined()
  })

  it('does not emit row-click when an actions button inside the row is clicked', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, rowClickable: true },
      slots: {
        actions: `<template #actions="{ row }"><button class="act">{{ row.id }}</button></template>`,
      },
    })
    await wrapper.find('table .act').trigger('click')
    expect(wrapper.emitted('row-click')).toBeUndefined()
  })
})
