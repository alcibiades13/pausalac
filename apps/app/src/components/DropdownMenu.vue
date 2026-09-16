<script setup lang="ts">
import { onMounted, onUnmounted, ref, useTemplateRef } from 'vue'

/**
 * Generalized from a user-avatar-only "UserMenu" once a second real
 * consumer showed up (the global quick-create "+" button) — the
 * open/close/outside-click/Escape mechanics were identical, only the
 * trigger button's own look differs, so the trigger is now a slot
 * instead of a hardcoded avatar circle. `menuWidthClass` exists because
 * the two current consumers need genuinely different widths (a short
 * "Podešavanja"/"Odjavi se" list vs. longer quick-create action labels).
 */
withDefaults(defineProps<{ label: string; menuWidthClass?: string; triggerClass?: string }>(), {
  menuWidthClass: 'w-48',
  triggerClass: '',
})

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
      :class="triggerClass"
      :aria-label="label"
      aria-haspopup="menu"
      :aria-expanded="open"
      @click="toggle"
    >
      <slot name="trigger" :open="open" />
    </button>
    <div
      v-if="open"
      role="menu"
      tabindex="-1"
      :class="[
        'absolute right-0 top-full z-20 mt-2 overflow-hidden rounded-xl border border-border bg-surface py-1 shadow-[0_10px_40px_-10px_rgba(10,10,10,0.20)]',
        menuWidthClass,
      ]"
      @click="close"
      @keydown.esc="close"
    >
      <slot />
    </div>
  </div>
</template>
