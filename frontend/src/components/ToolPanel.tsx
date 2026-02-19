import React from 'react';
import { 
  MousePointer2, 
  Square, 
  Lasso, 
  Wand2, 
  Hand, 
  ZoomIn, 
  ZoomOut, 
  Maximize2,
  Trash2,
  Undo2,
  Redo2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useEditorStore } from '@/store/editor-store';
import type { SelectionTool } from '@/types';

export const ToolPanel: React.FC = () => {
  const activeTool = useEditorStore((state) => state.activeTool);
  const setActiveTool = useEditorStore((state) => state.setActiveTool);
  const zoom = useEditorStore((state) => state.zoom);
  const setZoom = useEditorStore((state) => state.setZoom);
  const selections = useEditorStore((state) => state.selections);
  const clearSelections = useEditorStore((state) => state.clearSelections);

  const tools: Array<{ id: SelectionTool; icon: React.ReactNode; label: string; disabled?: boolean }> = [
    { id: 'none', icon: <MousePointer2 className="h-5 w-5" />, label: 'Select' },
    { id: 'rectangle', icon: <Square className="h-5 w-5" />, label: 'Rectangle' },
    { id: 'lasso', icon: <Lasso className="h-5 w-5" />, label: 'Lasso' },
    { id: 'magic-wand', icon: <Wand2 className="h-5 w-5" />, label: 'Magic Wand', disabled: true },
    { id: 'pan', icon: <Hand className="h-5 w-5" />, label: 'Pan' },
  ];

  const handleZoomIn = () => setZoom(zoom + 10);
  const handleZoomOut = () => setZoom(zoom - 10);
  const handleFitToScreen = () => setZoom(100);

  return (
    <div className="w-64 h-full border-r bg-background p-4 space-y-6">
      {/* Tools Section */}
      <div>
        <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
          Tools
        </h3>
        <div className="space-y-1">
          {tools.map((tool) => (
            <Button
              key={tool.id}
              variant={activeTool === tool.id ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => !tool.disabled && setActiveTool(tool.id)}
              disabled={tool.disabled}
            >
              {tool.icon}
              <span className="ml-2">{tool.label}</span>
              {tool.disabled && (
                <span className="ml-auto text-xs text-muted-foreground">(Soon)</span>
              )}
            </Button>
          ))}
        </div>
      </div>

      {/* Zoom Controls */}
      <div>
        <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
          View
        </h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomOut}
              disabled={zoom <= 10}
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <div className="flex-1 text-center text-sm font-medium">
              {zoom}%
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomIn}
              disabled={zoom >= 500}
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
          </div>
          <Button
            variant="outline"
            className="w-full"
            size="sm"
            onClick={handleFitToScreen}
          >
            <Maximize2 className="h-4 w-4 mr-2" />
            Fit to Screen
          </Button>
        </div>
      </div>

      {/* Selection Info */}
      <div>
        <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
          Selections
        </h3>
        <div className="space-y-2">
          <div className="text-sm text-muted-foreground">
            {selections.length} selection{selections.length !== 1 ? 's' : ''}
          </div>
          {selections.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={clearSelections}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All
            </Button>
          )}
        </div>
      </div>

      {/* History Controls */}
      <div>
        <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
          History
        </h3>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            title="Undo (Ctrl+Z)"
          >
            <Undo2 className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            title="Redo (Ctrl+Y)"
          >
            <Redo2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Instructions */}
      <div className="pt-4 border-t">
        <h4 className="text-xs font-semibold mb-2">Instructions</h4>
        <ul className="text-xs text-muted-foreground space-y-1">
          <li>• Select a tool from above</li>
          <li>• Draw on canvas to select watermark</li>
          <li>• Use Pan tool to move around</li>
          <li>• Zoom in/out for precision</li>
        </ul>
      </div>
    </div>
  );
};
