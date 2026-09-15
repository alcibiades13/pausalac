import { nextTick, onBeforeUnmount, watch, type Ref } from 'vue'

/**
 * Shared overlay accessibility for Modal/Drawer (master prompt §55
 * "keyboard navigation"): traps Tab/Shift+Tab inside the dialog while
 * open, closes on Escape, moves focus into the dialog on open, and
 * restores it to whatever was focused before on close. No dependency on
 * either component's own markup beyond a container ref and an open flag.
 */
export function useDialogA11y(
  containerRef: Ref<HTMLElement | null>,
  isOpen: Ref<boolean>,
  onClose: () => void,
) {
  let previouslyFocused: HTMLElement | null = null

  function focusableElements(): HTMLElement[] {
    if (!containerRef.value) return []
    return Array.from(
      containerRef.value.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ),
    )
  }

  function onKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      event.preventDefault()
      onClose()
      return
    }
    if (event.key !== 'Tab') return
    const elements = focusableElements()
    if (elements.length === 0) return
    const first = elements[0]!
    const last = elements[elements.length - 1]!
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first.focus()
    }
  }

  watch(isOpen, async (open) => {
    if (open) {
      previouslyFocused = document.activeElement as HTMLElement | null
      await nextTick()
      const elements = focusableElements()
      ;(elements[0] ?? containerRef.value)?.focus()
      window.addEventListener('keydown', onKeydown)
    } else {
      window.removeEventListener('keydown', onKeydown)
      previouslyFocused?.focus()
      previouslyFocused = null
    }
  })

  onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
}
