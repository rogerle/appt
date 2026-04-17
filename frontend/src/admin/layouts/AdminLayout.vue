<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content Area -->
    <main class="admin-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import Sidebar from '../../components/admin/Sidebar.vue'
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh; /* Full viewport height */
}

.admin-main {
  padding: 24px;
  background: #f9fafb;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin-layout {
    grid-template-columns: 1fr; /* Single column on mobile */
  }
  
  .admin-main {
    padding: 16px;
  }
}
</style>
