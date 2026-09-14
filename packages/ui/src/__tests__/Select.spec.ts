import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Select from '../Select.vue'

describe('Select', () => {
  it('renders options and reflects the model value', () => {
    const wrapper = mount(Select, {
      props: {
        label: 'Vrsta',
        modelValue: 'service',
        options: [
          { value: 'service', label: 'Usluga' },
          { value: 'product', label: 'Proizvod' },
        ],
      },
    })
    expect(wrapper.text()).toContain('Vrsta')
    expect(wrapper.text()).toContain('Usluga')
    expect(wrapper.text()).toContain('Proizvod')
    expect((wrapper.find('select').element as HTMLSelectElement).value).toBe('service')
  })

  it('emits update:modelValue when changed', async () => {
    const wrapper = mount(Select, {
      props: {
        modelValue: 'service',
        options: [
          { value: 'service', label: 'Usluga' },
          { value: 'product', label: 'Proizvod' },
        ],
      },
    })
    await wrapper.find('select').setValue('product')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['product'])
  })
})
