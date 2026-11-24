import os
import tempfile
import unittest
from app import app

PREFIX = "/product"

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        """Тимчасова БД і вимкнений CSRF перед кожним тестом."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["PRODUCTS_DB_PATH"] = os.path.join(self.tmp_dir.name, "products.json")
        self.client = app.test_client()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_products_list_empty(self):
        """Тест маршруту /product: товарів ще немає."""
        response = self.client.get(PREFIX)
        self.assertEqual(response.status_code, 200)
        self.assertIn("товари відсутні".encode(), response.data)

    def test_detailed_product_not_found(self):
        """Неіснуючий товар: 404 і повідомлення."""
        response = self.client.get(f"{PREFIX}/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Товар не знайдено".encode(), response.data)

if __name__ == "__main__":
    unittest.main()