import React from 'react';
import { ImageUploader } from './components/ImageUploader';
import { ImageCanvas } from './components/ImageCanvas';
import { ToolPanel } from './components/ToolPanel';
import { useEditorStore } from './store/editor-store';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { Button } from './components/ui/button';
import { Upload, Download, Sparkles } from 'lucide-react';
import { Toaster } from 'sonner';
import { formatFileSize } from './lib/utils';

function App() {
  const images = useEditorStore((state) => state.images);
  const currentImageId = useEditorStore((state) => state.currentImageId);
  const selections = useEditorStore((state) => state.selections);
  const setCurrentImage = useEditorStore((state) => state.setCurrentImage);
  const isProcessing = useEditorStore((state) => state.isProcessing);
  
  const currentImage = images.find((img) => img.id === currentImageId);

  // Enable keyboard shortcuts
  useKeyboardShortcuts();

  const handleLoadNewImage = () => {
    setCurrentImage(null);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Image Watermark Remover</h1>
              <p className="text-sm text-muted-foreground">
                Remove watermarks from your images with ease • 100% Private
              </p>
            </div>
            {currentImage && (
              <div className="flex items-center gap-2">
                <Button variant="outline" onClick={handleLoadNewImage}>
                  <Upload className="h-4 w-4 mr-2" />
                  Load New Image
                </Button>
                <Button 
                  disabled={selections.length === 0 || isProcessing}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Remove Watermark{selections.length > 1 ? 's' : ''}
                </Button>
                <Button variant="outline" disabled>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {!currentImage ? (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="max-w-2xl w-full">
              <ImageUploader />
            </div>
          </div>
        ) : (
          <>
            {/* Tool Panel */}
            <ToolPanel />

            {/* Canvas Area */}
            <div className="flex-1 flex flex-col">
              {/* Image Info Bar */}
              <div className="border-b bg-muted/50 px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div>
                      <h2 className="text-sm font-semibold">{currentImage.file.name}</h2>
                      <p className="text-xs text-muted-foreground">
                        {currentImage.width} × {currentImage.height} • {currentImage.format.toUpperCase()} • {formatFileSize(currentImage.size)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {selections.length > 0 && (
                      <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 rounded-md">
                        <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                        <span className="font-medium text-primary">
                          {selections.length} area{selections.length !== 1 ? 's' : ''} selected
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Canvas */}
              <div className="flex-1 p-4">
                <ImageCanvas />
              </div>

              {/* Status Bar */}
              <div className="border-t bg-muted/50 px-4 py-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-4">
                    <span>OpenCV.js: Not Loaded</span>
                    <span>•</span>
                    <span>All processing happens in your browser</span>
                    <span>•</span>
                    <span className="font-mono">
                      Shortcuts: R (Rectangle) • L (Lasso) • H (Pan) • Esc (Cancel)
                    </span>
                  </div>
                  <div>
                    Ready
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
