import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування клієнта тестування перед кожним тестом."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_products_list_page(self):
        """Тест маршруту /."""
        response = self.client.get("products/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)

    def test_detailed_product_pages_1(self):
        """Тест маршруту products/id/1."""
        response = self.client.get("products/id/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)

if __name__ == "__main__":
    unittest.main()