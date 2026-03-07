# Use Case Diagrams — Image Logo Remover

This document contains use case diagrams for the Image Logo Remover application using Mermaid syntax.

---

## 1. System Overview

```mermaid
graph TB
    subgraph Actors
        GUI_USER[Desktop User]
        CLI_USER[CLI User]
        API_CLIENT[API Client / Developer]
    end

    subgraph System[Image Logo Remover System]
        GUI[Desktop GUI<br/>gui.py]
        CLI[Command Line<br/>cli.py]
        API[REST API<br/>main.py]
        
        subgraph Core[Core Components]
            INF[Inference Engine<br/>inference.py]
            MASK[Auto Mask Generator<br/>auto_mask.py]
            MODEL[CNN Model<br/>model.py]
        end
    end

    GUI_USER --> GUI
    CLI_USER --> CLI
    API_CLIENT --> API
    
    GUI --> INF
    GUI --> MASK
    CLI --> INF
    API --> INF
    INF --> MODEL
```

---

## 2. Main Use Case Diagram

```mermaid
flowchart LR
    subgraph Actors
        USER((End User))
        DEV((Developer))
    end

    subgraph Image Logo Remover
        UC1[Remove Watermark<br/>from Image]
        UC2[Auto-Detect<br/>Watermark Region]
        UC3[Provide Manual<br/>Mask]
        UC4[Preview Before/After]
        UC5[Save Cleaned Image]
        UC6[Select Custom<br/>Model Weights]
        UC7[Choose Position<br/>Hint]
        UC8[Check API Health]
        UC9[Batch Process<br/>via CLI]
        UC10[Integrate via<br/>REST API]
    end

    USER --> UC1
    UC1 -.->|includes| UC2
    UC1 -.->|includes| UC4
    UC1 -.->|includes| UC5
    USER --> UC3
    USER --> UC6
    USER --> UC7
    USER --> UC9
    DEV --> UC8
    DEV --> UC10
    UC10 -.->|uses| UC1
```

---

## 3. GUI User Use Cases

```mermaid
flowchart TB
    subgraph Actor
        USER((Desktop User))
    end

    subgraph GUI Application
        subgraph Primary[Primary Use Cases]
            UC_LOAD[Load Image<br/>Browse / Drag-Drop]
            UC_REMOVE[Remove Logo]
            UC_SAVE[Save Result]
        end

        subgraph Secondary[Secondary Use Cases]
            UC_HINT[Select Position Hint<br/>auto/bottom-right/top-left/etc.]
            UC_PREVIEW[View Before/After Preview]
            UC_MODEL[Select Custom Model]
            UC_ADV[Toggle Advanced Panel]
        end

        subgraph System[System Operations]
            UC_DETECT[Auto-Detect Mask]
            UC_INPAINT[Inpaint Watermark Region]
        end
    end

    USER --> UC_LOAD
    USER --> UC_REMOVE
    USER --> UC_SAVE
    USER --> UC_HINT
    USER --> UC_MODEL
    USER --> UC_ADV

    UC_REMOVE --> UC_DETECT
    UC_REMOVE --> UC_INPAINT
    UC_REMOVE --> UC_PREVIEW

    style UC_REMOVE fill:#6c63ff,color:#fff
    style UC_DETECT fill:#22c55e,color:#fff
    style UC_INPAINT fill:#22c55e,color:#fff
```

---

## 4. CLI User Use Cases

```mermaid
flowchart LR
    subgraph Actor
        USER((CLI User))
    end

    subgraph CLI Application
        UC_ARGS[Provide Arguments<br/>--image --mask --output --model]
        UC_VALIDATE[Validate Input Files]
        UC_LOAD[Load Model]
        UC_RUN[Run Inference]
        UC_EXPORT[Export Cleaned Image]
    end

    subgraph FS[File System]
        IMG[(Input Image)]
        MASK[(Mask Image)]
        MODEL[(Model Weights)]
        OUT[(Output Image)]
    end

    USER --> UC_ARGS
    UC_ARGS --> UC_VALIDATE
    UC_VALIDATE --> UC_LOAD
    UC_LOAD --> UC_RUN
    UC_RUN --> UC_EXPORT

    IMG --> UC_VALIDATE
    MASK --> UC_VALIDATE
    MODEL --> UC_LOAD
    UC_EXPORT --> OUT
```

