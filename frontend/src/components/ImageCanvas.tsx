import React, { useEffect, useRef, useState } from 'react';
import { fabric } from 'fabric';
import { useEditorStore } from '@/store/editor-store';
import type { Selection } from '@/types';

export const ImageCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<fabric.Canvas | null>(null);
  const [isCanvasReady, setIsCanvasReady] = useState(false);

  const currentImageId = useEditorStore((state) => state.currentImageId);
  const images = useEditorStore((state) => state.images);
  const activeTool = useEditorStore((state) => state.activeTool);
  const zoom = useEditorStore((state) => state.zoom);
  const addSelection = useEditorStore((state) => state.addSelection);

  const currentImage = images.find((img) => img.id === currentImageId);

  // Initialize Fabric canvas
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = new fabric.Canvas(canvasRef.current, {
      width: 800,
      height: 600,
      backgroundColor: '#f0f0f0',
      selection: activeTool === 'rectangle',
    });

    fabricCanvasRef.current = canvas;
    setIsCanvasReady(true);

    // Cleanup
    return () => {
      canvas.dispose();
      fabricCanvasRef.current = null;
    };
  }, []);

  // Load image onto canvas
  useEffect(() => {
    if (!fabricCanvasRef.current || !currentImage || !isCanvasReady) return;

    const canvas = fabricCanvasRef.current;
    canvas.clear();

    fabric.Image.fromURL(currentImage.url, (img) => {
      if (!img) return;

      // Scale image to fit canvas
      const canvasWidth = canvas.getWidth();
      const canvasHeight = canvas.getHeight();
      const imgWidth = img.width || 1;
      const imgHeight = img.height || 1;

      const scaleX = (canvasWidth * 0.9) / imgWidth;
      const scaleY = (canvasHeight * 0.9) / imgHeight;
      const scale = Math.min(scaleX, scaleY);

      img.set({
        scaleX: scale,
        scaleY: scale,
        selectable: false,
        evented: false,
      });

      // Center image
      canvas.centerObject(img);
      canvas.add(img);
      canvas.sendToBack(img);
      canvas.renderAll();
    });
  }, [currentImage, isCanvasReady]);

  // Handle zoom changes
  useEffect(() => {
    if (!fabricCanvasRef.current) return;
    const canvas = fabricCanvasRef.current;
    const zoomLevel = zoom / 100;
    canvas.setZoom(zoomLevel);
    canvas.renderAll();
  }, [zoom]);

  // Handle tool changes
  useEffect(() => {
    if (!fabricCanvasRef.current) return;
    const canvas = fabricCanvasRef.current;

    // Clean up previous tool listeners
    canvas.off('mouse:down');
    canvas.off('mouse:move');
    canvas.off('mouse:up');

    switch (activeTool) {
      case 'rectangle':
        setupRectangleTool(canvas);
        break;
      case 'lasso':
        setupLassoTool(canvas);
        break;
      case 'pan':
        setupPanTool(canvas);
        break;
      default:
        canvas.isDrawingMode = false;
        canvas.selection = false;
    }
  }, [activeTool]);

  // Rectangle selection tool
  const setupRectangleTool = (canvas: fabric.Canvas) => {
    let isDrawing = false;
    let rect: fabric.Rect | null = null;
    let startX = 0;
    let startY = 0;

    canvas.isDrawingMode = false;
    canvas.selection = false;

    canvas.on('mouse:down', (e) => {
      if (!e.pointer) return;
      isDrawing = true;
      const pointer = canvas.getPointer(e.e);
      startX = pointer.x;
      startY = pointer.y;

      rect = new fabric.Rect({
        left: startX,
        top: startY,
        width: 0,
        height: 0,
        fill: 'rgba(59, 130, 246, 0.3)',
        stroke: '#3b82f6',
        strokeWidth: 2,
        selectable: false,
        evented: false,
      });

      canvas.add(rect);
    });

    canvas.on('mouse:move', (e) => {
      if (!isDrawing || !rect) return;
      const pointer = canvas.getPointer(e.e);

      const width = pointer.x - startX;
      const height = pointer.y - startY;

      rect.set({
        width: Math.abs(width),
        height: Math.abs(height),
        left: width < 0 ? pointer.x : startX,
        top: height < 0 ? pointer.y : startY,
      });

      canvas.renderAll();
    });

    canvas.on('mouse:up', () => {
      if (!isDrawing || !rect) return;
      isDrawing = false;

      // Save selection if valid size
      if (rect.width && rect.height && rect.width > 5 && rect.height > 5) {
        const selection: Selection = {
          id: crypto.randomUUID(),
          type: 'rectangle',
          coordinates: [
            { x: rect.left || 0, y: rect.top || 0 },
            { x: (rect.left || 0) + (rect.width || 0), y: rect.top || 0 },
            { x: (rect.left || 0) + (rect.width || 0), y: (rect.top || 0) + (rect.height || 0) },
            { x: rect.left || 0, y: (rect.top || 0) + (rect.height || 0) },
          ],
        };
        addSelection(selection);
      } else {
        // Remove if too small
        canvas.remove(rect);
      }

      rect = null;
    });
  };

  // Lasso (free-form) selection tool
  const setupLassoTool = (canvas: fabric.Canvas) => {
    let isDrawing = false;
    const points: fabric.Point[] = [];
    let polyline: fabric.Polyline | null = null;

    canvas.isDrawingMode = false;
    canvas.selection = false;

    canvas.on('mouse:down', (e) => {
      isDrawing = true;
      const pointer = canvas.getPointer(e.e);
      points.length = 0;
      points.push(new fabric.Point(pointer.x, pointer.y));

      polyline = new fabric.Polyline(points, {
        stroke: '#3b82f6',
        strokeWidth: 2,
        fill: 'rgba(59, 130, 246, 0.2)',
        selectable: false,
        evented: false,
      });

      canvas.add(polyline);
    });

    canvas.on('mouse:move', (e) => {
      if (!isDrawing || !polyline) return;
      const pointer = canvas.getPointer(e.e);
      points.push(new fabric.Point(pointer.x, pointer.y));

      polyline.set({ points: [...points] });
      canvas.renderAll();
    });

    canvas.on('mouse:up', () => {
      if (!isDrawing || !polyline) return;
      isDrawing = false;

      // Save selection
      if (points.length > 3) {
        const selection: Selection = {
          id: crypto.randomUUID(),
          type: 'lasso',
          coordinates: points.map((p) => ({ x: p.x, y: p.y })),
        };
        addSelection(selection);
      } else {
        canvas.remove(polyline);
      }

      polyline = null;
    });
  };

  // Pan tool
  const setupPanTool = (canvas: fabric.Canvas) => {
    let isPanning = false;
    let lastPosX = 0;
    let lastPosY = 0;

    canvas.isDrawingMode = false;
    canvas.selection = false;

    canvas.on('mouse:down', (e) => {
      if (!e.e) return;
      isPanning = true;
      lastPosX = e.e.clientX;
      lastPosY = e.e.clientY;
      canvas.defaultCursor = 'grabbing';
    });

    canvas.on('mouse:move', (e) => {
      if (!isPanning || !e.e) return;
      const deltaX = e.e.clientX - lastPosX;
      const deltaY = e.e.clientY - lastPosY;

      canvas.relativePan(new fabric.Point(deltaX, deltaY));

      lastPosX = e.e.clientX;
      lastPosY = e.e.clientY;
      canvas.renderAll();
    });

    canvas.on('mouse:up', () => {
      isPanning = false;
      canvas.defaultCursor = 'grab';
    });
  };

  if (!currentImage) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p>No image loaded</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full flex items-center justify-center bg-gray-100 rounded-lg overflow-hidden">
      <canvas ref={canvasRef} />
    </div>
  );
};
