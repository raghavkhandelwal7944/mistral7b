````markdown
# Mistral-7B Mental Health Counseling Model Deployment

This repository contains everything you need to deploy your fine-tuned Mistral-7B mental health counseling model.

## � NEW: Deploy to Google Cloud Platform!

**Got $300 GCP free credit? Deploy in 30 minutes for fast, cloud-hosted inference!**

👉 **Start here:** Open `QUICK_START_GCP.md` for the fastest deployment path!

- ⚡ Fast GPU inference (NVIDIA T4)
- 🌐 Accessible from anywhere
- 💰 Free with your $300 credit (~1-7 months)
- 📦 Includes web chat interface

**Files for GCP deployment:**
- `QUICK_START_GCP.md` - 30-minute quick start guide
- `GCP_DEPLOYMENT_GUIDE.md` - Complete detailed guide
- `gcp_vm_setup.sh` - Automated VM setup script
- `chat_web_interface.html` - Beautiful web UI
- `test_gcp_chatbot.py` - Python client
- `gcp_quick_reference.py` - Command reference

---

## 📋 Table of Contents

- [GCP Deployment (RECOMMENDED)](#-new-deploy-to-google-cloud-platform)
- [Local Installation](#-installation)
- [Usage Guide](#-usage-guide)
  - [1. Merge Model](#1-merge-model)
  - [2. FastAPI Server](#2-fastapi-server)
  - [3. Command-Line Chat](#3-command-line-chat)
- [Upload to Hugging Face](#upload-to-hugging-face)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)

## 🎯 Overview

This package includes:

1. **Model Merger** (`merge_model.py`) - Combines base Mistral-7B with LoRA adapters
2. **FastAPI Server** (`fastapi_server.py`) - HTTP API for production deployment
3. **CLI Chat** (`cli_chat.py`) - Interactive terminal chat interface
4. **Requirements** (`requirements.txt`) - All necessary dependencies

## 🔧 Prerequisites

### Hardware Requirements

**Minimum:**
- RAM: 16 GB
- Storage: 20 GB free space
- CPU: Modern multi-core processor

**Recommended:**
- GPU: NVIDIA GPU with 8+ GB VRAM (RTX 3060 or better)
- RAM: 32 GB
- Storage: 50 GB free space (SSD preferred)

### Software Requirements

- Python 3.8 or higher
- CUDA 11.8+ (if using GPU)
- Git (optional, for version control)

## 📦 Installation

### Step 1: Set up Python Environment

```cmd
REM Create virtual environment
python -m venv venv

REM Activate virtual environment
venv\Scripts\activate
```

### Step 2: Install PyTorch

**For GPU (CUDA 11.8):**
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**For GPU (CUDA 12.1):**
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**For CPU only:**
```cmd
pip install torch torchvision torchaudio
```

### Step 3: Install Dependencies

```cmd
pip install -r requirements.txt
```

### Step 4: Verify Installation

```cmd
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')"
```

## 🚀 Usage Guide

### 1. Merge Model

First, merge your LoRA adapter with the base model to create a standalone model.

**Run the merger:**
```cmd
python merge_model.py
```

**What it does:**
- Loads `mistralai/Mistral-7B-Instruct-v0.3` from HuggingFace
- Loads your LoRA adapter from `C:\Users\raghav khandelwal\Downloads\mistral-7b-mental-health-qlora-adapter`
- Merges them into a single model
- Saves to `./merged_mental_health_model/`

**Expected output:**
```
================================================================================
MISTRAL-7B MENTAL HEALTH MODEL MERGER
================================================================================

📦 Loading base model: mistralai/Mistral-7B-Instruct-v0.3
   ✓ Base model loaded successfully

🔧 Loading LoRA adapter from: C:\Users\raghav khandelwal\Downloads\...
   ✓ LoRA adapter loaded successfully

🔀 Merging adapter weights with base model...
   ✓ Model merged successfully

💾 Saving merged model to: ./merged_mental_health_model
   ✓ Model saved successfully

📝 Saving tokenizer to: ./merged_mental_health_model
   ✓ Tokenizer saved successfully

================================================================================
✅ MERGE COMPLETE!
================================================================================
```

**Time estimate:** 5-15 minutes (depending on hardware)

---

### 2. FastAPI Server

Deploy the model as an HTTP API server for production use.

**Start the server:**
```cmd
python fastapi_server.py
```

**Default settings:**
- Host: `0.0.0.0` (accessible from network)
- Port: `8000`

**Custom settings:**
```cmd
set MODEL_PATH=./merged_mental_health_model
set HOST=127.0.0.1
set PORT=8080
python fastapi_server.py
```

**Access points:**
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Example API call (using curl):**
```cmd
curl -X POST "http://localhost:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"I've been feeling anxious lately\"}"
```

**Example API call (using Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "I've been feeling stressed about work",
        "max_length": 512,
        "temperature": 0.7
    }
)

print(response.json()["response"])
```

---

### 3. Command-Line Chat

Interactive chat interface for local terminal use.

**Start the CLI:**
```cmd
python cli_chat.py
```

**Available commands:**
- Type your message and press Enter to chat
- `clear` - Clear conversation history
- `history` - View conversation history
- `quit` or `exit` - Exit the chat

**Example session:**
```
================================================================================
🧠 MENTAL HEALTH COUNSELING AI - COMMAND LINE INTERFACE
================================================================================

🎮 GPU detected: NVIDIA GeForce RTX 3060
   VRAM: 12.00 GB

📦 Loading model from: ./merged_mental_health_model
   ✓ Tokenizer loaded
   ✓ Model loaded successfully

✅ Ready to chat!
================================================================================

💬 Chat Interface
--------------------------------------------------------------------------------

You: I've been feeling overwhelmed with work lately

AI: I understand that work can be really stressful sometimes. It's important 
to acknowledge these feelings. Can you tell me more about what specifically 
is making you feel overwhelmed?

You: I have too many deadlines and not enough time

AI: It sounds like you're dealing with time pressure and multiple competing 
demands. That's a common source of stress. Have you been able to prioritize 
your tasks or talk to your manager about the workload?
```

## 📚 API Documentation

### Endpoints

#### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

#### 2. Simple Chat
```
POST /chat
```

**Request:**
```json
{
  "message": "Your message here",
  "max_length": 512,
  "temperature": 0.7,
  "top_p": 0.9
}
```

**Response:**
```json
{
  "response": "AI assistant's response",
  "model_info": {
    "model": "Mistral-7B Mental Health Counselor",
    "version": "1.0.0",
    "base": "mistralai/Mistral-7B-Instruct-v0.3"
  }
}
```

#### 3. Chat with History
```
POST /chat/conversation
```

**Request:**
```json
{
  "message": "Current message",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "max_length": 512,
  "temperature": 0.7,
  "top_p": 0.9
}
```

### Parameters

- **message** (required): User's input message
- **max_length** (optional, default: 512): Maximum response length (1-2048)
- **temperature** (optional, default: 0.7): Sampling temperature (0.1-2.0)
  - Lower = more focused/deterministic
  - Higher = more creative/random
- **top_p** (optional, default: 0.9): Nucleus sampling (0.0-1.0)

## 🔍 Troubleshooting

### Issue: CUDA Out of Memory

**Solutions:**
1. Reduce batch size in generation
2. Use CPU instead: `set CUDA_VISIBLE_DEVICES=-1`
3. Enable 4-bit quantization (modify model loading code)

### Issue: Model Not Found

**Check:**
1. Verify `merged_mental_health_model` folder exists
2. Run `merge_model.py` first
3. Set `MODEL_PATH` environment variable

### Issue: Slow Generation

**Improvements:**
1. Use GPU instead of CPU
2. Reduce `max_length` parameter
3. Install `xformers` for faster attention

### Issue: Import Errors

**Solution:**
```cmd
pip install --upgrade -r requirements.txt
```

### Issue: Port Already in Use

**Solution:**
```cmd
set PORT=8080
python fastapi_server.py
```

## 📤 Upload to Hugging Face

Want to share your model or use HuggingFace's hosted inference?

### Option 1: Fast Upload via Google Colab (Recommended)
1. Zip your model: `python zip_merged_model.py`
2. Open Google Colab: https://colab.research.google.com/
3. Copy code from `upload_to_hf_colab.py`
4. Upload zip and run (~10-15 minutes)

### Option 2: Local Upload with Retries
```cmd
python hf_upload_retry.py --repo YOUR_USERNAME/model-name --folder merged_mental_health_model
```

See `upload_to_hf_colab.py` and `hf_upload_retry.py` for details.

---

## 📊 Performance Tips

1. **GPU Acceleration**: Always use GPU when available
2. **Batch Processing**: For multiple requests, use batching
3. **Model Quantization**: Consider 4-bit/8-bit quantization for lower memory
4. **Caching**: Implement response caching for common queries
5. **Load Balancing**: Use multiple server instances for high traffic

## 🔐 Security Considerations

1. **Rate Limiting**: Implement rate limiting in production
2. **Authentication**: Add API key authentication
3. **Input Validation**: Validate and sanitize all inputs
4. **HTTPS**: Use SSL/TLS in production
5. **Monitoring**: Log all interactions for audit

## 📝 License

This deployment code is provided as-is. Ensure you comply with:
- Mistral AI's license for the base model
- Your organization's data handling policies
- Relevant healthcare/mental health regulations (HIPAA, etc.)

## 🤝 Support

For issues or questions:
1. Check this README
2. Review error messages carefully
3. Verify all prerequisites are met
4. Check GPU/CPU compatibility

---

**Created for:** Mistral-7B Mental Health Counseling Model  
**Base Model:** mistralai/Mistral-7B-Instruct-v0.3  
**Version:** 1.0.0  
**Last Updated:** November 2025
