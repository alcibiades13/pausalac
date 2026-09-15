import { describe, it, expect, vi, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { defineComponent, reactive } from 'vue'
import { createRouter, createMemoryHistory } from 'vue-router'
import { useUnsavedChangesGuard } from '../useUnsavedChangesGuard'

const HostComponent = defineComponent({
  setup() {
    const form = reactive({ name: '' })
    const { markClean, isDirty } = useUnsavedChangesGuard(() => form)
    return { form, markClean, isDirty }
  },
  template: '<div>{{ form.name }}</div>',
})

const RootComponent = defineComponent({ template: '<router-view />' })

let activeWrapper: VueWrapper | null = null

async function mountHost() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: HostComponent },
      { path: '/other', name: 'other', component: { template: '<div>other</div>' } },
    ],
  })
  await router.push('/')
  await router.isReady()
  const wrapper = mount(RootComponent, { global: { plugins: [router] } })
  activeWrapper = wrapper
  const host = wrapper.findComponent(HostComponent)
  return { host, router }
}

describe('useUnsavedChangesGuard', () => {
  afterEach(() => {
    activeWrapper?.unmount()
    activeWrapper = null
    vi.restoreAllMocks()
  })

  it('is not dirty before markClean has ever been called', async () => {
    const { host } = await mountHost()
    expect(host.vm.isDirty()).toBe(false)
  })

  it('is not dirty right after markClean, and becomes dirty once the snapshot changes', async () => {
    const { host } = await mountHost()
    host.vm.markClean()
    expect(host.vm.isDirty()).toBe(false)

    host.vm.form.name = 'Izmenjeno'
    await flushPromises()
    expect(host.vm.isDirty()).toBe(true)
  })

  it('markClean again after an edit resets the dirty baseline', async () => {
    const { host } = await mountHost()
    host.vm.markClean()
    host.vm.form.name = 'Izmenjeno'
    expect(host.vm.isDirty()).toBe(true)

    host.vm.markClean()
    expect(host.vm.isDirty()).toBe(false)
  })

  describe('route navigation guard', () => {
    it('allows navigation without prompting when the form is clean', async () => {
      const { host, router } = await mountHost()
      host.vm.markClean()
      const confirmSpy = vi.spyOn(window, 'confirm')

      await router.push('/other')
      await flushPromises()

      expect(confirmSpy).not.toHaveBeenCalled()
      expect(router.currentRoute.value.name).toBe('other')
    })

    it('prompts and blocks navigation when dirty and the user cancels', async () => {
      const { host, router } = await mountHost()
      host.vm.markClean()
      host.vm.form.name = 'Izmenjeno'
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)

      await router.push('/other')
      await flushPromises()

      expect(confirmSpy).toHaveBeenCalled()
      expect(router.currentRoute.value.name).toBe('home')
    })

    it('prompts and allows navigation when dirty and the user confirms', async () => {
      const { host, router } = await mountHost()
      host.vm.markClean()
      host.vm.form.name = 'Izmenjeno'
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)

      await router.push('/other')
      await flushPromises()

      expect(confirmSpy).toHaveBeenCalled()
      expect(router.currentRoute.value.name).toBe('other')
    })
  })

  describe('beforeunload', () => {
    it('does not prevent unload when the form is clean', async () => {
      const { host } = await mountHost()
      host.vm.markClean()

      const event = new Event('beforeunload', { cancelable: true })
      window.dispatchEvent(event)

      expect(event.defaultPrevented).toBe(false)
    })

    it('prevents unload when the form is dirty', async () => {
      const { host } = await mountHost()
      host.vm.markClean()
      host.vm.form.name = 'Izmenjeno'

      const event = new Event('beforeunload', { cancelable: true })
      window.dispatchEvent(event)

      expect(event.defaultPrevented).toBe(true)
    })

    it('stops listening once the component unmounts', async () => {
      const { host } = await mountHost()
      host.vm.markClean()
      host.vm.form.name = 'Izmenjeno'
      activeWrapper?.unmount()
      activeWrapper = null

      const event = new Event('beforeunload', { cancelable: true })
      window.dispatchEvent(event)

      expect(event.defaultPrevented).toBe(false)
    })
  })
})
