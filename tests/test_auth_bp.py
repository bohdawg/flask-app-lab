import unittest
from app import app

PREFIX = "/auth"
USERNAME = "user1"
PASSWORD = "1234"

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування клієнта тестування перед кожним тестом."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def login(self, username=USERNAME, password=PASSWORD):
        """Допоміжний метод: відправляє форму входу."""
        return self.client.post(
            f"{PREFIX}/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_login_page(self):
        """Тест маршруту auth/login (GET): є форма з полями."""
        response = self.client.get(f"{PREFIX}/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="username"', response.data)
        self.assertIn(b'name="password"', response.data)

    def test_login_success_redirects_to_profile(self):
        """Вірні дані: redirect на profile."""
        response = self.client.post(
            f"{PREFIX}/login",
            data={"username": USERNAME, "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(f"{PREFIX}/profile"))

    def test_login_success_saves_session_and_flash(self):
        """Вірні дані: користувач у сесії, на profile є flash і привітання."""
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ви успішно увійшли!".encode(), response.data)
        self.assertIn(f"Ласкаво просимо до сторінки {USERNAME}".encode(), response.data)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["username"], USERNAME)

    def test_login_wrong_password(self):
        """Невірний пароль: повернення на login з flash-помилкою."""
        response = self.login(password="wrong")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Неправильний логін або пароль".encode(), response.data)
        self.assertIn(b'name="username"', response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn("username", sess)

    def test_login_wrong_username(self):
        """Невірний username: користувача в сесії немає."""
        response = self.login(username="nobody")
        self.assertIn("Неправильний логін або пароль".encode(), response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn("username", sess)

    def test_profile_without_login(self):
        """Profile без входу: redirect на login."""
        response = self.client.get(f"{PREFIX}/profile")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(f"{PREFIX}/login"))

    def test_profile_without_login_flash(self):
        """Profile без входу: на login показується flash."""
        response = self.client.get(f"{PREFIX}/profile", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ви не ввійшли!".encode(), response.data)

    def test_profile_after_login(self):
        """Profile після входу: привітання з іменем із сесії."""
        self.login()
        response = self.client.get(f"{PREFIX}/profile")
        self.assertEqual(response.status_code, 200)
        self.assertIn(USERNAME.encode(), response.data)

    def test_logout(self):
        """Тест маршруту auth/logout: сесія очищається, redirect на login."""
        self.login()
        response = self.client.get(f"{PREFIX}/logout")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(f"{PREFIX}/login"))
        with self.client.session_transaction() as sess:
            self.assertNotIn("username", sess)

    def test_profile_after_logout(self):
        """Після виходу profile знову недоступний."""
        self.login()
        self.client.get(f"{PREFIX}/logout")
        response = self.client.get(f"{PREFIX}/profile")
        self.assertEqual(response.status_code, 302)


    def test_add_cookie(self):
        """Додавання кукі: flash, кукі збережена, видно в таблиці."""
        self.login()
        response = self.client.post(
            f"{PREFIX}/add_cookie",
            data={"key": "lang", "value": "uk", "max_age": "3600"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("додано".encode(), response.data)
        self.assertIn(b"<td>lang</td>", response.data)
        self.assertEqual(self.client.get_cookie("lang").value, "uk")

    def test_add_cookie_without_max_age(self):
        """Додавання кукі без терміну дії теж працює."""
        self.login()
        self.client.post(
            f"{PREFIX}/add_cookie",
            data={"key": "color", "value": "red", "max_age": ""},
        )
        self.assertEqual(self.client.get_cookie("color").value, "red")

    def test_delete_cookie(self):
        """Видалення кукі за ключем."""
        self.login()
        self.client.post(f"{PREFIX}/add_cookie", data={"key": "tmp", "value": "1"})
        response = self.client.post(
            f"{PREFIX}/delete_cookie", data={"key": "tmp"}, follow_redirects=True
        )
        self.assertIn("видалено".encode(), response.data)
        self.assertIsNone(self.client.get_cookie("tmp"))
        self.assertNotIn(b"<td>tmp</td>", response.data)

    def test_delete_all_cookies(self):
        """Видалення всіх кукі: session лишається, користувач не розлогінений."""
        self.login()
        self.client.post(f"{PREFIX}/add_cookie", data={"key": "a", "value": "1"})
        self.client.post(f"{PREFIX}/add_cookie", data={"key": "b", "value": "2"})
        response = self.client.post(f"{PREFIX}/delete_all_cookies", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.get_cookie("a"))
        self.assertIsNone(self.client.get_cookie("b"))
        self.assertIsNotNone(self.client.get_cookie("session"))
        self.assertIn(USERNAME.encode(), response.data)

    def test_cookie_routes_require_login(self):
        """Без входу всі маршрути кукі ведуть на login."""
        for route in ("add_cookie", "delete_cookie", "delete_all_cookies"):
            response = self.client.post(f"{PREFIX}/{route}", data={"key": "x", "value": "1"})
            self.assertEqual(response.status_code, 302, route)
            self.assertTrue(response.headers["Location"].endswith(f"{PREFIX}/login"), route)
        self.assertIsNone(self.client.get_cookie("x"))


    def test_default_theme_is_light(self):
        """Без вибору схема світла."""
        self.login()
        response = self.client.get(f"{PREFIX}/profile")
        self.assertIn(b'data-theme="light"', response.data)

    def test_set_theme_dark(self):
        """Вибір темної схеми: redirect на profile, кукі збережена, сторінка темна."""
        self.login()
        response = self.client.get(f"{PREFIX}/theme/dark")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(f"{PREFIX}/profile"))
        self.assertEqual(self.client.get_cookie("theme").value, "dark")

        response = self.client.get(f"{PREFIX}/profile")
        self.assertIn(b'="dark"', response.data)

    def test_theme_is_remembered(self):
        """Схема зберігається при наступних відвідуваннях (кукі лишається)."""
        self.login()
        self.client.get(f"{PREFIX}/theme/dark")
        self.client.get(f"{PREFIX}/theme/light")
        response = self.client.get(f"{PREFIX}/profile")
        self.assertIn(b'data-theme="light"', response.data)
        self.assertEqual(self.client.get_cookie("theme").value, "light")

    def test_theme_requires_login(self):
        """Без входу вибір схеми недоступний."""
        response = self.client.get(f"{PREFIX}/theme/dark")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(f"{PREFIX}/login"))


if __name__ == "__main__":
    unittest.main()