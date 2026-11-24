from flask import render_template, redirect, url_for, flash
from . import product_bp
from .forms import ProductForm, DeleteProductForm
from .model import get_products, get_product, create_product, update_product, delete_product
from .utils import save_image, delete_image

@product_bp.route("")
def products():
    return render_template("products.html", title="Товари", products=get_products())

@product_bp.route("/<int:id>")
def detailed(id):
    product = get_product(id)
    if product is None:
        return render_template("detailed_product.html", title="Товар не знайдено", product=None), 404
    return render_template(
        "detailed_product.html",
        title=product["name"],
        product=product,
        delete_form=DeleteProductForm()
    )

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

@product_bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    product = get_product(id)
    if product is None:
        flash("Товар не знайдено", "danger")
        return redirect(url_for("products.products"))

    form = ProductForm(data={
        "name": product["name"],
        "content": product["content"],
        "price": product["price"],
        "category": product["category"],
        "quantity": product["quantity"]
    })
    if form.validate_on_submit():
        image = product["image"]
        if form.image.data:
            delete_image(image)
            image = save_image(form.image.data)
        update_product(id, {
            "name": form.name.data,
            "content": form.content.data,
            "price": float(form.price.data),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image
        })
        flash(f"Товар «{form.name.data}» оновлено", "success")
        return redirect(url_for("products.detailed", id=id))
    return render_template(
        "product_form.html",
        title="Редагувати товар",
        form=form,
        product=product,
        cancel_url=url_for("products.detailed", id=id)
    )

@product_bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    form = DeleteProductForm()
    if not form.validate_on_submit():
        flash("Не вдалося видалити товар", "danger")
        return redirect(url_for("products.products"))

    product = get_product(id)
    if product is None:
        flash("Товар не знайдено", "danger")
    else:
        delete_image(product["image"])
        delete_product(id)
        flash(f"Товар «{product['name']}» видалено", "success")
    return redirect(url_for("products.products"))
