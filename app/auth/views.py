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
    return render_template("profile.html", username=session["username"])

@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Ви вийшли з системи", "info")
    return redirect(url_for("auth.login"))