<template>
  <div class="repository-page">
    <!-- Header -->
    <div class="repository-header">
      <div class="breadcrumb">
        <button class="breadcrumb-item" v-if="currentFolderId" @click="goToRoot">
          Root
        </button>
        <span v-if="currentFolderId" class="breadcrumb-sep">/</span>
        <span v-if="currentFolderId" class="breadcrumb-current">{{ currentFolderName }}</span>
      </div>

      <div class="header-actions">
        <button
          v-if="currentFolderId"
          class="btn btn-secondary"
          @click="goToRoot"
          title="Go back to root"
        >
          ← Back
        </button>
        <button
          class="btn btn-primary"
          @click="showCreateFolderInput"
          :disabled="creatingFolder"
        >
          + New Folder
        </button>
        <button
          class="btn btn-primary"
          @click="triggerFileUpload"
          :disabled="uploading"
        >
          📤 Upload File
        </button>
        <input
          ref="fileInput"
          type="file"
          multiple
          @change="handleFileSelect"
          style="display: none"
        />
      </div>
    </div>

    <!-- Create folder input -->
    <div v-if="showNewFolderInput" class="inline-input-container">
      <input
        ref="folderInput"
        v-model="newFolderName"
        type="text"
        placeholder="Folder name"
        @keyup.enter="createFolder"
        @keyup.escape="showNewFolderInput = false"
        autofocus
      />
      <button class="btn btn-sm btn-primary" @click="createFolder">✓</button>
      <button class="btn btn-sm btn-secondary" @click="showNewFolderInput = false">✕</button>
    </div>

    <!-- Upload progress -->
    <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
      <div class="progress-info">
        <span>{{ uploadingFileName }}</span>
        <span class="progress-percent">{{ uploadProgress }}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
    </div>

    <!-- File list -->
    <div class="file-list-container">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
      </div>

      <div v-if="!loading && items.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>This folder is empty</p>
      </div>

      <div v-else class="file-list">
        <div
          v-for="item in items"
          :key="item.id"
          class="file-item"
          :class="{ 'is-folder': item.type === 'folder' }"
          @click="handleItemClick(item)"
        >
          <div class="file-icon">{{ getFileIcon(item.mime_type, item.type === 'folder') }}</div>
          <div class="file-info">
            <div class="file-name">{{ item.name }}</div>
            <div v-if="indexingFiles.includes(item.id)" class="indexing-badge">
              ⏳ Indexing…
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { driveAPI } from '../services/api'
import { getFileIcon } from '../utils/icons'

const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadingFileName = ref('')
const creatingFolder = ref(false)
const items = ref([])
const currentFolderId = ref(null)
const currentFolderName = ref('')
const fileInput = ref(null)
const folderInput = ref(null)
const showNewFolderInput = ref(false)
const newFolderName = ref('')
const indexingFiles = ref([])

const loadItems = async () => {
  loading.value = true
  try {
    items.value = await driveAPI.listFolder(currentFolderId.value)
    // Simulate indexing state for newly uploaded files
    // In a real app, this would come from the backend
  } catch (error) {
    console.error('Error loading items:', error)
    alert('Error loading folder contents')
  } finally {
    loading.value = false
  }
}

const handleItemClick = (item) => {
  if (item.type === 'folder') {
    currentFolderId.value = item.id
    currentFolderName.value = item.name
  }
}

const goToRoot = () => {
  currentFolderId.value = null
  currentFolderName.value = ''
}

const showCreateFolderInput = () => {
  showNewFolderInput.value = true
  newFolderName.value = ''
  setTimeout(() => {
    folderInput.value?.focus()
  }, 0)
}

const createFolder = async () => {
  if (!newFolderName.value.trim()) return

  creatingFolder.value = true
  try {
    await driveAPI.createFolder(newFolderName.value, currentFolderId.value)
    showNewFolderInput.value = false
    newFolderName.value = ''
    await loadItems()
  } catch (error) {
    console.error('Error creating folder:', error)
    alert('Error creating folder')
  } finally {
    creatingFolder.value = false
  }
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files || [])
  if (files.length === 0) return

  uploading.value = true

  for (const file of files) {
    uploadingFileName.value = file.name
    uploadProgress.value = 0

    try {
      const result = await driveAPI.uploadFile(
        file,
        currentFolderId.value,
        (progress) => {
          uploadProgress.value = progress
        }
      )

      // Mark as indexing
      indexingFiles.value.push(result.id)
      
      // Simulate indexing completion after 2-3 seconds
      setTimeout(() => {
        indexingFiles.value = indexingFiles.value.filter(id => id !== result.id)
      }, 2000 + Math.random() * 1000)

      await loadItems()
    } catch (error) {
      console.error('Error uploading file:', error)
      alert(`Error uploading ${file.name}`)
    }
  }

  uploadProgress.value = 0
  uploadingFileName.value = ''
  uploading.value = false
  event.target.value = ''
}

onMounted(() => {
  loadItems()
})

watch(currentFolderId, () => {
  loadItems()
})
</script>

<style scoped>
.repository-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.repository-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-surface);
  flex-shrink: 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 14px;
  color: var(--color-text-secondary);
}

.breadcrumb-item {
  background: none;
  padding: 0;
  color: var(--color-primary);
  cursor: pointer;
  border: none;
  font-size: 14px;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-sep {
  margin: 0 4px;
}

.breadcrumb-current {
  color: var(--color-text-primary);
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.btn-secondary {
  background-color: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-border);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.inline-input-container {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.inline-input-container input {
  flex: 1;
  padding: 8px 12px;
}

.upload-progress {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.progress-percent {
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background-color: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-primary);
  transition: width 0.2s;
}

.file-list-container {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

.file-list {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.file-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: 4px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s;
}

.file-item:hover {
  background-color: var(--color-background);
  border-color: var(--color-primary);
}

.file-item.is-folder {
  cursor: pointer;
}

.file-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  word-break: break-word;
}

.indexing-badge {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
}

.empty-state p {
  font-size: 14px;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
</style>
