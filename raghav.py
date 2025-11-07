"""
Main entry point for Mistral-7B Mental Health Counseling Model.
This file provides a unified interface to all components.
"""

import os
import sys


def print_menu():
    """Display the main menu."""
    print("\n" + "=" * 80)
    print("🧠 MISTRAL-7B MENTAL HEALTH COUNSELING MODEL")
    print("=" * 80)
    print("\nAvailable Components:\n")
    print("1. 🔀 Merge Model")
    print("   Combine LoRA adapter with base model")
    print("   File: merge_model.py")
    print()
    print("2. 🌐 FastAPI Server")
    print("   Deploy model as HTTP API service")
    print("   File: fastapi_server.py")
    print()
    print("3. 💬 Command-Line Chat")
    print("   Interactive terminal chat interface")
    print("   File: cli_chat.py")
    print()
    print("4. 📚 View Documentation")
    print("   Open README.md for detailed instructions")
    print()
    print("5. ❌ Exit")
    print("\n" + "=" * 80)

def run_component(choice: str):
    """
    Run the selected component.
    
    Args:
        choice: User's menu choice
    """
    if choice == "1":
        print("\n🔀 Starting Model Merger...\n")
        import merge_model
        merge_model.main()
    
    elif choice == "2":
        print("\n🌐 Starting FastAPI Server...\n")
        import fastapi_server
        fastapi_server.main()
    
    elif choice == "3":
        print("\n💬 Starting Command-Line Chat...\n")
        import cli_chat
        cli_chat.main()
    
    elif choice == "4":
        print("\n📚 Opening Documentation...\n")
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        if os.path.exists(readme_path):
            # Try to open README with default application
            if sys.platform == "win32":
                os.startfile(readme_path)
            elif sys.platform == "darwin":
                os.system(f"open {readme_path}")
            else:
                os.system(f"xdg-open {readme_path}")
            print("   ✓ README.md opened in default application")
        else:
            print("   ✗ README.md not found")
    
    elif choice == "5":
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice. Please select 1-5.\n")

def main():
    """Main entry point with interactive menu."""
    
    print("\n" + "=" * 80)
    print("🚀 WELCOME TO MISTRAL-7B MENTAL HEALTH COUNSELING MODEL")
    print("=" * 80)
    print("\nThis suite provides tools to:")
    print("  • Merge your fine-tuned LoRA adapter with the base model")
    print("  • Deploy the model as a production-ready API server")
    print("  • Chat with the model interactively in your terminal")
    print("\n" + "=" * 80)
    
    # Quick setup guide
    print("\n📋 QUICK START GUIDE:")
    print("-" * 80)
    print("1. First time? Run 'Merge Model' to create your standalone model")
    print("2. For API deployment: Run 'FastAPI Server'")
    print("3. For local testing: Run 'Command-Line Chat'")
    print("4. Read documentation for detailed instructions")
    print("-" * 80)
    
    # Check if merged model exists
    merged_model_path = "./merged_mental_health_model"
    if os.path.exists(merged_model_path):
        print("\n✅ Merged model found at:", merged_model_path)
    else:
        print("\n⚠️  Merged model not found. Please run 'Merge Model' first!")
    
    # Interactive menu loop
    while True:
        try:
            print_menu()
            choice = input("Select option (1-5): ").strip()
            
            if choice:
                run_component(choice)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user. Goodbye!\n")
            sys.exit(0)
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

# Alternative: Direct script execution
def run_script(script_name: str):
    """
    Run a specific script directly.
    
    Args:
        script_name: Name of the script to run ('merge', 'server', or 'chat')
    """
    scripts = {
        'merge': merge_model,
        'server': fastapi_server,
        'chat': cli_chat
    }
    
    if script_name in scripts:
        return scripts[script_name].main()
    else:
        print(f"Unknown script: {script_name}")
        print("Available: merge, server, chat")
        return 1

if __name__ == "__main__":
    # Check if a specific script was requested via command line
    if len(sys.argv) > 1:
        script_arg = sys.argv[1].lower()
        sys.exit(run_script(script_arg))
    else:
        # Run interactive menu
        main()