---

## 5. API Use Cases

```mermaid
flowchart TB
    subgraph Actor
        CLIENT((API Client))
    end

    subgraph REST API
        subgraph Endpoints
            EP_HEALTH[GET /health<br/>Health Check]
            EP_REMOVE[POST /remove-logo<br/>Remove Watermark]
        end

        subgraph Operations
            OP_UPLOAD[Upload Image + Mask<br/>multipart/form-data]
            OP_DECODE[Decode Uploaded Files]
            OP_INFER[Run Inference]
            OP_ENCODE[Encode Result JPEG]
            OP_RETURN[Return JPEG Response]
        end
    end

    CLIENT --> EP_HEALTH
    CLIENT --> EP_REMOVE

    EP_REMOVE --> OP_UPLOAD
    OP_UPLOAD --> OP_DECODE
    OP_DECODE --> OP_INFER
    OP_INFER --> OP_ENCODE
    OP_ENCODE --> OP_RETURN

    style EP_REMOVE fill:#6c63ff,color:#fff
```

---

## 6. Auto-Mask Generation Use Cases

```mermaid
flowchart TB
    subgraph Input
        IMG[Input Image BGR]
        HINT[Position Hint<br/>auto/corner/center/full]
    end

    subgraph Auto Mask Generator
        subgraph Detection[Detection Strategies]
            D1[Brightness Detection<br/>LAB L > 200]
            D2[Edge Density<br/>Canny + Gaussian]
            D3[Grey Region<br/>Low Saturation HSV]
            D4[Corner Scoring<br/>Bottom-Right Priority]
        end

        subgraph Processing[Mask Processing]
            P1[Connected Components]
            P2[Largest Blob Selection]
            P3[Morphological Cleanup]
            P4[Boundary Expansion]
        end

        OUT[Binary Mask<br/>White=Remove Region]
    end

    IMG --> D1
    IMG --> D2
    IMG --> D3
    HINT --> D4

    D1 --> P1
    D2 --> P1
    D3 --> P1
    D4 --> P1

    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> OUT

    style OUT fill:#22c55e,color:#fff
```

---

## 7. Inference Pipeline Use Cases

```mermaid
flowchart TB
    subgraph Input
        IMG[Input Image<br/>H×W×3 BGR]
        MASK[Binary Mask<br/>H×W Grayscale]
        MODEL[Trained Model<br/>.pth Weights]
    end

    subgraph Inference Engine
        subgraph Preprocessing
            PRE1[Resize to 256×256]
            PRE2[BGR → RGB Conversion]
            PRE3[Normalize to 0-1]
            PRE4[Concatenate Mask<br/>4-Channel Tensor]
        end

        subgraph Model[SimpleLogoRemover CNN]
            ENC1[Encoder Conv1<br/>4→64 channels]
            ENC2[Encoder Conv2<br/>64→128 channels]
            DEC1[Decoder Conv1<br/>128→64 channels]
            DEC2[Decoder Conv2<br/>64→3 channels]
        end

        subgraph Postprocessing
            POST1[Clip Output 0-1]
            POST2[Scale to 0-255 uint8]
            POST3[RGB → BGR Conversion]
            POST4[Resize to Original Size]
        end

        OUT[Cleaned Image<br/>H×W×3 BGR]
    end

    IMG --> PRE1
    MASK --> PRE1
    PRE1 --> PRE2
    PRE2 --> PRE3
    PRE3 --> PRE4
    MODEL --> ENC1

    PRE4 --> ENC1
    ENC1 --> ENC2
    ENC2 --> DEC1
    DEC1 --> DEC2
    DEC2 --> POST1

    POST1 --> POST2
    POST2 --> POST3
    POST3 --> POST4
    POST4 --> OUT

    style OUT fill:#22c55e,color:#fff
```

---

