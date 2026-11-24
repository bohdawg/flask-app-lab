import io
import os
import tempfile
import unittest
from app import app
from app.products.forms import CATEGORIES
from app.products.model import get_products, get_product
from app.products.utils import delete_image

PREFIX = "/product"

VALID_DATA = {
    "name": "Laptop",
    "content": "Потужний ноутбук з процесором Intel Core i7.",
    "price": "1200.50",
    "category": CATEGORIES[0],
    "quantity": "5",
}

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        """Тимчасова БД і вимкнений CSRF перед кожним тестом."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["PRODUCTS_DB_PATH"] = os.path.join(self.tmp_dir.name, "products.json")
        self.client = app.test_client()

    def tearDown(self):
        """Видаляємо завантажені зображення і тимчасову БД."""
        for product in get_products():
            delete_image(product.get("image"))
        self.tmp_dir.cleanup()

    def add_product(self, follow_redirects=False, **overrides):
        """Допоміжний метод: відправляє форму додавання товару."""
        data = {**VALID_DATA, **overrides}
        return self.client.post(
            f"{PREFIX}/add",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=follow_redirects,
        )

    def test_products_list_empty(self):
        """Тест маршруту /product: товарів ще немає."""
        response = self.client.get(PREFIX)
        self.assertEqual(response.status_code, 200)
        self.assertIn("товари відсутні".encode(), response.data)

    def test_add_page(self):
        """Тест GET /product/add: є форма з полями."""
        response = self.client.get(f"{PREFIX}/add")
        self.assertEqual(response.status_code, 200)
        for field in ("name", "content", "price", "category", "quantity", "image"):
            self.assertIn(f'name="{field}"'.encode(), response.data)

    def test_add_product_success(self):
        """Вірні дані: redirect на список, flash, товар у БД з id і created_at."""
        response = self.add_product()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(PREFIX))

        products = get_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["id"], 1)
        self.assertEqual(products[0]["name"], "Laptop")
        self.assertEqual(products[0]["price"], 1200.5)
        self.assertIsNone(products[0]["image"])
        self.assertIn("created_at", products[0])

    def test_add_product_flash_and_list(self):
        """Після додавання на списку є flash і новий товар."""
        response = self.add_product(follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("успішно додано".encode(), response.data)
        self.assertIn(b"Laptop", response.data)
        self.assertIn("Немає зображення".encode(), response.data)

    def test_add_product_short_name(self):
        """Назва коротша за 3 символи: помилка, товар не збережено."""
        response = self.add_product(name="ab")
        self.assertEqual(response.status_code, 200)
        self.assertIn("щонайменше 3 символи".encode(), response.data)
        self.assertEqual(get_products(), [])

    def test_add_product_negative_price(self):
        """Від’ємна ціна: помилка валідації."""
        response = self.add_product(price="-5")
        self.assertIn("Ціна має бути додатною".encode(), response.data)
        self.assertEqual(get_products(), [])

    def test_add_product_price_three_decimals(self):
        """Ціна з трьома знаками після коми: помилка валідації."""
        response = self.add_product(price="10.999")
        self.assertIn("не більше двох знаків".encode(), response.data)
        self.assertEqual(get_products(), [])

    def test_add_product_negative_quantity(self):
        """Від’ємна кількість: помилка валідації."""
        response = self.add_product(quantity="-1")
        self.assertIn("не може бути від’ємною".encode(), response.data)
        self.assertEqual(get_products(), [])

    def test_add_product_zero_quantity(self):
        """Кількість 0 допустима."""
        response = self.add_product(quantity="0")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_products()[0]["quantity"], 0)

    def test_add_product_with_image(self):
        """Завантаження PNG: файл збережено, у БД відносний шлях."""
        response = self.add_product(image=(io.BytesIO(b"fake-png-data"), "photo.png"))
        self.assertEqual(response.status_code, 302)

        image = get_products()[0]["image"]
        self.assertTrue(image.startswith("uploads/"))
        self.assertTrue(image.endswith(".png"))

        page = self.client.get(PREFIX)
        self.assertIn(image.encode(), page.data)

    def test_add_product_wrong_image_format(self):
        """Файл не PNG/JPG/JPEG: помилка, товар не збережено."""
        response = self.add_product(image=(io.BytesIO(b"gif-data"), "photo.gif"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Дозволені лише файли".encode(), response.data)
        self.assertEqual(get_products(), [])

    def test_detailed_product_page(self):
        """Тест /product/<id>: повна інформація, включно з описом."""
        self.add_product()
        response = self.client.get(f"{PREFIX}/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn("Потужний ноутбук".encode(), response.data)

    def test_detailed_product_not_found(self):
        """Неіснуючий товар: 404 і повідомлення."""
        response = self.client.get(f"{PREFIX}/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Товар не знайдено".encode(), response.data)

    def test_edit_page_prefilled(self):
        """Тест GET /product/<id>/edit: форма з поточними даними."""
        self.add_product()
        response = self.client.get(f"{PREFIX}/1/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="Laptop"', response.data)
        self.assertIn(b'value="1200.50"', response.data)

    def test_edit_product_success(self):
        """Редагування: дані змінено, id і created_at залишились."""
        self.add_product()
        created_at = get_product(1)["created_at"]

        response = self.client.post(
            f"{PREFIX}/1/edit",
            data={**VALID_DATA, "name": "Gaming Laptop", "price": "1500", "quantity": "3"},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(f"{PREFIX}/1"))

        product = get_product(1)
        self.assertEqual(product["id"], 1)
        self.assertEqual(product["created_at"], created_at)
        self.assertEqual(product["name"], "Gaming Laptop")
        self.assertEqual(product["price"], 1500.0)
        self.assertEqual(product["quantity"], 3)

    def test_edit_product_keeps_and_replaces_image(self):
        """Без нового файлу зображення зберігається, з новим - замінюється."""
        self.add_product(image=(io.BytesIO(b"first"), "first.png"))
        old_image = get_product(1)["image"]

        self.client.post(f"{PREFIX}/1/edit", data=VALID_DATA, content_type="multipart/form-data")
        self.assertEqual(get_product(1)["image"], old_image)

        self.client.post(
            f"{PREFIX}/1/edit",
            data={**VALID_DATA, "image": (io.BytesIO(b"second"), "second.jpg")},
            content_type="multipart/form-data",
        )
        new_image = get_product(1)["image"]
        self.assertNotEqual(new_image, old_image)
        self.assertTrue(new_image.endswith(".jpg"))

    def test_edit_product_invalid(self):
        """Невалідні дані при редагуванні: помилка, товар без змін."""
        self.add_product()
        response = self.client.post(
            f"{PREFIX}/1/edit",
            data={**VALID_DATA, "name": "ab"},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("щонайменше 3 символи".encode(), response.data)
        self.assertEqual(get_product(1)["name"], "Laptop")

    def test_edit_product_not_found(self):
        """Редагування неіснуючого товару: redirect і flash."""
        response = self.client.get(f"{PREFIX}/999/edit", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Товар не знайдено".encode(), response.data)

    def test_delete_product(self):
        """Видалення через POST: товар зникає з БД, є flash."""
        self.add_product()
        response = self.client.post(f"{PREFIX}/1/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("видалено".encode(), response.data)
        self.assertIsNone(get_product(1))

    def test_delete_product_removes_image(self):
        """Разом з товаром видаляється файл зображення."""
        self.add_product(image=(io.BytesIO(b"data"), "photo.png"))
        image = get_product(1)["image"]
        from app.products import product_bp
        path = os.path.join(product_bp.static_folder, image)
        self.assertTrue(os.path.isfile(path))

        self.client.post(f"{PREFIX}/1/delete")
        self.assertFalse(os.path.isfile(path))

    def test_delete_product_not_found(self):
        """Видалення неіснуючого товару: flash-помилка."""
        response = self.client.post(f"{PREFIX}/999/delete", follow_redirects=True)
        self.assertIn("Товар не знайдено".encode(), response.data)

    def test_delete_product_get_not_allowed(self):
        """Видалення через GET заборонено."""
        self.add_product()
        response = self.client.get(f"{PREFIX}/1/delete")
        self.assertEqual(response.status_code, 405)
        self.assertIsNotNone(get_product(1))

    def test_ids_are_unique(self):
        """Кожен новий товар отримує новий id."""
        self.add_product()
        self.add_product(name="Phone")
        self.assertEqual([p["id"] for p in get_products()], [1, 2])

if __name__ == "__main__":
    unittest.main()
