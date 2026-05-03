<template>
  <div class="app-container">
    <Sidebar 
      :activeSection="activeSection"
      :isCollapsed="isSidebarCollapsed"
      @navigate="handleNavigation"
      @toggle-collapse="toggleSidebar"
    />
    <main class="main-content">
      <Transition name="page" mode="out-in">
        <Repository v-if="activeSection === 'repository'" ref="repositoryRef" :key="'repo'" />
        <Chat v-else-if="activeSection === 'chat'" :key="'chat'" />
        <Settings v-else-if="activeSection === 'settings'" :key="'settings'" />
      </Transition>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Repository from './pages/Repository.vue'
import Chat from './pages/Chat.vue'
import Settings from './pages/Settings.vue'

const activeSection = ref('repository')
const isSidebarCollapsed = ref(false)
const repositoryRef = ref(null)

const handleNavigation = (section) => {
  activeSection.value = section
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}
</script>

<style scoped>
.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: var(--color-background);
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Page Transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.2s ease-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 900px) {
  .app-container {
    flex-direction: column;
  }
}
</style>
