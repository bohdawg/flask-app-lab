import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .forms import ContactForm

main_bp = Blueprint("main", __name__)

def write_contact_log(form):
    """Дописує дані контактної форми у log-файл."""
    path = current_app.config["CONTACT_LOG_PATH"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record = {
        "name": form.name.data,
        "email": form.email.data,
        "phone": form.phone.data,
        "subject": form.subject.data,
        "message": form.message.data
    }
    with open(path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {json.dumps(record, ensure_ascii=False)}\n")

@main_bp.route('/resume')
def resume():
    return render_template('resume.html', title='Резюме')

@main_bp.route('/contacts', methods=['GET', 'POST'])
def contacts():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            write_contact_log(form)
        except OSError:
            flash("Не вдалося записати повідомлення. Спробуйте пізніше.", "danger")
        else:
            flash(f"Дякуємо, {form.name.data}! Ваше повідомлення надіслано.", "success")
        return redirect(url_for('main.contacts'))
    if request.method == 'POST':
        flash("Форму заповнено з помилками. Перевірте виділені поля.", "danger")
    return render_template('contacts.html', title='Контакти', form=form)

@main_bp.route("/homepage")
def home():
    return render_template('index.html', title='Головна')
