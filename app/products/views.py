from flask import render_template
from . import product_bp
from .model import get_products, get_product

@product_bp.route("")
def products():
    return render_template("products.html", title="Товари", products=get_products())

@product_bp.route("/<int:id>")
def detailed(id):
    product = get_product(id)
    if product is None:
        return render_template("detailed_product.html", title="Товар не знайдено", product=None), 404
    return render_template("detailed_product.html", title=product["name"], product=product)