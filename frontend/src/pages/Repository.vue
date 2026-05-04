<template>
  <div class="repository-page">
    <!-- Header -->
    <header class="repository-header">
      <div class="header-left">
        <h1 class="page-title">All files</h1>
      </div>

      <div class="header-right">
        <div class="search-bar" title="Soon">
          <Search :size="18" class="search-icon" />
          <input type="text" placeholder="Search files..." disabled />
          <span class="badge-soon">soon</span>
        </div>
        <button class="icon-btn">
          <Bell :size="20" />
        </button>
        <div class="user-avatar-neutral">
          <CircleUser :size="24" />
        </div>
      </div>
    </header>

    <!-- Content Area -->
    <div class="repository-content">
      <!-- Action Bar -->
      <div class="action-bar">
        <div class="breadcrumb">
          <span class="breadcrumb-item" @click="goToRoot">My Files</span>
          <template v-if="currentFolderId">
            <ChevronRight :size="14" class="breadcrumb-sep" />
            <span class="breadcrumb-current">{{ currentFolderName }}</span>
          </template>
        </div>

        <div class="actions">
          <button class="btn-secondary" @click="showCreateFolderInput">
            <FolderPlus :size="18" />
            <span>New folder</span>
          </button>
          <button class="btn-primary" @click="triggerFileUpload">
            <Upload :size="18" />
            <span>Upload</span>
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
        <div v-if="showNewFolderInput" class="inline-input-container">
          <div class="input-wrapper">
            <Folder :size="20" class="input-icon" />
            <input
              ref="folderInput"
              v-model="newFolderName"
              type="text"
              placeholder="Folder name"
              @keyup.enter="createFolder"
              @keyup.escape="showNewFolderInput = false"
              autofocus
            />
          </div>
          <div class="input-actions">
            <button class="action-btn-text" @click="createFolder">Create</button>
            <button class="action-btn-text cancel" @click="showNewFolderInput = false">Cancel</button>
          </div>
        </div>
      </Transition>

      <!-- Upload progress -->
      <Transition name="fade">
        <div v-if="uploading" class="upload-progress">
          <div class="progress-info">
            <span class="file-name-text">Uploading {{ uploadingFileName }}...</span>
            <span class="progress-percent">{{ uploadProgress }}%</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
        </div>
      </Transition>

      <!-- File Table -->
      <div class="file-table-container">
        <div class="table-header">
          <div class="col-name">Name</div>
          <div class="col-size">Size</div>
          <div class="col-date">Date modified</div>
          <div class="col-actions"></div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
        </div>

        <div v-else-if="items.length === 0" class="empty-state">
          <div class="empty-illustration">
            <Inbox :size="48" />
          </div>
          <p>No files found in this folder</p>
        </div>

        <div v-else class="table-body">
          <div
            v-for="item in sortedItems"
            :key="item.id"
            class="file-row"
            @click="handleItemClick(item)"
          >
            <div class="col-name">
              <div class="file-icon-wrapper" :style="{ color: getIconColor(item) }">
                <component :is="getFileIconComponent(item.mime_type, item.type === 'folder')" :size="22" />
              </div>
              <span class="file-name">{{ item.name }}</span>
              <div v-if="indexingFiles.includes(item.id)" class="indexing-badge">
                <LoaderCircle :size="12" class="spin" />
                <span>Indexing</span>
              </div>
            </div>
            
            <div class="col-size">
              {{ item.type === 'file' ? formatSize(item.size) : '--' }}
            </div>

            <div class="col-date">
              {{ formatDate(item.modified_time) }}
            </div>

            <div class="col-actions">
              <button
                class="delete-btn"
                title="Delete"
                @click.stop="confirmDeleteItem(item)"
              >
                <Trash2 :size="18" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { 
  Search, 
  Bell, 
  ChevronRight, 
  FolderPlus, 
  Upload, 
  Folder, 
  Inbox, 
  LoaderCircle, 
  Trash2,
  Check,
  X,
  CircleUser
} from 'lucide-vue-next'
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