## 8. Complete System Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant GUI as GUI/CLI/API
    participant MASK as Auto Mask
    participant INF as Inference
    participant MODEL as CNN Model
    participant FS as File System

    U->>GUI: Provide Input Image
    GUI->>FS: Read Image File
    FS-->>GUI: Image Data (BGR)

    alt GUI Mode
        U->>GUI: Select Position Hint
        GUI->>MASK: generate_mask(image, hint)
        MASK-->>GUI: Binary Mask
    else CLI/API Mode
        U->>GUI: Provide Manual Mask
        GUI->>FS: Read Mask File
        FS-->>GUI: Mask Data
    end

    GUI->>INF: remove_logo(model, image, mask)
    INF->>MODEL: Forward Pass
    MODEL-->>INF: Cleaned Tensor
    INF-->>GUI: Cleaned Image (BGR)

    GUI->>GUI: Display Preview (GUI only)
    U->>GUI: Save Result
    GUI->>FS: Write Output File
    FS-->>GUI: Success
    GUI-->>U: Done
```

---

## Use Case Descriptions

### UC-01: Remove Watermark from Image
**Actor:** End User (GUI/CLI/API)  
**Description:** Remove a logo or watermark from an image using the trained model.  
**Preconditions:** Valid image file exists  
**Postconditions:** Cleaned image saved or returned  
**Main Flow:**
1. User provides input image
2. System generates or receives mask
3. System runs inference
4. System returns/saves cleaned image

### UC-02: Auto-Detect Watermark Region
**Actor:** System (GUI mode)  
**Description:** Automatically detect the watermark region without user input.  
**Preconditions:** Image loaded  
**Postconditions:** Binary mask generated  
**Main Flow:**
1. Detect low-saturation grey regions
2. Score corner zones
3. Select highest-scoring region
4. Clean up mask morphologically

### UC-03: Provide Manual Mask
**Actor:** CLI/API User  
**Description:** Provide a pre-made mask image for precise control.  
**Preconditions:** Mask file matches image dimensions  
**Postconditions:** Mask used for inference

### UC-04: Preview Before/After
**Actor:** GUI User  
**Description:** View original and cleaned images side-by-side.  
**Preconditions:** Image loaded and processed  
**Postconditions:** User can compare results

### UC-05: Save Cleaned Image
**Actor:** End User  
**Description:** Export the cleaned image to disk.  
**Preconditions:** Processing complete  
**Postconditions:** File written to specified path

### UC-06: Select Custom Model
**Actor:** Advanced User  
**Description:** Use a different trained model weights file.  
**Preconditions:** Valid .pth file exists  
**Postconditions:** Custom model used for inference

### UC-07: Choose Position Hint
**Actor:** GUI User  
**Description:** Guide auto-detection with position hint.  
**Options:** auto, bottom-right, bottom-left, top-right, top-left, center, full  
**Postconditions:** Detection focused on specified region

### UC-08: Check API Health
**Actor:** API Client  
**Description:** Verify API server is running and model is loaded.  
**Endpoint:** GET /health  
**Response:** `{status, device, model_loaded}`

### UC-09: Batch Process via CLI
**Actor:** CLI User  
**Description:** Process multiple images via shell scripting.  
**Preconditions:** Multiple images and masks available  
**Postconditions:** All images processed

### UC-10: Integrate via REST API
**Actor:** Developer  
**Description:** Integrate logo removal into another application.  
**Endpoint:** POST /remove-logo  
**Input:** multipart/form-data (image + mask)  
**Output:** JPEG image

---

## Actor Summary

| Actor | Interface | Use Cases |
|-------|-----------|-----------|
| Desktop User | `gui.py` | UC-01, UC-02, UC-04, UC-05, UC-06, UC-07 |
| CLI User | `cli.py` | UC-01, UC-03, UC-05, UC-06, UC-09 |
| API Client | `main.py` | UC-01, UC-03, UC-05, UC-08, UC-10 |

---

## Component Summary

| Component | File | Responsibility |
|-----------|------|----------------|
| GUI | `gui.py` | Desktop interface with drag-drop, preview |
| CLI | `cli.py` | Command-line argument parsing, file I/O |
| REST API | `main.py` | FastAPI endpoints, multipart handling |
| Inference | `inference.py` | Model loading, preprocessing, postprocessing |
| Auto Mask | `auto_mask.py` | Automatic watermark region detection |
| Model | `model.py` | SimpleLogoRemover CNN architecture |
