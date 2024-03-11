from sqlite3 import IntegrityError
from flask import Flask, make_response, render_template, url_for, request, send_file, redirect, session, abort, flash

from PIL import Image, ImageDraw, ImageEnhance
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from models import *
from forms import *
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SECRET_KEY'] ='secret-pzdc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profile.db'

db = SQLAlchemy(app)

app.app_context().push()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/registering', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        login = form.login.data
        email = form.email.data
        password = form.password.data
        repeat_password = form.repeat_password.data
        if password == repeat_password and login != "" and password != "" and repeat_password != "":
            user = User()
            password_hash = user.set_password(password)
            print(user.set_password(password))
            user = User(login=login, email=email, password=password_hash)
            try:
                db.session.add(user)
                db.session.commit()
                return redirect('/workplace')
            except IntegrityError:
                db.session.rollback()  # Откатываем изменения
                flash('Этот логин или адрес электронной почты уже используется.')
                return redirect('/registering')
            except Exception as e:
                print(e)
                return redirect('/registering')
        else:
            return redirect('/registering')
    return render_template('reg.html', form=form)


@app.route('/logining', methods=['GET', 'POST'])
def logIN():
    form = LoginForm()
    if form.validate_on_submit():
        login_email = form.login_email.data
        password = form.password.data
        remember_me = form.remember_me.data
        user = User()
        if login_email != "" and password != "":
            user = db.session.query(User).filter(or_(User.login == login_email, User.email == login_email)).first()
            if user and user.check_password(password):
                # Успешная аутентификация
                if remember_me:
                    # Установить куки на месяц
                    resp = make_response(redirect('/workplace'))
                    resp.set_cookie('user_id', str(user.id), max_age=30*24*60*60)
                    return resp
                else:
                    # Не сохранять сеанс
                    session['user_id'] = user.id
                    return redirect('/workplace')
            else:
                # Неверный email или пароль
                print ('Password is incorrect')
                return redirect('/logining')
    return render_template('log.html', form=form)

from flask import abort

from flask import request

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Проверяем, что файл был загружен
        if 'image' not in request.files:
            return "No file selected", 400

        uploaded_file = request.files['image']

        # Проверяем, что файл имеет имя
        if uploaded_file.filename == "":
            return "No file selected", 400

        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        # Проверяем разрешенное расширение файла
        if uploaded_file.filename.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
            return "Invalid file type", 400

        # Путь для сохранения загруженного файла
        file_path = os.path.join('static', 'EDITOR', uploaded_file.filename)

        try:
            # Сохраняем загруженный файл
            uploaded_file.save(file_path)

            # Открываем файл для редактирования
            image = Image.open(file_path)

            # Получаем параметры обрезки из запроса
            x = int(request.form.get('x'))  # НОВОЕ
            y = int(request.form.get('y'))  # НОВОЕ
            width = int(request.form.get('width'))  # НОВОЕ
            height = int(request.form.get('height'))  # НОВОЕ


            # Применяем фильтры и обрезаем изображение
            image = process_image(
                image,
                x, y, width, height,
                request.form['contrast-slider'],
                request.form['brightness-slider'],
                request.form['saturation-slider'],
                request.form['sharpness-slider']
            )

            edited_filename = "edited_" + uploaded_file.filename
            save_path = os.path.join('static', 'EDITOR', edited_filename)

            image.save(save_path)

            return redirect(url_for('download', filename=edited_filename))
        except Exception as e:
            return f"Error: {str(e)}", 500
    else:
        # Возвращаем ошибку, если метод запроса не POST
        return "Method not allowed", 405

#///
def process_image(image, x, y, width, height, contrast_slider, brightness_slider, saturation_slider, sharpness_slider):
    # Обрезаем изображение
    image = image.crop((x, y, x + width, y + height))

    # Применяем фильтры к изображению
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(float(contrast_slider))

    brightness = ImageEnhance.Brightness(image)
    image = brightness.enhance(float(brightness_slider))

    saturation = ImageEnhance.Color(image)
    image = saturation.enhance(float(saturation_slider))

    sharpness = ImageEnhance.Sharpness(image)
    image = sharpness.enhance(float(sharpness_slider))

    return image

#///
@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    # Путь к файлу для скачивания
    file_path = os.path.join('static', 'EDITOR', filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_file(file_path, as_attachment=True)



@app.route('/contakts')
def contact():
    return render_template( 'contakts.html')

@app.route("/workplace")
def workplace():
    return render_template("workplace.html")

@app.route('/premier')
def premier():
    return render_template( 'premier.html')

@app.route('/about')
def about():
    return render_template( 'about.html')

if __name__ == "__main__":
    app.run(debug=True)
