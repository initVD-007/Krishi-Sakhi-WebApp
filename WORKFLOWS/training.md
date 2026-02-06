# Training Phase Workflow

This document outlines the steps to retrain the plant disease detection model using the GPU-enabled environment.

## Prerequisites
- **GPU Environment**: You must use the `venv_gpu` virtual environment, which has TensorFlow with CUDA support.
- **Dataset**: The dataset must be located at `data/dataset` (with `train` and `valid` subdirectories).

## Directory Structure
```
KrishiSakhi_WebApp/
├── data/
│   ├── dataset/         # Images
│   └── models/          # Output folder for .tflite model
├── scripts/
│   └── train_model.py   # Training script
├── venv_gpu/            # GPU-enabled Python environment
└── WORKFLOWS/           # This documentation
```

## Step-by-Step Instructions

### 1. Open Terminal
Navigate to the project root directory: `v:\PROJECTS\KrishiSakhi_WebApp`

### 2. Run Training Script with GPU
Do **NOT** use the standard `venv`. Use the `venv_gpu` Python executable directly to ensure GPU usage.

**Command:**
```powershell
cd scripts
..\venv_gpu\Scripts\python train_model.py
```

### 3. Monitoring Training
- The script will first verify if a GPU is detected. You should see: `✅ GPU DETECTED`.
- It will run in two phases:
    1.  **Phase 1**: Training the Head (Transfer Learning) - 10 Epochs.
    2.  **Phase 2**: Fine-tuning (Unfreezing Layers) - 10 Epochs.

### 4. Output
Upon success, the script will generate:
- `data/models/finetuned_model.tflite`: The optimized TFLite model.
- `data/models/labels.txt`: The class labels file.

### 5. Deployment
- The web application is configured to automatically load the model from `data/models/finetuned_model.tflite`.
- **Restart the Web App** (`run.py`) to load the new model.

## Troubleshooting
- **"NO GPU DETECTED"**: You are likely running with the wrong python environment (e.g., standard `venv` or global python). Ensure you point to `..\venv_gpu\Scripts\python`.
- **"OOM / Out of Memory"**: Reduce `BATCH_SIZE` in `scripts/train_model.py`.
