import unittest
from datetime import datetime
from app import create_app, db
from app.posts.models import Post

PREFIX = "/post"
VALID_DATA = {"title": "My first post", "content": "This is TDD!", "is_active": "y",
              "publish_date": "2026-11-24T12:00", "category": "tech"}

class PostTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    def create_post(self, **overrides):
        """Допоміжний метод: створює пост напряму в БД, повертає його id."""
        data = {
            "title": "Test post",
            "content": "Test content",
            "category": "tech",
            "posted": datetime(2026, 11, 24, 12, 0),
            **overrides,
        }
        with self.app.app_context():
            post = Post(**data)
            db.session.add(post)
            db.session.commit()
            return post.id

    def get_posts(self):
        """Допоміжний метод: усі пости з БД."""
        with self.app.app_context():
            return db.session.scalars(db.select(Post)).all()

    def test_create_post_page(self):
        """GET /post/create: є форма з полями."""
        response = self.client.get(f"{PREFIX}/create")
        self.assertEqual(response.status_code, 200)
        for field in ("title", "content", "is_active", "publish_date", "category"):
            self.assertIn(f'name="{field}"'.encode(), response.data)

    def test_create_post(self):
        """POST /post/create: пост збережено, redirect, flash."""
        response = self.client.post(f"{PREFIX}/create", data=VALID_DATA, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("успішно додано".encode(), response.data)

        posts = self.get_posts()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, "My first post")
        self.assertEqual(posts[0].content, "This is TDD!")
        self.assertEqual(posts[0].category, "tech")
        self.assertTrue(posts[0].is_active)
        self.assertEqual(posts[0].posted, datetime(2026, 11, 24, 12, 0))
        self.assertEqual(posts[0].author, "Anonymous")

    def test_create_post_redirect(self):
        """Після створення - redirect на список (PRG)."""
        response = self.client.post(f"{PREFIX}/create", data=VALID_DATA)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(PREFIX))

    def test_create_post_author_from_session(self):
        """Автор поста - користувач із сесії."""
        with self.client.session_transaction() as sess:
            sess["username"] = "user1"
        self.client.post(f"{PREFIX}/create", data=VALID_DATA)
        self.assertEqual(self.get_posts()[0].author, "user1")

    def test_create_post_invalid(self):
        """Занадто короткий заголовок: помилка, пост не збережено."""
        response = self.client.post(f"{PREFIX}/create", data={**VALID_DATA, "title": "a"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("від 2 до 150".encode(), response.data)
        self.assertIn("Перевірте правильність".encode(), response.data)
        self.assertEqual(self.get_posts(), [])

    def test_create_post_wrong_category(self):
        """Категорія поза списком: помилка, пост не збережено."""
        response = self.client.post(f"{PREFIX}/create", data={**VALID_DATA, "category": "unknown"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_posts(), [])

    def test_list_posts(self):
        """GET /post: видно пости, новіші - першими."""
        self.create_post(title="Older post", posted=datetime(2026, 11, 1, 10, 0))
        self.create_post(title="Newer post", posted=datetime(2026, 11, 20, 10, 0))
        response = self.client.get(PREFIX)
        self.assertEqual(response.status_code, 200)
        html = response.data.decode()
        self.assertIn("Older post", html)
        self.assertLess(html.index("Newer post"), html.index("Older post"))

    def test_list_posts_hides_inactive(self):
        """Неактивні пости у списку не відображаються."""
        self.create_post(title="Visible post", is_active=True)
        self.create_post(title="Hidden post", is_active=False)
        response = self.client.get(PREFIX)
        self.assertIn(b"Visible post", response.data)
        self.assertNotIn(b"Hidden post", response.data)

    def test_list_posts_empty(self):
        """Порожній список: повідомлення і кнопка Add Post."""
        response = self.client.get(PREFIX)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Постів поки немає".encode(), response.data)
        self.assertIn(b"Add Post", response.data)

    def test_view_post_detail(self):
        """GET /post/<id>: повна інформація про пост."""
        post_id = self.create_post(title="Detailed post", content="Full content", author="Alice")
        response = self.client.get(f"{PREFIX}/{post_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Detailed post", response.data)
        self.assertIn(b"Full content", response.data)
        self.assertIn(b"Alice", response.data)
        self.assertIn(b"tech", response.data)