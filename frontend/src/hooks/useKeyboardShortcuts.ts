import { useEffect } from 'react';
import { useEditorStore } from '@/store/editor-store';

export const useKeyboardShortcuts = () => {
  const setActiveTool = useEditorStore((state) => state.setActiveTool);
  const clearSelections = useEditorStore((state) => state.clearSelections);
  const zoom = useEditorStore((state) => state.zoom);
  const setZoom = useEditorStore((state) => state.setZoom);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent shortcuts when typing in input fields
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Tool shortcuts
      if (!e.ctrlKey && !e.metaKey && !e.altKey) {
        switch (e.key.toLowerCase()) {
          case 'v':
            setActiveTool('none');
            break;
          case 'r':
            setActiveTool('rectangle');
            break;
          case 'l':
            setActiveTool('lasso');
            break;
          case 'h':
            setActiveTool('pan');
            break;
          case 'escape':
            setActiveTool('none');
            clearSelections();
            break;
          case 'delete':
          case 'backspace':
            clearSelections();
            e.preventDefault();
            break;
        }
      }

      // Zoom shortcuts
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
        switch (e.key) {
          case '=':
          case '+':
            setZoom(Math.min(500, zoom + 10));
            e.preventDefault();
            break;
          case '-':
            setZoom(Math.max(10, zoom - 10));
            e.preventDefault();
            break;
          case '0':
            setZoom(100);
            e.preventDefault();
            break;
        }
      }

      // Undo/Redo (handled by zundo, but prevent browser defaults)
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        // Undo is handled by zundo middleware
      }
      if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) {
        e.preventDefault();
        // Redo is handled by zundo middleware
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setActiveTool, clearSelections, zoom, setZoom]);
};
