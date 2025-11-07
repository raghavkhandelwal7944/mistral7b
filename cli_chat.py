"""
Command-line interface for interactive chat with Mistral-7B Mental Health Counseling Model.
Provides a terminal-based chat experience.
"""

import os
import sys
from typing import Dict, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class MentalHealthChatbot:
    """Interactive chatbot for mental health counseling."""
    
    def __init__(self, model_path: str = "./merged_mental_health_model"):
        """
        Initialize the chatbot.
        
        Args:
            model_path: Path to the merged model directory
        """
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.device = None
        self.conversation_history: List[Dict[str, str]] = []
        
    def load_model(self):
        """Load the model and tokenizer."""
        print("=" * 80)
        print("🧠 MENTAL HEALTH COUNSELING AI - COMMAND LINE INTERFACE")
        print("=" * 80)
        
        # Detect device
        if torch.cuda.is_available():
            self.device = "cuda"
            print(f"\n🎮 GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            self.device = "cpu"
            print("\n💻 Using CPU (GPU not available - responses may be slower)")
        
        print(f"\n📦 Loading model from: {self.model_path}")
        print("   This may take a minute...")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            print("   ✓ Tokenizer loaded")
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            print("   ✓ Model loaded successfully")
            
            print("\n✅ Ready to chat!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ Error loading model: {e}")
            raise
    
    def format_prompt(self, message: str) -> str:
        """
        Format message using Mistral chat template with conversation history.
        
        Args:
            message: Current user message
        
        Returns:
            Formatted prompt string
        """
        formatted_messages = []
        
        # Add conversation history
        for msg in self.conversation_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                formatted_messages.append(f"[INST] {content} [/INST]")
            else:
                formatted_messages.append(content)
        
        # Add current message
        formatted_messages.append(f"[INST] {message} [/INST]")
        
        return " ".join(formatted_messages)
    
    def generate_response(
        self,
        message: str,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate a response to the user's message.
        
        Args:
            message: User's input message
            max_length: Maximum length of generated response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
        
        Returns:
            Generated response string
        """
        try:
            # Format prompt
            prompt = self.format_prompt(message)
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract assistant's response
            if "[/INST]" in full_response:
                response = full_response.split("[/INST]")[-1].strip()
            else:
                response = full_response.strip()
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(self):
        """Run the interactive chat loop."""
        print("\n💬 Chat Interface")
        print("-" * 80)
        print("Commands:")
        print("  • Type your message and press Enter to chat")
        print("  • 'clear' - Clear conversation history")
        print("  • 'history' - Show conversation history")
        print("  • 'quit' or 'exit' - Exit the chat")
        print("-" * 80)
        print("\nStart chatting! I'm here to support you.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for chatting. Take care!")
                    break
                
                elif user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("\n🔄 Conversation history cleared.\n")
                    continue
                
                elif user_input.lower() == 'history':
                    if not self.conversation_history:
                        print("\n📭 No conversation history yet.\n")
                    else:
                        print("\n📜 Conversation History:")
                        print("-" * 80)
                        for i, msg in enumerate(self.conversation_history, 1):
                            role = "You" if msg["role"] == "user" else "AI"
                            print(f"{i}. {role}: {msg['content']}")
                        print("-" * 80 + "\n")
                    continue
                
                # Generate response
                print("\n🤔 Thinking...", end="", flush=True)
                response = self.generate_response(user_input)
                print("\r" + " " * 20 + "\r", end="")  # Clear "Thinking..." message
                
                # Display response
                print(f"AI: {response}\n")
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": response})
                
                # Limit history to last 10 exchanges (20 messages)
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

def main():
    """Main execution function."""
    
    # Get model path from environment or use default
    model_path = os.getenv("MODEL_PATH", "./merged_mental_health_model")
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Error: Model not found at {model_path}")
        print("\nPlease ensure you have:")
        print("  1. Run merge_model.py to create the merged model")
        print(f"  2. The model is saved in: {model_path}")
        print("\nAlternatively, set MODEL_PATH environment variable to your model location.")
        return 1
    
    try:
        # Initialize and load chatbot
        chatbot = MentalHealthChatbot(model_path)
        chatbot.load_model()
        
        # Start chat interface
        chatbot.chat()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
