<script setup lang="ts">
import { onMounted, onUnmounted, ref, useTemplateRef } from 'vue'

// `label`, not `ariaLabel` — see NotificationBell.vue's comment on why
// (Vue's TSX prop typing special-cases `aria-*` template bindings as
// fallthrough, never matching a same-named declared prop).
defineProps<{ initials: string; label: string }>()

const open = ref(false)
const rootRef = useTemplateRef<HTMLElement>('root')

function toggle() {
  open.value = !open.value
}

function close() {
  open.value = false
}

function onDocumentClick(event: MouseEvent) {
  if (rootRef.value && !rootRef.value.contains(event.target as Node)) close()
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') close()
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-dark text-sm font-semibold text-white hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
      :aria-label="label"
      aria-haspopup="menu"
      :aria-expanded="open"
      @click="toggle"
    >
      {{ initials }}
    </button>
    <div
      v-if="open"
      role="menu"
      tabindex="-1"
      class="absolute right-0 top-full z-20 mt-2 w-48 overflow-hidden rounded-xl border border-border bg-surface py-1 shadow-[0_10px_40px_-10px_rgba(10,10,10,0.20)]"
      @click="close"
      @keydown.esc="close"
    >
      <slot />
    </div>
  </div>
</template>
