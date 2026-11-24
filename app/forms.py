from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp

SUBJECTS = ["Загальне запитання", "Співпраця", "Відгук", "Інше"]


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Вкажіть ім'я"),
            Length(min=4, max=10, message="Ім'я має містити від 4 до 10 символів")
        ]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Вкажіть email"),
            Email(message="Некоректна адреса електронної пошти")
        ]
    )
    phone = StringField(
        "Телефон",
        validators=[Regexp(r"^\+380\d{9}$", message="Формат телефону: +380XXXXXXXXX")]
    )
    subject = SelectField("Тема", choices=[(s, s) for s in SUBJECTS])
    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Введіть повідомлення"),
            Length(max=500, message="Повідомлення має містити не більше 500 символів")
        ]
    )
    submit = SubmitField("Надіслати")
