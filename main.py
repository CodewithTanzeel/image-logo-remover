"""
main.py — FastAPI backend for the logo remover.

Endpoints:
    GET  /health          → {"status": "ok", "device": "cpu|cuda"}
    POST /remove-logo     → multipart: image (file) + mask (file)
                            returns cleaned image as JPEG download

Run:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import io
import os
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

from inference import DEVICE, load_model, remove_logo

# ---------------------------------------------------------------------------
# Model lifecycle — load once at startup, reuse for every request
# ---------------------------------------------------------------------------

MODEL_PATH = os.path.join(os.path.dirname(__file__),
                          "fine_tuned_watermark_remover.pth")
_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")
    _model = load_model(MODEL_PATH)
    print(f"[logo-remover] Model loaded on {DEVICE}")
    yield
    _model = None


app = FastAPI(
    title="Logo Remover API",
    description="Remove logos/watermarks from images using a trained PyTorch model.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _decode_image(data: bytes, grayscale: bool = False) -> np.ndarray:
    """Decode uploaded file bytes into a numpy array via OpenCV."""
    arr = np.frombuffer(data, dtype=np.uint8)
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imdecode(arr, flag)
    if img is None:
        raise HTTPException(
            status_code=400,
            detail="Could not decode image. Make sure the file is a valid image (JPEG/PNG).",
        )
    return img


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "device": DEVICE, "model_loaded": _model is not None}


@app.post(
    "/remove-logo",
    response_class=Response,
    responses={
        200: {"content": {"image/jpeg": {}}, "description": "Cleaned image (JPEG)"},
        400: {"description": "Bad request — invalid image or mask"},
        500: {"description": "Inference error"},
    },
)
async def remove_logo_endpoint(
    image: UploadFile = File(..., description="Source image (JPEG or PNG)"),
    mask: UploadFile = File(
        ...,
        description="Grayscale mask (JPEG or PNG). White=255 marks the logo region.",
    ),
):
    """
    Upload an image and a mask. Returns the cleaned image as a JPEG.

    - **image**: The photo containing the logo (JPEG or PNG).
    - **mask**: A grayscale image of the same size. White pixels indicate the
      logo region to be removed; black pixels are kept untouched.
    """
    # Read uploads
    image_bytes = await image.read()
    mask_bytes = await mask.read()

    # Decode
    image_bgr = _decode_image(image_bytes, grayscale=False)
    mask_gray = _decode_image(mask_bytes, grayscale=True)

    # Run inference
    try:
        assert _model is not None, "Model not loaded"
        result_bgr = remove_logo(_model, image_bgr, mask_gray)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

    # Encode result as JPEG and return
    success, encoded = cv2.imencode(".jpg", result_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode output image.")

    return Response(
        content=encoded.tobytes(),
        media_type="image/jpeg",
        headers={"Content-Disposition": f'attachment; filename="cleaned_{image.filename}"'},
    )
