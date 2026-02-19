import React from 'react';
import { ImageUploader } from './components/ImageUploader';
import { useEditorStore } from './store/editor-store';
import { Toaster } from 'sonner';

function App() {
  const images = useEditorStore((state) => state.images);
  const currentImageId = useEditorStore((state) => state.currentImageId);
  
  const currentImage = images.find((img) => img.id === currentImageId);

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Image Watermark Remover</h1>
          <p className="text-sm text-muted-foreground">
            Remove watermarks from your images with ease
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {!currentImage ? (
          <div className="max-w-2xl mx-auto">
            <ImageUploader />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">{currentImage.file.name}</h2>
                <p className="text-sm text-muted-foreground">
                  {currentImage.width} × {currentImage.height} • {currentImage.format.toUpperCase()}
                </p>
              </div>
            </div>
            
            <div className="border rounded-lg overflow-hidden">
              <img
                src={currentImage.url}
                alt={currentImage.file.name}
                className="w-full h-auto"
              />
            </div>
            
            <div className="text-center text-muted-foreground">
              <p>Selection tools and processing coming soon...</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
