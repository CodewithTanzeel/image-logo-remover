export interface ImageFile {
  id: string;
  file: File;
  url: string;
  width: number;
  height: number;
  format: string;
  size: number;
}

export interface Selection {
  id: string;
  type: 'rectangle' | 'lasso' | 'magic-wand' | 'ai-detection';
  coordinates: Coordinate[];
  mask?: ImageData;
  confidence?: number;
}

export interface Coordinate {
  x: number;
  y: number;
}

export interface ProcessingOptions {
  algorithm: 'telea' | 'navier-stokes';
  radius: number;
  quality: number;
}

export interface ExportOptions {
  format: 'png' | 'jpeg' | 'webp';
  quality: number;
  filename: string;
}

export type SelectionTool = 'rectangle' | 'lasso' | 'magic-wand' | 'pan' | 'none';

export interface EditorState {
  images: ImageFile[];
  currentImageId: string | null;
  selections: Selection[];
  isProcessing: boolean;
  activeTool: SelectionTool;
  processingOptions: ProcessingOptions;
  zoom: number;
  
  // Actions
  addImage: (image: ImageFile) => void;
  removeImage: (id: string) => void;
  setCurrentImage: (id: string | null) => void;
  addSelection: (selection: Selection) => void;
  removeSelection: (id: string) => void;
  clearSelections: () => void;
  setActiveTool: (tool: SelectionTool) => void;
  setProcessing: (isProcessing: boolean) => void;
  setZoom: (zoom: number) => void;
  updateProcessingOptions: (options: Partial<ProcessingOptions>) => void;
}
