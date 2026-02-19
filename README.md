# Image Watermark Remover

A powerful, privacy-focused web application for removing watermarks from images. All processing happens in your browser - your images never leave your device.

## Features

- **Drag & Drop Upload** - Easy image upload interface
- **Manual Selection Tools** - Rectangle, lasso, and magic wand tools
- **AI-Powered Detection** - Automatic watermark detection (optional)
- **Advanced Inpainting** - Uses OpenCV.js algorithms (Telea & Navier-Stokes)
- **Undo/Redo** - Full editing history with unlimited undo
- **Multiple Formats** - Export as PNG, JPEG, or WebP
- **Batch Processing** - Process multiple images at once
- **100% Private** - All processing happens client-side
- **Mobile Friendly** - Works on phones and tablets

## Tech Stack

- **Frontend:** React + Vite + TypeScript
- **UI:** shadcn/ui + Tailwind CSS
- **Image Processing:** OpenCV.js
- **AI Detection:** ONNX Runtime Web
- **State Management:** Zustand with temporal middleware

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/CodewithTanzeel/image-logo-remover.git
cd image-logo-remover

# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev
\`\`\`

Visit http://localhost:5173 to see the app.

### Backend (Optional - for AI features)

\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
\`\`\`

## Usage

1. **Upload Image** - Drag and drop or click to upload an image
2. **Select Watermark** - Use tools to select the watermark area
   - Rectangle: Click and drag
   - Lasso: Free-form drawing
   - Magic Wand: Click on watermark color
   - AI Auto-detect: Let AI find watermarks
3. **Remove** - Click "Remove Watermark" button
4. **Export** - Download your processed image

## Development

### Project Structure

\`\`\`
frontend/
├── src/
│   ├── components/      # React components
│   ├── lib/             # Core logic
│   ├── hooks/           # Custom hooks
│   ├── store/           # State management
│   └── types/           # TypeScript types
└── public/              # Static assets

backend/                 # Optional Python backend
├── api/                 # FastAPI routes
└── models/              # AI models
\`\`\`

### Available Scripts

\`\`\`bash
npm run dev           # Start dev server
npm run build         # Build for production
npm run preview       # Preview production build
npm run lint          # Run linter
npm run type-check    # Check TypeScript types
npm test              # Run tests
\`\`\`

## Contributing

Contributions are welcome! Please read [AGENTS.md](AGENTS.md) for code style guidelines.

1. Fork the repository
2. Create your feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'feat: add amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Privacy

This application processes images entirely in your browser. No images are uploaded to any server. Your privacy is our priority.

## Acknowledgments

- OpenCV.js for image processing
- shadcn/ui for beautiful UI components
- Vercel for hosting

## Roadmap

- [x] Basic watermark removal
- [x] Multiple selection tools
- [x] Undo/redo functionality
- [ ] AI-powered detection
- [ ] Batch processing
- [ ] Video watermark removal
- [ ] Browser extension

## Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ by [Tanzeel](https://github.com/CodewithTanzeel)
