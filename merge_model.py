"""
Merge LoRA adapter with base Mistral-7B model and save as standalone model.
This script loads the base model, applies LoRA weights, and saves the merged result.
"""

import os

import torch
from peft import PeftConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def merge_and_save_model(
    base_model_name: str = "mistralai/Mistral-7B-Instruct-v0.3",
    adapter_path: str = r"C:\Users\raghav khandelwal\Downloads\mistral-7b-mental-health-qlora-adapter\adapter",
    output_path: str = "./merged_mental_health_model",
    device_map: str = "auto"
):
    """
    Merge LoRA adapter with base model and save as standalone model.
    
    Args:
        base_model_name: HuggingFace model identifier
        adapter_path: Local path to LoRA adapter weights
        output_path: Where to save the merged model
        device_map: Device mapping strategy ('auto', 'cpu', or specific GPU)
    """
    
    print("=" * 80)
    print("MISTRAL-7B MENTAL HEALTH MODEL MERGER")
    print("=" * 80)
    
    # Check if adapter path exists
    if not os.path.exists(adapter_path):
        raise FileNotFoundError(f"Adapter path not found: {adapter_path}")
    
    print(f"\n📦 Loading base model: {base_model_name}")
    print("   This may take several minutes...")
    
    try:
        # Load base model WITHOUT device_map to avoid PEFT conflicts
        # We'll move to device after merging
        print("   Loading base model (without device mapping to avoid PEFT issues)...")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            device_map=None,  # Critical: Don't use device_map with PEFT
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print("   ✓ Base model loaded successfully")
        
    except Exception as e:
        print(f"   ✗ Error loading base model: {e}")
        raise
    
    print(f"\n🔧 Loading LoRA adapter from: {adapter_path}")
    try:
        # Check PEFT and Transformers versions
        import peft
        import transformers
        print(f"   Transformers version: {transformers.__version__}")
        print(f"   PEFT version: {peft.__version__}")
        
        # Suppress the meta parameter warnings - they're harmless
        import warnings
        warnings.filterwarnings("ignore", message=".*copying from a non-meta parameter.*")

        # Load the PEFT model with adapter (is_trainable=False for inference/merging)
        print("   Loading LoRA adapter...")
        model = PeftModel.from_pretrained(
            base_model,
            adapter_path,
            is_trainable=False
        )
        print("   ✓ LoRA adapter loaded successfully")
    except KeyError as ke:
        print(f"   ✗ KeyError loading adapter: {ke}")
        print("\n   This usually means the adapter is incompatible with the base model.")
        print("   - Ensure your adapter was trained on EXACTLY the same base model version.")
        print("   - Check for mismatched architectures or model types.")
        print("   - Try updating PEFT and Transformers to the latest versions.")
        print("   - If you see meta parameter warnings, try using PEFT >=0.7.0.")
        print("   - If you trained the adapter with a custom script, check for naming mismatches.")
        raise
    except Exception as e:
        print(f"   ✗ Error loading adapter: {e}")
        print("\n   Troubleshooting steps:")
        print("   - Make sure the adapter path is correct and contains all necessary files.")
        print("   - Ensure the base model and adapter are compatible.")
        print("   - Upgrade PEFT and Transformers.")
        print("   - If you see meta parameter warnings, try updating your libraries.")
        print("   - If the error persists, retrain your adapter or contact the model author.")
        raise
    
    print("\n🔀 Merging adapter weights with base model...")
    
    try:
        # Merge adapter weights into base model
        merged_model = model.merge_and_unload()
        print("   ✓ Model merged successfully")
        
    except Exception as e:
        print(f"   ✗ Error merging model: {e}")
        raise
    
    print(f"\n💾 Saving merged model to: {output_path}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Save the merged model
        merged_model.save_pretrained(
            output_path,
            safe_serialization=True,
            max_shard_size="5GB"
        )
        print("   ✓ Model saved successfully")
        
    except Exception as e:
        print(f"   ✗ Error saving model: {e}")
        raise
    
    print(f"\n📝 Saving tokenizer to: {output_path}")
    
    try:
        # Load and save tokenizer
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        tokenizer.save_pretrained(output_path)
        print("   ✓ Tokenizer saved successfully")
        
    except Exception as e:
        print(f"   ✗ Error saving tokenizer: {e}")
        raise
    
    print("\n" + "=" * 80)
    print("✅ MERGE COMPLETE!")
    print("=" * 80)
    print(f"\nYour merged model is ready at: {output_path}")
    print("\nYou can now:")
    print("  1. Use it with FastAPI server (fastapi_server.py)")
    print("  2. Chat locally via CLI (cli_chat.py)")
    print("  3. Upload to HuggingFace Hub")
    print("  4. Deploy anywhere - no adapter files needed!")
    
    # Print model size information
    try:
        model_size = sum(
            os.path.getsize(os.path.join(output_path, f))
            for f in os.listdir(output_path)
            if os.path.isfile(os.path.join(output_path, f))
        )
        print(f"\nTotal model size: {model_size / (1024**3):.2f} GB")
    except:
        pass

def main():
    """Main execution function with error handling."""
    
    # Check GPU availability
    if torch.cuda.is_available():
        print(f"🎮 GPU detected: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        device_map = "auto"
    else:
        print("💻 No GPU detected - using CPU (this will be slower)")
        device_map = "cpu"
    
    try:
        merge_and_save_model(device_map=device_map)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n\n❌ Error during merge process: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
