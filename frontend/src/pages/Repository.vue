<template>
  <div class="repository-page">
    <!-- Header -->
    <div class="repository-header glass">
      <div class="header-left">
        <h1 class="page-title">Files</h1>
        <div class="breadcrumb">
          <button class="breadcrumb-item" v-if="currentFolderId" @click="goToRoot">
            Root
          </button>
          <span v-if="currentFolderId" class="breadcrumb-sep">/</span>
          <span v-if="currentFolderId" class="breadcrumb-current">{{ currentFolderName }}</span>
        </div>
      </div>

      <div class="header-actions">
        <button
          v-if="currentFolderId"
          class="btn btn-secondary"
          @click="goToRoot"
          title="Go back to root"
        >
          <ArrowLeft :size="16" />
          <span>Back</span>
        </button>
        <button
          class="btn btn-secondary"
          @click="showCreateFolderInput"
          :disabled="creatingFolder"
        >
          <FolderPlus :size="16" />
          <span>New Folder</span>
        </button>
        <button
          class="btn btn-primary"
          @click="triggerFileUpload"
          :disabled="uploading"
        >
          <Upload :size="16" />
          <span>Upload File</span>
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
    <Transition name="slide-down">
      <div v-if="showNewFolderInput" class="inline-input-container glass">
        <div class="input-wrapper">
          <Folder :size="18" class="input-icon" />
          <input
            ref="folderInput"
            v-model="newFolderName"
            type="text"
            placeholder="Name your new folder..."
            @keyup.enter="createFolder"
            @keyup.escape="showNewFolderInput = false"
            autofocus
          />
        </div>
        <div class="input-actions">
          <button class="btn-icon success" @click="createFolder" title="Confirm">
            <Check :size="18" />
          </button>
          <button class="btn-icon danger" @click="showNewFolderInput = false" title="Cancel">
            <X :size="18" />
          </button>
        </div>
      </div>
    </Transition>

    <!-- Upload progress -->
    <Transition name="fade">
      <div v-if="uploading" class="upload-progress glass">
        <div class="progress-info">
          <div class="file-name-container">
            <Upload :size="14" class="upload-icon" />
            <span class="file-name-text">{{ uploadingFileName }}</span>
          </div>
          <span class="progress-percent">{{ uploadProgress }}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
      </div>
    </Transition>

    <!-- File list -->
    <div class="file-list-container">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
      </div>

      <div v-if="!loading && items.length === 0" class="empty-state">
        <div class="empty-illustration">
          <Inbox :size="64" class="empty-icon" />
        </div>
        <h3>No files found</h3>
        <p>Upload your first file to get started with AI Assisted Drive</p>
      </div>

      <div v-else class="file-list">
        <TransitionGroup name="list">
          <div
            v-for="item in items"
            :key="item.id"
            class="file-item"
            :class="{ 'is-folder': item.type === 'folder' }"
            @click="handleItemClick(item)"
          >
            <div class="file-icon-wrapper" :class="item.type">
              <component :is="getFileIconComponent(item.mime_type, item.type === 'folder')" :size="22" />
            </div>
            
            <div class="file-content">
              <div class="file-main">
                <span class="file-name">{{ item.name }}</span>
                <div v-if="indexingFiles.includes(item.id)" class="badge indexing">
                  <LoaderCircle :size="12" class="spin" />
                  <span>Indexing</span>
                </div>
              </div>
              <div class="file-meta">
                <span v-if="item.type === 'file'">{{ formatSize(item.size) }}</span>
                <span v-else>Folder</span>
                <span class="dot">•</span>
                <span>{{ formatDate(item.modified_time) }}</span>
              </div>
            </div>

            <div class="file-actions" @click.stop>
              <button
                class="btn-icon danger"
                :title="`Delete ${item.name}`"
                @click="confirmDeleteItem(item)"
              >
                <Trash2 :size="18" />
              </button>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ArrowLeft, FolderPlus, Inbox, LoaderCircle, Trash2, Upload, Folder, Check, X } from 'lucide-vue-next'
import { driveAPI } from '../services/api'
import { getFileIconComponent } from '../utils/icons'

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
  } catch (error) {
    console.error('Error loading items:', error)
  } finally {
    loading.value = false
  }
}

const handleItemClick = (item) => {
  if (item.type === 'folder') {
    currentFolderId.value = item.id
    currentFolderName.value = item.name
    return
  }
  openItem(item)
}

const openItem = async (item) => {
  if (item.type !== 'file') return
  try {
    const { url } = await driveAPI.openFile(item.id)
    window.open(url, '_blank', 'noopener,noreferrer')
  } catch (error) {
    console.error('Error opening item:', error)
  }
}

const confirmDeleteItem = async (item) => {
  if (!window.confirm(`Are you sure you want to delete ${item.name}?`)) return
  try {
    await driveAPI.deleteItem(item.id)
    indexingFiles.value = indexingFiles.value.filter(id => id !== item.id)
    await loadItems()
  } catch (error) {
    console.error('Error deleting item:', error)
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
      indexingFiles.value.push(result.id)
      setTimeout(() => {
        indexingFiles.value = indexingFiles.value.filter(id => id !== result.id)
      }, 3000)
      await loadItems()
    } catch (error) {
      console.error('Error uploading file:', error)
    }
  }
  uploadProgress.value = 0
  uploadingFileName.value = ''
  uploading.value = false
  event.target.value = ''
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
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
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: var(--color-background);
}

.repository-header {
  padding: var(--spacing-xl) var(--spacing-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  z-index: 10;
}

.page-title {
  font-size: 24px;
  margin-bottom: 4px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.breadcrumb-item {
  background: none;
  padding: 0;
  color: var(--color-primary-light);
  cursor: pointer;
  border: none;
  font-size: 13px;
  font-weight: 500;
}

.breadcrumb-item:hover {
  color: white;
}

.breadcrumb-current {
  color: var(--color-text-primary);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
}

.inline-input-container {
  margin: 0 var(--spacing-lg) var(--spacing-lg);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.input-icon {
  color: var(--color-text-muted);
}

.input-wrapper input {
  background: transparent;
  border: none;
  width: 100%;
  font-size: 15px;
  padding: 0;
}

.input-wrapper input:focus {
  box-shadow: none;
}

.input-actions {
  display: flex;
  gap: 8px;
}

.upload-progress {
  margin: 0 var(--spacing-lg) var(--spacing-lg);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.file-name-container {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 500;
}

.upload-icon {
  color: var(--color-primary-light);
}

.progress-percent {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary-light);
}

.progress-bar-container {
  height: 6px;
  background: var(--color-surface-hover);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.file-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: 12px var(--spacing-md);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.file-item:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.file-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-sm);
  background: var(--color-surface-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.file-item:hover .file-icon-wrapper {
  color: var(--color-primary);
  background: rgba(79, 70, 229, 0.1);
}

.file-content {
  flex: 1;
  min-width: 0;
}

.file-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 12px;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.dot {
  font-size: 8px;
}

.file-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.file-item:hover .file-actions {
  opacity: 1;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--color-text-muted);
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary);
}

.btn-icon.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.btn-icon.success:hover {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-illustration {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--color-surface-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-muted);
}

.empty-state h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--color-text-muted);
  max-width: 300px;
  font-size: 14px;
}

.spin {
  animation: spin 1s linear infinite;
}

/* Transitions */
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.list-enter-active, .list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}
.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@media (max-width: 768px) {
  .repository-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-lg);
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .btn span {
    display: none;
  }
  
  .btn {
    padding: 10px;
    flex: 1;
  }
}
</style>
