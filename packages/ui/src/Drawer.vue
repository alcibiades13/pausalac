<script setup lang="ts">
import { ref, toRef } from 'vue'
import { useDialogA11y } from './composables/useDialogA11y'

const props = withDefaults(
  defineProps<{
    open: boolean
    label: string
    containerClass?: string
  }>(),
  {
    containerClass: '',
  },
)

const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const containerRef = ref<HTMLElement | null>(null)
const openRef = toRef(props, 'open')

function close() {
  emit('update:open', false)
}

useDialogA11y(containerRef, openRef, close)
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-30" :class="containerClass">
      <div class="absolute inset-0 bg-navy/40" @click="close" />
      <div
        ref="containerRef"
        role="dialog"
        aria-modal="true"
        :aria-label="label"
        tabindex="-1"
        class="absolute inset-x-0 bottom-0 flex flex-col gap-1 rounded-t-2xl bg-surface p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-[0_-4px_24px_rgba(23,32,51,0.12)] outline-none"
      >
        <slot />
      </div>
    </div>
  </Teleport>
</template>
