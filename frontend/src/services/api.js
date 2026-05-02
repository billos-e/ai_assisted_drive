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
  }
}

export const chatAPI = {
  /**
   * Stream chat response
   * @param {string} message - User message
   * @param {Array} history - Chat history
   * @param {number} topK - Number of sources
   * @param {Function} onChunk - Callback for each chunk
   * @returns {Promise}
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

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        fullText += chunk
        if (onChunk) {
          onChunk(chunk)
        }
      }

      return fullText
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
