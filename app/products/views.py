from flask import flash, redirect, render_template, url_for
from app.products.forms import ProductForm
from app.products.utils import save_image
from . import product_bp
from .model import create_product, get_products, get_product

@product_bp.route("")
def products():
    return render_template("products.html", title="Товари", products=get_products())

@product_bp.route("/<int:id>")
def detailed(id):
    product = get_product(id)
    if product is None:
        return render_template("detailed_product.html", title="Товар не знайдено", product=None), 404
    return render_template("detailed_product.html", title=product["name"], product=product)

@product_bp.route("/add", methods=["GET", "POST"])
def add():
    form = ProductForm()
    if form.validate_on_submit():
        create_product({
            "name": form.name.data,
            "content": form.content.data,
            "price": float(form.price.data),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": save_image(form.image.data)
        })
        flash(f"Товар «{form.name.data}» успішно додано", "success")
        return redirect(url_for("products.products"))
    return render_template(
        "product_form.html",
        title="Додати товар",
        form=form,
        product=None,
        cancel_url=url_for("products.products")
    )