const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => {
    // Folders first
    if (a.type === 'folder' && b.type !== 'folder') return -1
    if (a.type !== 'folder' && b.type === 'folder') return 1
    
    // Then alphabetical
    return a.name.localeCompare(b.name)
  })
})

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
  if (!bytes) return '--'
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

const getIconColor = (item) => {
  if (item.type === 'folder') return '#4F46E5'
  const mime = item.mime_type?.toLowerCase() || ''
  if (mime.includes('pdf')) return 'var(--color-file-pdf)'
  if (mime.includes('presentation') || mime.includes('powerpoint')) return 'var(--color-file-slides)'
  if (mime.includes('image')) return 'var(--color-file-image)'
  if (mime.includes('zip') || mime.includes('tar') || mime.includes('archive')) return 'var(--color-file-archive)'
  return 'var(--color-text-secondary)'
}

onMounted(() => {
  loadItems()
})

watch(currentFolderId, () => {
  loadItems()
})

defineExpose({
  triggerFileUpload
})
</script>

<style scoped>
.repository-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: var(--color-background);
  overflow: hidden;
}

.repository-header {
  height: 70px;
  background-color: var(--color-surface);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--spacing-xl);
  flex-shrink: 0;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.search-bar {
  position: relative;
  width: 300px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
}

.search-bar input {
  width: 100%;
  padding: 10px 60px 10px 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background-color: var(--color-background);
  font-size: 14px;
}

.search-bar input:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.search-bar .badge-soon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%) translateX(10px);
  font-size: 10px;
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  color: var(--color-text-muted);
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
}

.search-bar:hover .badge-soon {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.icon-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.icon-btn:hover {
  background-color: var(--color-background);
}

.user-avatar-neutral {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
}

.user-avatar-neutral:hover {
  border-color: var(--color-primary-light);
  color: var(--color-primary);
}

.repository-content {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.breadcrumb-item {
  color: var(--color-text-secondary);
  cursor: pointer;
}

.breadcrumb-item:hover {
  color: var(--color-primary);
}

.breadcrumb-sep {
  color: var(--color-text-muted);
}

.breadcrumb-current {
  color: var(--color-text-primary);
}

.actions {
  display: flex;
  gap: var(--spacing-md);
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  padding: 8px 20px;
  border-radius: var(--radius-md);
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.btn-secondary {
  background-color: white;
  color: var(--color-text-primary);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-weight: 600;
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.inline-input-container {
  background-color: white;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--color-primary);
  box-shadow: var(--shadow-subtle);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.input-wrapper input {
  border: none;
  font-size: 15px;
  outline: none;
  width: 100%;
}

.input-actions {
  display: flex;
  gap: 12px;
}

.action-btn-text {
  background: none;
  border: none;
  font-weight: 600;
  color: var(--color-primary);
  cursor: pointer;
}

.action-btn-text.cancel {
  color: var(--color-text-secondary);
}

.upload-progress {
  background-color: white;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
}

.progress-bar-container {
  height: 6px;
  background-color: var(--color-background);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: 3px;
}

.file-table-container {
  background-color: white;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
}

.table-header {
  display: flex;
  padding: 12px 24px;
  border-bottom: 1px solid var(--color-border);
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.col-name { flex: 2; display: flex; align-items: center; gap: 16px; min-width: 0; }
.col-size { flex: 0.5; }
.col-date { flex: 1; }
.col-actions { width: 50px; display: flex; justify-content: flex-end; }

.file-row {
  display: flex;
  padding: 0 24px;
  height: 60px;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background-color 0.2s;
}

.file-row:hover {
  background-color: var(--color-background);
}

.file-row:last-child {
  border-bottom: none;
}

.file-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.indexing-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  background-color: #FEF3C7;
  color: #D97706;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.delete-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  opacity: 0;
  transition: all 0.2s;
}

.file-row:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: var(--color-error);
  background-color: #FEE2E2;
}

.loading-state, .empty-state {
  padding: 100px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  gap: 16px;
}

.empty-illustration {
  color: var(--color-border);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Transitions */
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
