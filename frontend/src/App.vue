<script setup lang="ts">
import { ref, onMounted } from 'vue'

const status = ref<string>('loading...')

onMounted(async () => {
  try {
    const res = await fetch('/health')
    const data = await res.json()
    status.value = data.status
  } catch (err) {
    status.value = 'error'
  }
})
</script>

<template>
  <main>
    <h1>Flask Healthcare</h1>
    <p>Backend status: {{ status }}</p>
  </main>
</template>
