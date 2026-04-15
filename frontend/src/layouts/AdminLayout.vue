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
import Sidebar from '../components/admin/Sidebar.vue'
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: calc(100vh - 64px); /* Subtract header height */
}

.admin-main {
  flex: 1;
  padding: 24px;
  background: #f9fafb;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
  }
  
  .admin-main {
    padding: 16px;
  }
}
</style>
