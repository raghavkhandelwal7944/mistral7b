"""
Robust uploader for Hugging Face model folders with retries.

Usage:
    python hf_upload_retry.py --repo raghav-7944/mensmentalhealthchatbot --folder merged_mental_health_model --token <HF_TOKEN>

This uploads each file in the folder sequentially and retries failed uploads with exponential backoff.
Useful when the CLI upload fails due to intermittent network / S3 PUT errors.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import List

from huggingface_hub import upload_file


def iter_files(folder: str) -> List[str]:
    files = []
    for root, _, filenames in os.walk(folder):
        for fn in filenames:
            files.append(os.path.join(root, fn))
    files.sort()
    return files


def upload_with_retries(
    local_path: str,
    repo_id: str,
    path_in_repo: str,
    token: str | None = None,
    max_retries: int = 5,
):
    backoff = 2
    for attempt in range(1, max_retries + 1):
        try:
            upload_file(
                path_or_fileobj=local_path,
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type="model",
                token=token,
            )
            return True

        except Exception as e:
            print(f"Upload failed (attempt {attempt}/{max_retries}) for {local_path}: {e}")
            if attempt == max_retries:
                return False
            sleep = backoff ** attempt
            print(f"  -> Retrying in {sleep}s...")
            time.sleep(sleep)


def main():
    parser = argparse.ArgumentParser(description="Upload folder to HF with retries")
    parser.add_argument("--repo", required=True, help="Hugging Face repo id (user/repo)")
    parser.add_argument("--folder", required=True, help="Local folder to upload")
    parser.add_argument("--token", default=os.getenv("HF_TOKEN"), help="Hugging Face token (or set HF_TOKEN env)")
    parser.add_argument("--max-retries", type=int, default=5)
    args = parser.parse_args()

    folder = args.folder
    repo = args.repo
    token = args.token

    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        sys.exit(2)

    files = iter_files(folder)
    print(f"Found {len(files)} files to upload from '{folder}' to repo '{repo}'")

    failed: List[str] = []
    for local_path in files:
        relative = os.path.relpath(local_path, folder).replace("\\", "/")
        path_in_repo = relative
        print(f"Uploading: {relative}")
        ok = upload_with_retries(local_path, repo, path_in_repo, token=token, max_retries=args.max_retries)
        if not ok:
            failed.append(local_path)

    if failed:
        print("\nThe following files failed to upload:")
        for p in failed:
            print("  ", p)
        print("\nSuggestions: retry the script, try from a different network, or upload from a cloud VM with a stable connection.")
        sys.exit(1)

    print("\nAll files uploaded successfully.")


if __name__ == "__main__":
    main()
