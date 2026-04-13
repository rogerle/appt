<script setup lang="ts">
interface TimeSlot {
  id: number
  start_time: string
  end_time: string
  duration_minutes: number
  available: boolean
  booked_count?: number
}

const props = defineProps<{
  slots: TimeSlot[]
  selectedSlot?: { start: string; end: string } | null
}>()

const emit = defineEmits<{
  select: [slot: TimeSlot]
}>()

function handleSelect(slot: TimeSlot) {
  if (!slot.available) return
  emit('select', slot)
}
</script>

<template>
  <div class="time-slot-picker">
    <!-- Grid of time slots -->
    <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
      <button
        v-for="slot in slots"
        :key="slot.id"
        @click="handleSelect(slot)"
        :disabled="!slot.available"
        class="relative p-3 rounded-lg border-2 transition-all duration-200 text-sm min-h-[70px] flex flex-col items-center justify-center"
        :class="[
          selectedSlot?.start === slot.start_time 
            ? 'border-accent-dark bg-accent-light text-accent-dark shadow-md scale-105' 
            : 'border-primary-200 hover:border-accent-green hover:bg-primary-50',
          !slot.available ? 'opacity-40 cursor-not-allowed bg-gray-100' : 'cursor-pointer'
        ]"
      >
        <!-- Time -->
        <div class="font-bold text-base">{{ slot.start_time }}</div>
        
        <!-- Duration -->
        <div class="text-xs text-gray-600 mt-1">
          {{ slot.duration_minutes }}分钟
        </div>

        <!-- Booked count indicator -->
        <div v-if="slot.booked_count !== undefined" class="absolute top-1 right-1">
          <span 
            class="px-1.5 py-0.5 rounded-full text-xs font-medium"
            :class="[
              slot.available && slot.booked_count > 0 
                ? 'bg-yellow-100 text-yellow-700' 
                : 'bg-red-100 text-red-700',
              !slot.available ? 'opacity-60' : ''
            ]"
          >
            {{ slot.booked_count }}人已约
          </span>
        </div>

        <!-- Unavailable badge -->
        <div v-if="!slot.available" class="absolute inset-0 flex items-center justify-center">
          <span class="text-lg opacity-50">✗</span>
        </div>
      </button>
    </div>

    <!-- Legend -->
    <div class="mt-6 flex flex-wrap gap-4 text-sm justify-center">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 rounded-lg border-2 border-accent-dark bg-accent-light"></div>
        <span class="text-gray-700">已选择</span>
      </div>

      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 rounded-lg border-2 border-primary-200 bg-white"></div>
        <span class="text-gray-700">可选</span>
      </div>

      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 rounded-lg border-2 border-gray-300 bg-gray-100 opacity-40"></div>
        <span class="text-gray-700">已满</span>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="slots.length === 0" class="text-center py-12">
      <p class="text-4xl mb-3">🕐</p>
      <p class="text-gray-500">暂无可预约时段</p>
    </div>
  </div>
</template>

<style scoped></style>
