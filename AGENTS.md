# AGENTS.md

Guidelines for AI coding agents working on the **Image Watermark Remover** project.

## Project Overview

A web-based image watermark removal application built with React + Vite + TypeScript (frontend) and Python FastAPI (backend). The app uses OpenCV.js for client-side image processing with manual selection tools and optional AI-powered watermark detection using ONNX Runtime.

**License:** GNU General Public License v3.0  
**Repository:** https://github.com/CodewithTanzeel/image-logo-remover.git

## Build, Lint & Test Commands

### Frontend (React + Vite + TypeScript)

\`\`\`bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Fix linting issues automatically
npm run lint:fix

# Type checking
npm run type-check

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run a single test file
npm test -- path/to/test-file.test.ts

# Run tests with coverage
npm test -- --coverage
\`\`\`

### Backend (Python FastAPI)

\`\`\`bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn api.main:app --reload --port 8000

# Run linter
flake8 . --count --show-source --statistics

# Run formatter
black .

# Run type checker
mypy .

# Run all tests
pytest

# Run tests with coverage
pytest --cov=api --cov-report=html

# Run a single test file
pytest tests/test_detector.py
\`\`\`

## Code Style Guidelines

### General Principles

1. **Readability first** - Code should be self-documenting and clear
2. **Consistency** - Follow existing patterns in the codebase
3. **Performance matters** - Image processing is resource-intensive; optimize where possible
4. **Type safety** - Use TypeScript strictly, avoid \`any\` types
5. **Error handling** - Always handle errors gracefully with user-friendly messages
6. **Privacy by design** - Process images client-side whenever possible

### Imports Organization

**TypeScript/React:**
\`\`\`typescript
// 1. React and core libraries
import React, { useState, useEffect } from 'react';

// 2. Third-party UI libraries
import { Button } from '@/components/ui/button';

// 3. Third-party utilities
import { clsx } from 'clsx';

// 4. Local components
import { ImageCanvas } from '@/components/ImageCanvas';

// 5. Local utilities and hooks
import { useOpenCV } from '@/hooks/useOpenCV';

// 6. Types
import type { ImageData, Selection } from '@/types';
\`\`\`

### Formatting

- **Indentation:** 2 spaces for TypeScript/JSX, 4 spaces for Python
- **Line length:** Max 100 characters (strict: 120 for complex JSX)
- **Semicolons:** Required in TypeScript
- **Quotes:** Single quotes for TypeScript, double quotes for Python
- **Trailing commas:** Always use in multiline arrays/objects

### TypeScript Types

- **Strict mode:** Always enabled, no implicit \`any\`
- **Explicit return types:** For all functions and methods
- **Interface over type:** For object shapes

\`\`\`typescript
// Good - explicit and type-safe
interface ProcessingOptions {
  algorithm: 'telea' | 'ns';
  radius: number;
  quality: number;
}

function removeWatermark(
  image: ImageData,
  selection: Selection,
  options: ProcessingOptions
): Promise<ImageData> {
  // implementation
}
\`\`\`

### Naming Conventions

**TypeScript/React:**
- **Components:** PascalCase (\`ImageUploader\`, \`ToolPanel\`)
- **Hooks:** camelCase with \`use\` prefix (\`useOpenCV\`, \`useSelection\`)
- **Functions:** camelCase (\`processImage\`, \`applyInpainting\`)
- **Constants:** UPPER_SNAKE_CASE (\`MAX_FILE_SIZE\`)
- **Files:** kebab-case (\`image-uploader.tsx\`, \`opencv-loader.ts\`)

**Python:**
- **Classes:** PascalCase (\`WatermarkDetector\`)
- **Functions:** snake_case (\`detect_watermark\`)
- **Constants:** UPPER_SNAKE_CASE (\`MAX_IMAGE_SIZE\`)

### React Component Structure

\`\`\`typescript
import React, { useState } from 'react';
import type { FC } from 'react';

interface ImageUploaderProps {
  onUpload: (file: File) => void;
  maxSize?: number;
}

export const ImageUploader: FC<ImageUploaderProps> = ({ 
  onUpload, 
  maxSize = 10485760 // 10MB
}) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    // Handler logic
  };

  return (
    <div className="uploader-container">
      {/* JSX */}
    </div>
  );
};
\`\`\`

### Error Handling

\`\`\`typescript
// Always use try-catch for async operations
async function loadImage(url: string): Promise<HTMLImageElement> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(\`Failed to load image: \${response.statusText}\`);
    }
    return await createImageBitmap(await response.blob());
  } catch (error) {
    console.error('Error loading image:', { url, error });
    throw new ImageLoadError('Image loading failed', { cause: error });
  }
}
\`\`\`

### State Management (Zustand)

\`\`\`typescript
import { create } from 'zustand';
import { temporal } from 'zundo';

interface EditorState {
  image: ImageData | null;
  selections: Selection[];
  isProcessing: boolean;
  
  setImage: (image: ImageData | null) => void;
  addSelection: (selection: Selection) => void;
}

export const useEditorStore = create<EditorState>()(
  temporal(
    (set) => ({
      image: null,
      selections: [],
      isProcessing: false,
      
      setImage: (image) => set({ image }),
      addSelection: (selection) => 
        set((state) => ({ selections: [...state.selections, selection] })),
    }),
    { limit: 50 } // Keep last 50 states for undo/redo
  )
);
\`\`\`

### Performance Best Practices

1. **Lazy load heavy dependencies** (OpenCV.js is ~10MB)
2. **Use Web Workers** for image processing
3. **Optimize canvas rendering** for large images
4. **Clean up OpenCV Mat objects** to prevent memory leaks
5. **Debounce user inputs** for selection tools

### Testing Guidelines

\`\`\`typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ImageUploader } from './ImageUploader';

describe('ImageUploader', () => {
  it('should accept valid image files', async () => {
    const onUpload = vi.fn();
    render(<ImageUploader onUpload={onUpload} />);
    
    const file = new File(['image'], 'test.png', { type: 'image/png' });
    const input = screen.getByLabelText(/upload/i);
    
    fireEvent.change(input, { target: { files: [file] } });
    
    expect(onUpload).toHaveBeenCalledWith(file);
  });
});
\`\`\`

## Git Commit Guidelines

- **Format:** \`<type>(<scope>): <subject>\`
- **Types:** \`feat\`, \`fix\`, \`docs\`, \`style\`, \`refactor\`, \`test\`, \`chore\`, \`perf\`
- **Scope:** Component or module name (e.g., \`uploader\`, \`canvas\`)
- **Subject:** Imperative mood, lowercase, no period, max 72 chars

**Examples:**
\`\`\`
feat(uploader): add drag and drop support
fix(canvas): resolve zoom calculation bug
perf(inpainting): optimize memory usage for large images
\`\`\`

## Project-Specific Notes

- **OpenCV.js:** Always delete Mat objects after use to prevent memory leaks
- **Image validation:** Max 10MB, formats: PNG, JPG, WebP
- **Selection tools:** Use Fabric.js for canvas interactions
- **Inpainting radius:** Default 3px, range 1-10px
- **Export quality:** PNG (lossless), JPEG (80-100%), WebP (80-100%)
- **Browser support:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
