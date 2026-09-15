<script setup lang="ts">
import { useId } from 'vue'

const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    type?: string
    placeholder?: string
    error?: string
    hint?: string
    required?: boolean
    disabled?: boolean
    autocomplete?: string
  }>(),
  {
    type: 'text',
    required: false,
    disabled: false,
  },
)

const inputId = useId()

/**
 * Manual value/input wiring instead of `v-model` — Vue 3.4+ auto-casts
 * `v-model` on `type="number"`/`"range"` inputs to a JS number, silently
 * breaking this app's Decimal-as-string convention for every money/
 * numeric field (found via a real failing test, not assumed). This
 * keeps the model a string for every `type`, matching what `defineModel`
 * is actually typed as.
 */
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
    <input
      :id="inputId"
      :value="model"
      @input="onInput"
      :type="type"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :autocomplete="autocomplete"
      :aria-invalid="!!error"
      :aria-describedby="error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined"
      :class="[
        'rounded-lg border bg-surface px-3 py-2 text-sm text-navy placeholder:text-text-secondary',
        'transition-shadow focus-visible:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40',
        'disabled:cursor-not-allowed disabled:bg-background disabled:opacity-60',
        error ? 'border-danger' : 'border-border',
      ]"
    />
    <p v-if="error" :id="`${inputId}-error`" class="text-sm text-danger">{{ error }}</p>
    <p v-else-if="hint" :id="`${inputId}-hint`" class="text-sm text-text-secondary">{{ hint }}</p>
  </div>
</template>
