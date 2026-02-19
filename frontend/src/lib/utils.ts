import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

export function validateImageFile(file: File): { valid: boolean; error?: string } {
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB
  const SUPPORTED_FORMATS = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];

  if (!SUPPORTED_FORMATS.includes(file.type)) {
    return { valid: false, error: 'Unsupported format. Please use PNG, JPEG, or WebP.' };
  }

  if (file.size > MAX_SIZE) {
    return { valid: false, error: `File too large. Maximum size is ${formatFileSize(MAX_SIZE)}.` };
  }

  return { valid: true };
}
