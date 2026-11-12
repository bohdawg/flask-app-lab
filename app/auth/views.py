from flask import render_template, request, session, flash, redirect, url_for, make_response
from . import auth_bp

USERNAME = "user1"
PASSWORD = "1234"

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["username"] = username
            flash("Ви успішно увійшли!", "success")
            return redirect(url_for("auth.profile"))

        flash("Неправильний логін або пароль", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/profile")
def profile():
    if "username" not in session:
        flash("Ви не ввійшли!", "warning")
        return redirect(url_for("auth.login"))
    theme = request.cookies.get("theme", "light")
    return render_template("profile.html", username=session["username"],
                       cookies=request.cookies, theme=theme)

@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Ви вийшли з системи", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/add_cookie", methods=["POST"])
def add_cookie():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    key = request.form.get("key")
    value = request.form.get("value")
    max_age = request.form.get("max_age", type=int)

    response = make_response(redirect(url_for("auth.profile")))
    response.set_cookie(key, value, max_age=max_age)
    flash(f"Кукі '{key}' додано", "success")
    return response


@auth_bp.route("/delete_cookie", methods=["POST"])
def delete_cookie():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    key = request.form.get("key")
    response = make_response(redirect(url_for("auth.profile")))
    response.delete_cookie(key)
    flash(f"Кукі '{key}' видалено", "success")
    return response


@auth_bp.route("/delete_all_cookies", methods=["POST"])
def delete_all_cookies():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    response = make_response(redirect(url_for("auth.profile")))
    for key in request.cookies:
        if key != "session":
            response.delete_cookie(key)
    flash("Усі кукі видалено", "success")
    return response

@auth_bp.route("/theme/<color>")
def set_theme(color):
    if ("username" not in session):
        return redirect(url_for("auth.login"))
    response = make_response(redirect(url_for("auth.profile")))
    response.set_cookie("theme", color, max_age=60*60*24*354)
    return response