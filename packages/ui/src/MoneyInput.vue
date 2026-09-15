<script setup lang="ts">
import { useId } from 'vue'

const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    currency?: string
    error?: string
    hint?: string
    required?: boolean
    disabled?: boolean
  }>(),
  {
    currency: 'RSD',
    required: false,
    disabled: false,
  },
)

const inputId = useId()

// Manual value/input wiring, not `v-model` — Vue 3.4+ auto-casts
// `v-model` on `type="number"` to a JS number, breaking this app's
// Decimal-as-string convention for every money value (see Input.vue's
// identical fix for the same, real, test-caught bug).
function onInput(event: Event) {
  model.value = (event.target as HTMLInputElement).value
}
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" :for="inputId" class="text-sm font-medium text-navy">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <div class="relative">
      <input
        :id="inputId"
        :value="model"
        @input="onInput"
        type="number"
        inputmode="decimal"
        step="0.01"
        min="0"
        :required="required"
        :disabled="disabled"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined"
        :class="[
          'w-full rounded-lg border bg-surface px-3 py-2 pr-14 text-sm text-navy',
          'transition-shadow focus-visible:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40',
          'disabled:cursor-not-allowed disabled:bg-background disabled:opacity-60',
          error ? 'border-danger' : 'border-border',
        ]"
      />
      <span
        class="pointer-events-none absolute inset-y-0 right-3 flex items-center text-sm text-text-secondary"
      >
        {{ currency }}
      </span>
    </div>
    <p v-if="error" :id="`${inputId}-error`" class="text-sm text-danger">{{ error }}</p>
    <p v-else-if="hint" :id="`${inputId}-hint`" class="text-sm text-text-secondary">{{ hint }}</p>
  </div>
</template>
