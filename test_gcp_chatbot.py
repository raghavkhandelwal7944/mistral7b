"""
Simple Python client to test your GCP-hosted Mental Health Chatbot.

Usage:
    1. Update API_URL with your GCP VM's external IP
    2. Run: python test_gcp_chatbot.py

Features:
    - Interactive chat loop
    - Conversation history
    - Error handling
    - Pretty output
"""

import json
import sys

import requests

# TODO: Replace with your GCP VM's external IP after deployment
API_URL = "http://YOUR_VM_EXTERNAL_IP:8000/chat"

def chat(message: str, max_length: int = 512) -> dict:
    """Send a message to the chatbot API."""
    try:
        response = requests.post(
            API_URL,
            json={
                "message": message,
                "max_length": max_length,
                "temperature": 0.7,
                "top_p": 0.9
            },
            timeout=60  # Wait up to 60 seconds for response
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Is it running?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Model may still be loading."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def main():
    """Interactive chat loop."""
    print("=" * 80)
    print("🧠 MENTAL HEALTH CHATBOT - GCP CLIENT")
    print("=" * 80)
    print(f"\n📡 Connecting to: {API_URL}")
    
    # Test connection
    print("🔍 Testing connection...")
    health_url = API_URL.replace("/chat", "/health")
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is online!\n")
        else:
            print("⚠️  Server responded but may not be ready.\n")
    except:
        print("❌ Cannot connect to server. Check the URL and VM status.\n")
        print("To get your VM's external IP:")
        print("  1. Go to GCP Console → Compute Engine → VM instances")
        print("  2. Find 'External IP' column")
        print("  3. Update API_URL in this script\n")
        sys.exit(1)
    
    print("💬 Chat Interface")
    print("-" * 80)
    print("Commands:")
    print("  • Type your message and press Enter to chat")
    print("  • 'quit' or 'exit' - Exit the chat")
    print("-" * 80)
    print("\nStart chatting! Type your message below.\n")
    
    conversation_history = []
    
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
            
            # Send to API
            print("\n🤔 Thinking...", end="", flush=True)
            result = chat(user_input)
            print("\r" + " " * 20 + "\r", end="")  # Clear "Thinking..."
            
            # Display response
            if "error" in result:
                print(f"❌ Error: {result['error']}\n")
            elif "response" in result:
                response = result["response"]
                print(f"AI: {response}\n")
                conversation_history.append({"user": user_input, "ai": response})
            else:
                print(f"⚠️  Unexpected response: {result}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
