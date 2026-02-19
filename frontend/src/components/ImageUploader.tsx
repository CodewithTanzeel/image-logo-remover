import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon } from 'lucide-react';
import { validateImageFile, formatFileSize } from '@/lib/utils';
import { useEditorStore } from '@/store/editor-store';
import type { ImageFile } from '@/types';
import { toast } from 'sonner';

export const ImageUploader: React.FC = () => {
  const addImage = useEditorStore((state) => state.addImage);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      for (const file of acceptedFiles) {
        const validation = validateImageFile(file);
        
        if (!validation.valid) {
          toast.error(validation.error || 'Invalid file');
          continue;
        }

        try {
          // Load image to get dimensions
          const url = URL.createObjectURL(file);
          const img = new Image();
          
          await new Promise<void>((resolve, reject) => {
            img.onload = () => resolve();
            img.onerror = () => reject(new Error('Failed to load image'));
            img.src = url;
          });

          const imageFile: ImageFile = {
            id: crypto.randomUUID(),
            file,
            url,
            width: img.width,
            height: img.height,
            format: file.type.split('/')[1],
            size: file.size,
          };

          addImage(imageFile);
          toast.success(`Loaded ${file.name}`);
        } catch (error) {
          console.error('Error loading image:', error);
          toast.error(`Failed to load ${file.name}`);
        }
      }
    },
    [addImage]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/webp': ['.webp'],
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div
      {...getRootProps()}
      className={`
        relative flex flex-col items-center justify-center
        min-h-[400px] rounded-lg border-2 border-dashed
        transition-all duration-200 cursor-pointer
        ${isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'}
      `}
    >
      <input {...getInputProps()} />
      
      <div className="flex flex-col items-center gap-4 text-center p-8">
        {isDragActive ? (
          <>
            <Upload className="h-16 w-16 text-primary animate-bounce" />
            <div>
              <p className="text-lg font-medium">Drop images here</p>
              <p className="text-sm text-muted-foreground">Release to upload</p>
            </div>
          </>
        ) : (
          <>
            <ImageIcon className="h-16 w-16 text-muted-foreground" />
            <div>
              <p className="text-lg font-medium">Drag & drop images here</p>
              <p className="text-sm text-muted-foreground">or click to browse</p>
            </div>
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Supported formats: PNG, JPEG, WebP</p>
              <p>Maximum size: 10 MB per image</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
