import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const driveAPI = {
  /**
   * List items in a folder
   * @param {string} folderId - Folder ID (null for root)
   * @returns {Promise<Array>}
   */
  async listFolder(folderId = null) {
    try {
      const params = folderId ? { folder_id: folderId } : {}
      const response = await apiClient.get('/drive/list', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Create a new folder
   * @param {string} name - Folder name
   * @param {string} folderId - Parent folder ID (optional)
   * @returns {Promise}
   */
  async createFolder(name, folderId = null) {
    try {
      const payload = { name, folder_id: folderId }
      const response = await apiClient.post('/drive/folder', payload)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Upload a file
   * @param {File} file - File to upload
   * @param {string} folderId - Target folder ID (optional)
   * @param {Function} onProgress - Progress callback
   * @returns {Promise}
   */
  async uploadFile(file, folderId = null, onProgress = null) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (folderId) {
        formData.append('folder_id', folderId)
      }

      const response = await apiClient.post('/drive/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: onProgress ? (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        } : undefined
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Open a file in Google Drive
   * @param {string} fileId - Drive file ID
   * @returns {Promise<{url: string}>}
   */
  async openFile(fileId) {
    try {
      const response = await apiClient.get(`/drive/${fileId}/open`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Delete a file or folder from Google Drive
   * @param {string} fileId - Drive file or folder ID
   * @returns {Promise}
   */
  async deleteItem(fileId) {
    try {
      const response = await apiClient.delete(`/drive/${fileId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export const chatAPI = {
  /**
   * Stream chat response
   * @param {string} message - User message
   * @param {Array} history - Chat history
   * @param {number} topK - Number of sources
   * @param {Function} onChunk - Callback for each chunk
   * @returns {Promise<{text: string, sources: Array}>}
   */
  async streamChat(message, history = [], topK = 5, onChunk = null) {
    try {
      const payload = {
        message,
        history,
        top_k: topK
      }

      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullText = ''
      let sources = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        
        // Check for sources separator
        if (chunk.includes('[SOURCES_SEPARATOR]')) {
          // Split text and sources
          const parts = chunk.split('[SOURCES_SEPARATOR]')
          
          // Send the text part first
          if (parts[0]) {
            fullText += parts[0]
            if (onChunk) {
              onChunk(parts[0])
            }
          }
          
          // Parse sources from remaining part
          if (parts[1]) {
            try {
              const sourcesJson = parts[1].trim()
              if (sourcesJson) {
                sources = JSON.parse(sourcesJson)
              }
            } catch (e) {
              console.error('Failed to parse sources:', e)
            }
          }
        } else {
          fullText += chunk
          if (onChunk) {
            onChunk(chunk)
          }
        }
      }

      return { text: fullText, sources }
    } catch (error) {
      throw error
    }
  }
}

export const healthAPI = {
  /**
   * Health check
   * @returns {Promise}
   */
  async check() {
    try {
      const response = await apiClient.get('/health')
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default {
  driveAPI,
  chatAPI,
  healthAPI
}
