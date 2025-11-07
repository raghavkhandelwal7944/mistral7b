"""
Run this in Google Colab to upload your model to Hugging Face quickly.

Instructions:
1. Go to https://colab.research.google.com/
2. Create a new notebook
3. Copy and paste this entire code into a cell
4. Run it
5. When prompted, upload your merged_mental_health_model folder (as a zip)
6. Enter your HF token when asked
"""

# Install dependencies
!pip install -q huggingface_hub

# Upload your model folder (zipped)
from google.colab import files
import zipfile
import os

print("📦 Please upload your merged_mental_health_model folder as a ZIP file...")
uploaded = files.upload()

# Extract the zip
zip_name = list(uploaded.keys())[0]
print(f"Extracting {zip_name}...")
with zipfile.ZipFile(zip_name, 'r') as zip_ref:
    zip_ref.extractall('.')

# Find the extracted folder
model_folder = None
for item in os.listdir('.'):
    if os.path.isdir(item) and 'model' in item.lower():
        model_folder = item
        break

if not model_folder:
    print("❌ Could not find model folder. Please check the zip contents.")
    exit(1)

print(f"✅ Found model folder: {model_folder}")

# Login to Hugging Face
from huggingface_hub import login, upload_folder
import getpass

hf_token = getpass.getpass("Enter your Hugging Face token (with write access): ")
login(token=hf_token)

# Upload to HF
repo_id = "raghav-7944/mensmentalhealthchatbot"
print(f"\n📤 Uploading {model_folder} to {repo_id}...")
print("This may take a few minutes...")

try:
    upload_folder(
        folder_path=model_folder,
        repo_id=repo_id,
        repo_type="model",
        token=hf_token
    )
    print(f"\n✅ Successfully uploaded to https://huggingface.co/{repo_id}")
    print("\nYou can now use your model from anywhere with:")
    print(f"  from transformers import AutoModelForCausalLM, AutoTokenizer")
    print(f"  model = AutoModelForCausalLM.from_pretrained('{repo_id}')")
    print(f"  tokenizer = AutoTokenizer.from_pretrained('{repo_id}')")
    
except Exception as e:
    print(f"❌ Error: {e}")
