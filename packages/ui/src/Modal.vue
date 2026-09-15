<script setup lang="ts">
import { ref, toRef, useId } from 'vue'
import { useDialogA11y } from './composables/useDialogA11y'

const props = defineProps<{
  open: boolean
  title?: string
}>()

const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const containerRef = ref<HTMLElement | null>(null)
const openRef = toRef(props, 'open')
const titleId = useId()

function close() {
  emit('update:open', false)
}

useDialogA11y(containerRef, openRef, close)
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-40 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-navy/40" @click="close" />
      <div
        ref="containerRef"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="title ? titleId : undefined"
        tabindex="-1"
        class="relative flex w-full max-w-md flex-col gap-4 rounded-2xl bg-surface p-6 shadow-[0_1px_2px_rgba(23,32,51,0.04),0_8px_24px_-8px_rgba(23,32,51,0.10)] outline-none"
      >
        <div v-if="title || $slots.header" class="flex items-center justify-between gap-4">
          <h2 v-if="title" :id="titleId" class="text-base font-semibold text-navy">{{ title }}</h2>
          <slot name="header" />
          <button
            type="button"
            class="ml-auto flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-text-secondary hover:bg-background focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            aria-label="Zatvori"
            @click="close"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>
        <div>
          <slot />
        </div>
        <div v-if="$slots.footer" class="flex justify-end gap-3">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
