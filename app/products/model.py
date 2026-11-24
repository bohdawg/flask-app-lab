import os
from datetime import datetime
from tinydb import TinyDB
from .. import app

TABLE_NAME = "products"

def get_db():
    """Відкриває JSON-сховище TinyDB (каталог data/ створюється автоматично)."""
    path = app.config["PRODUCTS_DB_PATH"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return TinyDB(path, indent=4, ensure_ascii=False, encoding="utf-8")

def init_db():
    """Ініціалізує сховище: створює файл products.json і таблицю товарів."""
    with get_db() as db:
        db.table(TABLE_NAME)

def get_products():
    with get_db() as db:
        return db.table(TABLE_NAME).all()

def get_product(product_id):
    with get_db() as db:
        return db.table(TABLE_NAME).get(doc_id=product_id)

def create_product(data):
    """Додає товар, автоматично встановлює id і created_at. Повертає id."""
    with get_db() as db:
        table = db.table(TABLE_NAME)
        product_id = table.insert({
            **data,
            "created_at": datetime.now().isoformat(timespec="seconds")
        })
        table.update({"id": product_id}, doc_ids=[product_id])
    return product_id

def update_product(product_id, data):
    """Оновлює поля товару (id і created_at не змінюються)."""
    with get_db() as db:
        db.table(TABLE_NAME).update(data, doc_ids=[product_id])

def delete_product(product_id):
    with get_db() as db:
        db.table(TABLE_NAME).remove(doc_ids=[product_id])

init_db()
