# PROJECT PLAN: Image Watermark Remover

## Executive Summary

A privacy-focused, browser-based watermark removal tool that processes images entirely client-side using OpenCV.js for manual selection and ONNX Runtime for AI-powered detection.

## Tech Stack

### Frontend
- **Framework:** React 18 + Vite 5 + TypeScript 5
- **UI:** shadcn/ui + Tailwind CSS 3
- **State:** Zustand 4 + zundo
- **Image Processing:** OpenCV.js 4.9
- **AI/ML:** ONNX Runtime Web
- **Canvas:** Fabric.js 5
- **Icons:** Lucide React

### Backend (Optional)
- **Framework:** FastAPI
- **ML:** PyTorch, OpenCV-Python

## Implementation Phases

### Phase 1: Setup & Upload (Days 1-2)
- Initialize Vite + React + TypeScript
- Configure Tailwind + shadcn/ui
- Create app layout
- Implement drag-drop upload
- File validation (10MB, PNG/JPG/WebP)

### Phase 2: Canvas & Selection (Days 2-3)
- Image canvas with zoom/pan
- Rectangle selection tool
- Lasso selection tool
- Magic wand tool
- Multiple selections

### Phase 3: OpenCV & Inpainting (Days 3-4)
- Load OpenCV.js asynchronously
- Telea algorithm
- Navier-Stokes algorithm
- Web Worker processing
- Progress indicators

### Phase 4: History & Undo (Day 4)
- Zustand + zundo setup
- Undo/Redo UI
- Keyboard shortcuts (Ctrl+Z/Y)
- History panel

### Phase 5: AI Detection (Days 5-6) [Optional]
- ONNX Runtime integration
- Watermark detection model
- Auto-selection
- Confidence threshold

### Phase 6: Export (Day 6)
- PNG/JPEG/WebP export
- Quality settings
- Batch export with ZIP
- Before/after preview

### Phase 7: Polish (Days 7-8)
- Loading states
- Error handling
- Keyboard shortcuts
- Responsive design
- Accessibility

### Phase 8: Testing (Days 8-9)
- Unit tests
- Integration tests
- Browser testing
- Performance optimization

### Phase 9: Deployment (Day 9)
- Deploy to Vercel
- Setup CI/CD
- Documentation

## Performance Targets
- Initial load: < 3 seconds
- Inpainting: < 5 seconds
- Memory: < 500MB for 10MB image
- Bundle: < 500KB initial

## Browser Support
Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## Success Criteria
- Upload and display image
- Manual watermark selection
- Remove watermark via inpainting
- Export processed image
- Undo/redo functionality
- Works on mobile

---
**Status:** Ready for Implementation
