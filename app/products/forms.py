from decimal import Decimal
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, ValidationError

CATEGORIES = ["Електроніка", "Одяг", "Книги", "Дім і сад", "Спорт"]


class ProductForm(FlaskForm):
    name = StringField(
        "Назва",
        validators=[
            DataRequired(message="Вкажіть назву товару"),
            Length(min=3, message="Назва має містити щонайменше 3 символи")
        ]
    )
    content = TextAreaField(
        "Опис",
        validators=[DataRequired(message="Введіть опис товару")],
        render_kw={"rows": 5, "cols": 40}
    )
    price = DecimalField(
        "Ціна, грн",
        places=2,
        validators=[
            InputRequired(message="Вкажіть ціну"),
            NumberRange(min=Decimal("0.01"), message="Ціна має бути додатною")
        ]
    )
    category = SelectField("Категорія", choices=[(c, c) for c in CATEGORIES])
    quantity = IntegerField(
        "Кількість",
        validators=[
            InputRequired(message="Вкажіть кількість"),
            NumberRange(min=0, message="Кількість не може бути від’ємною")
        ]
    )
    image = FileField(
        "Зображення",
        validators=[FileAllowed(["png", "jpg", "jpeg"], "Дозволені лише файли PNG, JPG, JPEG")]
    )
    submit = SubmitField("Зберегти")

    def validate_price(self, field):
        if field.data is not None and field.data.is_finite() and field.data.as_tuple().exponent < -2:
            raise ValidationError("Ціна може мати не більше двох знаків після коми")


class DeleteProductForm(FlaskForm):
    submit = SubmitField("Видалити")
