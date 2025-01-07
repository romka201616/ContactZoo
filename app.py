from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'секретный_ключ'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def is_username_unique(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is None

# Главная страница (вход/регистрация)
@app.route('/', methods=['GET', 'POST'])
def login_register():
    if request.method == "POST":
        if "password_confirm" in request.form:  # Регистрация
            username = request.form["username"]
            password = request.form["password"]
            password_confirm = request.form["password_confirm"]

            if len(username) < 4:
                flash("Имя пользователя должно содержать минимум 4 символа.")
            elif not username.isalnum():
                flash("Имя пользователя должно содержать только цифры и буквы английского алфавита.")
            elif not is_username_unique(username):
                flash("Имя пользователя уже существует.")
            elif len(password) < 8:
                flash("Пароль должен содержать минимум 8 символов.")
            elif not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
                flash("Пароль должен содержать как минимум 1 букву и 1 цифру.")
            elif password != password_confirm:
                flash("Пароль и повтор пароля должны совпадать.")
            else:
                conn = get_db_connection()
                password_hash = generate_password_hash(password)
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
                conn.commit()
                conn.close()
                flash("Регистрация успешна! Войдите в систему.")
                return redirect(url_for("login_register"))

        else:  # Авторизация
            username = request.form["username"]
            password = request.form["password"]

            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["is_admin"] = user["is_admin"]
                return redirect(url_for("user_dashboard"))
            else:
                flash("Логин или пароль неверны.")

    return render_template("login_register.html")

# Панель управления пользователя
@app.route("/user")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login_register"))

    user_id = session["user_id"]
    username = session["username"]

    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    return render_template("user_dashboard.html", contacts=contacts, username=username)

# Панель администратора
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login_register'))
    conn = get_db_connection()
    users = conn.execute('SELECT id, username FROM users').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users)

# Добавление контакта
@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        photo = request.files['photo']
        user_id = session['user_id']

        if not (name and surname and phone and photo):
            flash('Не все поля заполнены')
            return redirect(url_for('add_contact'))

        conn = get_db_connection()
        existing_contact = conn.execute('SELECT id FROM contacts WHERE phone = ? AND user_id = ?', (phone, user_id)).fetchone()

        if existing_contact:
            flash('Контакт с этим номером уже существует в вашей записной книжке')
            conn.close()
            return redirect(url_for('add_contact'))

        if photo:
            filename = secure_filename(photo.filename)
            try:
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conn.execute('INSERT INTO contacts (user_id, name, surname, phone, photo) VALUES (?, ?, ?, ?, ?)',
                             (user_id, name, surname, phone, filename))
                conn.commit()
                conn.close()
                return redirect(url_for('user_dashboard'))
            except Exception as e:
                conn.close()
                flash(f"Ошибка сохранения файла: {e}")
                return redirect(url_for('add_contact'))
        else:
            conn.close()
            flash("Пожалуйста, загрузите фотографию.")
            return redirect(url_for('add_contact'))

    return render_template('add_contact.html')

# Редактирование контакта
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = session['user_id']
    conn = get_db_connection()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ? AND user_id = ?', (id, user_id)).fetchone()

    if not contact:
        conn.close()
        flash('Контакт не найден или не принадлежит вам')
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        photo = request.files['photo']

        if not (name and surname and phone):
            flash('Не все поля заполнены')
            conn.close()
            return redirect(url_for('edit_contact', id=id))

        filename = contact['photo']  # По умолчанию оставляем старое фото

        if photo:
            filename = secure_filename(photo.filename)
            try:
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                flash(f"Ошибка сохранения файла: {e}")
                conn.close()
                return redirect(url_for('edit_contact', id=id))

        try:
            conn.execute('UPDATE contacts SET name = ?, surname = ?, phone = ?, photo = ? WHERE id = ? AND user_id = ?',
                         (name, surname, phone, filename, id, user_id))
            conn.commit()
            conn.close()
            flash('Контакт обновлен')
            return redirect(url_for('user_dashboard'))
        except sqlite3.IntegrityError:
            flash('Контакт с таким номером телефона уже существует')
            conn.close()
            return redirect(url_for('edit_contact', id=id))

    return render_template('edit_contact.html', contact=contact)

# Удаление контакта
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_contact(id):
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = session['user_id']
    conn = get_db_connection()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ? AND user_id = ?', (id, user_id)).fetchone()

    if not contact:
        conn.close()
        flash('Контакт не найден или не принадлежит вам')
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        conn.execute('DELETE FROM contacts WHERE id = ? AND user_id = ?', (id, user_id))
        conn.commit()
        conn.close()
        flash('Контакт удалён')
        return redirect(url_for('user_dashboard'))

    return render_template('delete_confirm.html')

# Удаление пользователя (только для администратора)
@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login_register'))

    conn = get_db_connection()
    if session['user_id'] != id: # Администратор не может удалить сам себя
        conn.execute('DELETE FROM users WHERE id = ?', (id,))
        # Каскадное удаление контактов пользователя
        conn.execute('DELETE FROM contacts WHERE user_id = ?', (id,))
        conn.commit()
        flash('Пользователь удален')
    else:
        flash('Нельзя удалить текущего администратора')
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Поиск контактов
@app.route('/search')
def search_contacts():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    user_id = session['user_id']
    query = request.args.get('query')
    conn = get_db_connection()
    contacts = []
    if query:
        search_term = f"%{query}%"
        contacts = conn.execute("""
            SELECT * FROM contacts
            WHERE user_id = ? AND (name LIKE ? OR surname LIKE ? OR phone LIKE ?)
        """, (user_id, search_term, search_term, search_term)).fetchall()
    conn.close()
    return render_template('search_results.html', results=contacts, query=query)

# Выход из системы
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_register'))

if __name__ == '__main__':
    # Убедитесь, что папка для загрузок существует
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=8080)