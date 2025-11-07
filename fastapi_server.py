"""
FastAPI server for Mistral-7B Mental Health Counseling Model.
Provides HTTP API endpoints for chat interaction.
"""

import os
from typing import Dict, List, Optional

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer

# Initialize FastAPI app
app = FastAPI(
    title="Mental Health Counseling AI",
    description="Mistral-7B model fine-tuned for mental health support",
    version="1.0.0"
)

# Global variables for model and tokenizer
model = None
tokenizer = None
device = None

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message", min_length=1)
    max_length: Optional[int] = Field(512, description="Maximum response length", ge=1, le=2048)
    temperature: Optional[float] = Field(0.7, description="Sampling temperature", ge=0.1, le=2.0)
    top_p: Optional[float] = Field(0.9, description="Nucleus sampling parameter", ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI assistant's response")
    model_info: Dict[str, str] = Field(..., description="Model metadata")

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    model_loaded: bool
    device: str

def format_mistral_prompt(message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Format message using Mistral chat template.
    
    Args:
        message: User's current message
        conversation_history: Optional list of previous messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        Formatted prompt string
    """
    # Mistral instruction format
    formatted_messages = []
    
    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                formatted_messages.append(f"[INST] {content} [/INST]")
            else:
                formatted_messages.append(content)
    
    # Add current message
    formatted_messages.append(f"[INST] {message} [/INST]")
    
    return " ".join(formatted_messages)

@app.on_event("startup")
async def load_model():
    """Load model and tokenizer on server startup."""
    global model, tokenizer, device
    
    model_path = os.getenv("MODEL_PATH", "./merged_mental_health_model")
    
    print("=" * 80)
    print("🚀 Starting Mental Health Counseling AI Server")
    print("=" * 80)
    
    # Detect device
    if torch.cuda.is_available():
        device = "cuda"
        print(f"🎮 GPU detected: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        device = "cpu"
        print("💻 Using CPU (GPU not available)")
    
    print(f"\n📦 Loading model from: {model_path}")
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        print("   ✓ Tokenizer loaded")
        
        # Load model with optimizations
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        if device == "cpu":
            model = model.to(device)
        
        model.eval()
        print("   ✓ Model loaded and ready")
        
        print("\n✅ Server ready to accept requests!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        raise

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="online",
        model_loaded=model is not None,
        device=device if device else "unknown"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        device=device if device else "unknown"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for mental health counseling.
    
    Args:
        request: ChatRequest with user message and generation parameters
    
    Returns:
        ChatResponse with AI assistant's response
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Format the prompt
        prompt = format_mistral_prompt(request.message)
        
        # Tokenize
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(device)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_length,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response (remove the prompt)
        # Find the last [/INST] and take everything after it
        if "[/INST]" in full_response:
            assistant_response = full_response.split("[/INST]")[-1].strip()
        else:
            assistant_response = full_response.strip()
        
        return ChatResponse(
            response=assistant_response,
            model_info={
                "model": "Mistral-7B Mental Health Counselor",
                "version": "1.0.0",
                "base": "mistralai/Mistral-7B-Instruct-v0.3"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.post("/chat/conversation", response_model=ChatResponse)
async def chat_with_history(request: Dict):
    """
    Chat endpoint with conversation history support.
    
    Expected format:
    {
        "message": "current message",
        "history": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ],
        "max_length": 512,
        "temperature": 0.7,
        "top_p": 0.9
    }
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        message = request.get("message")
        history = request.get("history", [])
        max_length = request.get("max_length", 512)
        temperature = request.get("temperature", 0.7)
        top_p = request.get("top_p", 0.9)
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Format prompt with history
        prompt = format_mistral_prompt(message, history)
        
        # Tokenize
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(device)
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "[/INST]" in full_response:
            assistant_response = full_response.split("[/INST]")[-1].strip()
        else:
            assistant_response = full_response.strip()
        
        return ChatResponse(
            response=assistant_response,
            model_info={
                "model": "Mistral-7B Mental Health Counselor",
                "version": "1.0.0",
                "base": "mistralai/Mistral-7B-Instruct-v0.3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

def main():
    """Run the FastAPI server."""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\n🌐 Server will be available at: http://{host}:{port}")
    print(f"📚 API documentation: http://{host}:{port}/docs")
    print(f"🔄 Alternative docs: http://{host}:{port}/redoc\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
