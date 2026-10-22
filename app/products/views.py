from flask import render_template
from . import product_bp
from .model import products as products_list

@product_bp.route("/")
def products():
    return render_template("products.html", products=products_list)

@product_bp.route("/id/<int:id>")
def detailed(id):
    product = next((item for item in products_list if item["id"] == id), None)
    return render_template("detailed_product.html", product=product)