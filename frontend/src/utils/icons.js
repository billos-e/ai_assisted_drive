/**
 * Get icon for a file based on mime type
 */
export function getFileIcon(mimeType, isFolder = false) {
  if (isFolder) return '📁'
  
  if (mimeType?.includes('pdf')) return '📄'
  if (mimeType?.includes('word') || mimeType?.includes('document')) return '📘'
  if (mimeType?.includes('sheet') || mimeType?.includes('excel')) return '📊'
  if (mimeType?.includes('presentation') || mimeType?.includes('powerpoint')) return '🎯'
  if (mimeType?.includes('image')) return '🖼️'
  if (mimeType?.includes('audio')) return '🎵'
  if (mimeType?.includes('video')) return '🎬'
  if (mimeType?.includes('text') || mimeType?.includes('plain')) return '📃'
  if (mimeType?.includes('code') || mimeType?.includes('javascript') || mimeType?.includes('python')) return '💻'
  
  return '📎'
}

/**
 * Get human-readable file type
 */
export function getFileType(mimeType) {
  if (mimeType?.includes('pdf')) return 'PDF'
  if (mimeType?.includes('word')) return 'Word'
  if (mimeType?.includes('sheet') || mimeType?.includes('excel')) return 'Excel'
  if (mimeType?.includes('presentation') || mimeType?.includes('powerpoint')) return 'PowerPoint'
  if (mimeType?.includes('image')) return 'Image'
  if (mimeType?.includes('audio')) return 'Audio'
  if (mimeType?.includes('video')) return 'Video'
  if (mimeType?.includes('text')) return 'Text'
  return 'File'
}
