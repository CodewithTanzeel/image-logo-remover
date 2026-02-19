import { create } from 'zustand';
import { temporal } from 'zundo';
import type { EditorState, ImageFile, Selection, SelectionTool, ProcessingOptions } from '@/types';

const useEditorStoreBase = create<EditorState>()((set) => ({
  images: [],
  currentImageId: null,
  selections: [],
  isProcessing: false,
  activeTool: 'none',
  zoom: 100,
  processingOptions: {
    algorithm: 'telea',
    radius: 3,
    quality: 90,
  },

  addImage: (image: ImageFile) =>
    set((state) => ({
      images: [...state.images, image],
      currentImageId: image.id,
    })),

  removeImage: (id: string) =>
    set((state) => ({
      images: state.images.filter((img) => img.id !== id),
      currentImageId: state.currentImageId === id ? null : state.currentImageId,
    })),

  setCurrentImage: (id: string | null) => set({ currentImageId: id }),

  addSelection: (selection: Selection) =>
    set((state) => ({
      selections: [...state.selections, selection],
    })),

  removeSelection: (id: string) =>
    set((state) => ({
      selections: state.selections.filter((s) => s.id !== id),
    })),

  clearSelections: () => set({ selections: [] }),

  setActiveTool: (tool: SelectionTool) => set({ activeTool: tool }),

  setProcessing: (isProcessing: boolean) => set({ isProcessing }),

  setZoom: (zoom: number) => set({ zoom: Math.max(10, Math.min(500, zoom)) }),

  updateProcessingOptions: (options: Partial<ProcessingOptions>) =>
    set((state) => ({
      processingOptions: { ...state.processingOptions, ...options },
    })),
}));

export const useEditorStore = temporal(useEditorStoreBase, {
  limit: 50,
  equality: (a, b) => a === b,
  handleSet: (handleSet) =>
    (state) => {
      // Don't track certain state changes in history
      const { isProcessing, activeTool, zoom, ...trackedState } = state;
      handleSet(trackedState as EditorState);
    },
});

// Export undo/redo actions
export const { undo, redo, clear: clearHistory } = useEditorStore.temporal.getState();
