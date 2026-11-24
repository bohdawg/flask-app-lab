import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

debug=True
SECRET_KEY = "very-secret-key"

MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # максимальний розмір завантаження: 2 МБ
CONTACT_LOG_PATH = os.path.join(BASE_DIR, "logs", "contacts.log")
PRODUCTS_DB_PATH = os.path.join(BASE_DIR, "data", "products.json")
