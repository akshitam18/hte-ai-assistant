"""
utils.py

Contains helper functions used across the backend.
"""

import os
from datetime import datetime
from fastapi import UploadFile

from config import DOCUMENTS_FOLDER, ALLOWED_EXTENSIONS


# ==========================
# CHECK FILE EXTENSION
# ==========================

def allowed_file(filename: str) -> bool:
    """
    Returns True if the uploaded file has an allowed extension.
    """

    extension = os.path.splitext(filename)[1].lower()
    return extension in ALLOWED_EXTENSIONS


# ==========================
# GENERATE UNIQUE FILE NAME
# ==========================

def generate_unique_filename(filename: str) -> str:
    """
    Adds a timestamp to avoid duplicate filenames.
    """

    name, extension = os.path.splitext(filename)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"{name}_{timestamp}{extension}"


# ==========================
# SAVE PDF
# ==========================

def save_uploaded_file(file: UploadFile) -> str:
    """
    Saves the uploaded PDF inside the documents folder.

    Returns the saved filename.
    """

    if file.filename is None:
        raise ValueError("Filename is missing.")

    filename = generate_unique_filename(file.filename)

    file_path = os.path.join(
        DOCUMENTS_FOLDER,
        filename
    )

    with open(file_path, "wb") as pdf_file:
        pdf_file.write(file.file.read())

    return filename