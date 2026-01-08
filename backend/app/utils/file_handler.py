import os
import uuid
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("uploads")

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    """Saves a file to local disk and returns the relative path."""
    # Generate a unique filename to prevent overwrites
    extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            # Read file in chunks to be memory efficient
            while content := await upload_file.read(1024 * 1024): # 1MB chunks
                buffer.write(content)
        return str(file_path)
    finally:
        await upload_file.seek(0) # Reset file pointer for later use (e.g. AI analysis)