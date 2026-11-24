import os
import uuid
from . import product_bp

UPLOAD_DIR = "uploads"

def save_image(file_storage):
    """Зберігає зображення під унікальним UUID-іменем, повертає відносний шлях."""
    if not file_storage:
        return None
    extension = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    upload_path = os.path.join(product_bp.static_folder, UPLOAD_DIR)
    os.makedirs(upload_path, exist_ok=True)
    file_storage.save(os.path.join(upload_path, filename))
    return f"{UPLOAD_DIR}/{filename}"

def delete_image(relative_path):
    """Видаляє файл зображення, якщо він існує."""
    if not relative_path:
        return
    full_path = os.path.join(product_bp.static_folder, relative_path)
    if os.path.isfile(full_path):
        os.remove(full_path)
