<template>
  <aside class="sidebar glass">
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">
          <Sparkles :size="20" />
        </div>
        <span class="logo-text">AI Drive</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <button
        class="nav-item"
        :class="{ active: activeSection === 'repository' }"
        @click="$emit('navigate', 'repository')"
        title="Repository"
      >
        <Folder :size="20" class="nav-icon" />
        <span class="nav-label">Repository</span>
      </button>

      <button
        class="nav-item"
        :class="{ active: activeSection === 'chat' }"
        @click="$emit('navigate', 'chat')"
        title="Chat"
      >
        <MessageSquare :size="20" class="nav-icon" />
        <span class="nav-label">Chat</span>
      </button>

      <button
        class="nav-item"
        :class="{ active: activeSection === 'settings' }"
        @click="$emit('navigate', 'settings')"
        title="Settings"
      >
        <Settings2 :size="20" class="nav-icon" />
        <span class="nav-label">Settings</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info">
        <div class="avatar">JS</div>
        <div class="user-details">
          <p class="user-name">User Account</p>
          <p class="user-status">Online</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { Folder, MessageSquare, Settings2, Sparkles } from 'lucide-vue-next'

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
  width: 240px;
  flex: 0 0 240px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-xl) 0;
  border-right: 1px solid var(--color-border);
  position: relative;
  z-index: 20;
}

.sidebar-header {
  padding: 0 var(--spacing-lg) var(--spacing-xl);
  margin-bottom: var(--spacing-md);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

.logo-text {
  font-family: 'Outfit', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 var(--spacing-md);
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px var(--spacing-md);
  border-radius: var(--radius-md);
  background-color: transparent;
  color: var(--color-text-secondary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  font-size: 15px;
  font-weight: 500;
  border: 1px solid transparent;
}

.nav-item:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text-primary);
  transform: translateX(4px);
}

.nav-item.active {
  background: rgba(79, 70, 229, 0.05);
  color: var(--color-primary);
  border-color: transparent;
  box-shadow: none;
  font-weight: 600;
}

.nav-item.active .nav-icon {
  filter: none;
  color: var(--color-primary);
}

.nav-icon {
  flex-shrink: 0;
  transition: all 0.3s;
}

.sidebar-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 32px;
  height: 32px;
  background: var(--color-surface-hover);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.user-status {
  font-size: 11px;
  color: var(--color-success);
}

@media (max-width: 900px) {
  .sidebar {
    width: 100%;
    flex: 0 0 auto;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
    padding: var(--spacing-md) 0;
  }

  .sidebar-header, .sidebar-footer {
    display: none;
  }

  .sidebar-nav {
    flex-direction: row;
    justify-content: center;
  }

  .nav-item {
    padding: var(--spacing-sm);
  }

  .nav-label {
    display: none;
  }
}
</style>
