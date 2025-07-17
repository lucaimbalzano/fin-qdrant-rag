export const fileUtils = {
  // Sanitize file name
  sanitizeFileName(name: string): string {
    if (!name || name.trim() === "") {
      return "-";
    }
    // Replace weird characters with underscore
    return name.replace(/[^a-zA-Z0-9.-]/g, "_");
  },

  // Format file size
  formatFileSize(bytes: number): string {
    const mb = bytes / 1024 / 1024;
    return `${mb.toFixed(2)} MB`;
  },

  // Validate file type
  isValidFileType(file: File, allowedTypes: string[]): boolean {
    return allowedTypes.includes(file.type);
  },

  // Get file extension
  getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toLowerCase() || '';
  },
}; 