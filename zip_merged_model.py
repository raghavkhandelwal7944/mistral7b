"""
Zip the merged_mental_health_model folder for easy upload to Colab or Hugging Face.

Usage:
    python zip_merged_model.py

This will create merged_mental_health_model.zip in the current folder.
"""
import os
import zipfile

folder = "merged_mental_health_model"
zip_name = "merged_mental_health_model.zip"

if not os.path.isdir(folder):
    print(f"❌ Folder not found: {folder}")
    exit(1)

print(f"Zipping folder '{folder}' to '{zip_name}'...")
with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(folder):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, folder)
            zipf.write(abs_path, os.path.join(folder, rel_path))
print(f"✅ Done! Created {zip_name}")
