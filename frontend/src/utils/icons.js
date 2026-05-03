import {
  File,
  FileCode2,
  FileImage,
  FileSpreadsheet,
  FileText,
  Folder,
  Music,
  Presentation,
  Video
} from 'lucide-vue-next'

export function getFileIconComponent(mimeType, isFolder = false) {
  if (isFolder) return Folder

  if (mimeType?.includes('pdf')) return FileText
  if (mimeType?.includes('word') || mimeType?.includes('document')) return FileText
  if (mimeType?.includes('sheet') || mimeType?.includes('excel')) return FileSpreadsheet
  if (mimeType?.includes('presentation') || mimeType?.includes('powerpoint')) return Presentation
  if (mimeType?.includes('image')) return FileImage
  if (mimeType?.includes('audio')) return Music
  if (mimeType?.includes('video')) return Video
  if (mimeType?.includes('text') || mimeType?.includes('plain')) return FileText
  if (mimeType?.includes('code') || mimeType?.includes('javascript') || mimeType?.includes('python')) return FileCode2

  return File
}

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
