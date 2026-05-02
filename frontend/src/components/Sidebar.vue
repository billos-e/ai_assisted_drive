<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo">🚀 AI Drive</div>
    </div>

    <nav class="sidebar-nav">
      <button
        class="nav-item"
        :class="{ active: activeSection === 'repository' }"
        @click="$emit('navigate', 'repository')"
        title="Repository"
      >
        <span class="nav-icon">📁</span>
        <span class="nav-label">Repository</span>
      </button>

      <button
        class="nav-item"
        :class="{ active: activeSection === 'chat' }"
        @click="$emit('navigate', 'chat')"
        title="Chat"
      >
        <span class="nav-icon">💬</span>
        <span class="nav-label">Chat</span>
      </button>

      <button
        class="nav-item"
        :class="{ active: activeSection === 'settings' }"
        @click="$emit('navigate', 'settings')"
        title="Settings"
      >
        <span class="nav-icon">⚙️</span>
        <span class="nav-label">Settings</span>
      </button>
    </nav>
  </aside>
</template>

<script setup>
defineProps({
  activeSection: {
    type: String,
    default: 'repository'
  }
})

defineEmits(['navigate'])
</script>

<style scoped>
.sidebar {
  width: 200px;
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: var(--spacing-lg) 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 0 var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--spacing-md);
}

.logo {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: 0 var(--spacing-md);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: 4px;
  background-color: transparent;
  color: var(--color-text-secondary);
  transition: all 0.2s;
  text-align: left;
  font-size: 14px;
  border: none;
}

.nav-item:hover {
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.nav-item.active {
  background-color: var(--color-primary);
  color: white;
  font-weight: 500;
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
}
</style>
