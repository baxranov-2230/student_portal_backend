from fastapi import UploadFile 
import os
from uuid import uuid4

async def save_uploaded_file(file: UploadFile , upload_dir : str | None = "uploads"):
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return file_path
