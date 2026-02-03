<template>
  <a 
    v-if="isExternal" 
    :href="to" 
    target="_blank" 
    rel="noopener" 
    class="text-link"
  >
    <slot />
  </a>
  <RouterLink 
    v-else 
    v-bind="$props" 
    custom
    v-slot="{ href, navigate }"
  >
    <a 
      :href="href" 
      @click="navigate" 
      target="_blank" 
      rel="noopener"
      class="text-link"
    >
      <slot />
    </a>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  // Import all props from RouterLink if you need strict typing, 
  // but 'to' is the most important one.
  to: {
    type: [String, Object],
    required: true
  }
})

const isExternal = computed(() => {
  return typeof props.to === 'string' && props.to.startsWith('http')
})
</script>