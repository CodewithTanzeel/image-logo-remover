from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from PIL import Image
import io

app = FastAPI(
    title="Watermark Remover API",
    description="AI-powered watermark detection and removal",
    version="0.1.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Watermark Remover API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "detect": "/api/detect (POST)",
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/detect")
async def detect_watermark(file: UploadFile = File(...)):
    """
    Detect watermarks in an uploaded image using AI/CV techniques.
    Returns bounding boxes and confidence scores.
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Placeholder for actual detection logic
        # TODO: Implement AI-based watermark detection
        detections = []
        
        return {
            "success": True,
            "detections": detections,
            "message": "Detection completed (placeholder)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
