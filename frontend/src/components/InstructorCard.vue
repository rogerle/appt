<script setup lang="ts">
import { computed } from 'vue'

interface Instructor {
  id: number
  name: string
  avatar_url?: string
  bio?: string
  specialties?: string[]
}

const props = defineProps<{
  instructor: Instructor
  selected?: boolean
}>()

const emit = defineEmits<{
  click: []
}>()

// Generate initials from name if no avatar
const initials = computed(() => {
  const names = props.instructor.name.split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

// Avatar display (initials if no image)
const avatarDisplay = computed(() => {
  return props.instructor.avatar_url || initials.value
})
</script>

<template>
  <div 
    @click="$emit('click')"
    class="card cursor-pointer transition-all duration-200 transform hover:scale-[1.02] hover:shadow-lg border-2"
    :class="selected ? 'border-accent-dark bg-accent-light' : 'border-transparent'"
  >
    <div class="flex items-center space-x-4">
      <!-- Avatar -->
      <div 
        class="w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl"
        :class="selected ? 'bg-accent-dark' : 'bg-primary-400'"
      >
        {{ avatarDisplay }}
      </div>

      <!-- Info -->
      <div class="flex-grow">
        <h3 class="font-bold text-lg text-gray-800">{{ instructor.name }}</h3>
        
        <p v-if="instructor.bio" class="text-sm text-gray-600 mt-1 line-clamp-2">
          {{ instructor.bio }}
        </p>

        <!-- Specialties Tags -->
        <div v-if="instructor.specialties && instructor.specialties.length > 0" class="flex flex-wrap gap-1 mt-2">
          <span 
            v-for="(tag, index) in instructor.specialties.slice(0, 3)" 
            :key="index"
            class="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium"
          >
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- Selection Indicator -->
      <div 
        v-if="selected"
        class="w-8 h-8 rounded-full bg-accent-dark flex items-center justify-center text-white animate-scale-in"
      >
        ✓
      </div>
    </div>
  </div>
</template>

<style scoped></style>
