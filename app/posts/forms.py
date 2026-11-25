from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateTimeLocalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

CATEGORIES = [
    ("news", "Новини"),
    ("publication", "Публікація"),
    ("tech", "Технології"),
    ("other", "Інше"),
]


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[
            DataRequired(message="Вкажіть заголовок"),
            Length(min=2, max=150, message="Заголовок має містити від 2 до 150 символів")
        ]
    )
    content = TextAreaField(
        "Текст",
        render_kw={"rows": 5, "cols": 40},
        validators=[DataRequired(message="Введіть текст поста")]
    )
    is_active = BooleanField("Активний пост", default=True)
    publish_date = DateTimeLocalField(
        "Дата публікації",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,
        validators=[DataRequired(message="Вкажіть дату публікації")]
    )
    category = SelectField(
        "Категорія",
        choices=CATEGORIES,
        validators=[DataRequired(message="Оберіть категорію")]
    )
    submit = SubmitField("Зберегти")
