from flask import render_template, request, redirect, url_for, flash, session
from app import db
from . import post_bp
from .forms import PostForm
from .models import Post

@post_bp.route("/post")
def all_posts():
    stmt = db.select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc())
    posts = db.session.scalars(stmt).all()
    return render_template("posts.html", posts=posts, title="Пости")

@post_bp.route("/post/create", methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            is_active=form.is_active.data,
            posted=form.publish_date.data,
            category=form.category.data,
            author=session.get("username", "Anonymous")
        )
        db.session.add(new_post)
        db.session.commit()
        flash(f"Пост «{new_post.title}» успішно додано", "success")
        return redirect(url_for(".all_posts"))
    elif request.method == "POST":
        flash("Перевірте правильність заповнення форми!", "danger")
    return render_template("add_post.html", form=form, title="Створити пост")

@post_bp.route("/post/<int:id>")
def detail_post(id):
    post = db.get_or_404(Post, id)
    return render_template("detail_post.html", post=post, title=post.title)

@post_bp.route("/post/<int:id>/update", methods=["GET", "POST"])
def edit_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)  # заповнення форми даними поста
    if request.method == "GET":
        form.publish_date.data = post.posted  # назви атрибутів не співпадають
    if form.validate_on_submit():
        form.populate_obj(post)  # оновлення об'єкта post з форми
        post.posted = form.publish_date.data
        db.session.commit()
        flash("Пост оновлено!", "success")
        return redirect(url_for(".detail_post", id=post.id))
    elif request.method == "POST":
        flash("Перевірте правильність заповнення форми!", "danger")
    return render_template("add_post.html", form=form, title="Редагувати пост")

@post_bp.route("/post/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        flash("Пост успішно видалено.", "danger")
        return redirect(url_for(".all_posts"))
    return render_template("delete_confirm.html", post=post, title="Видалення поста")
