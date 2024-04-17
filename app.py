from sqlite3 import IntegrityError
from flask import Flask, make_response, render_template, url_for, request, send_file, redirect, session, abort, flash
from flask_login import LoginManager, current_user, login_user

from PIL import Image as IMAGE, ImageEnhance
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import uuid

from models import *
from forms import *
from werkzeug.utils import secure_filename

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = 'static/EDITOR/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SECRET_KEY'] ='secret-pzdc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profile.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CORS_HEADER'] = 'Content-Type'
app.config['Access-Control-Allow-Origin'] = ('*')

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
            user = User(login=login, email=email, password=password_hash)
            try:
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
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
                    login_user(user)
                    return redirect('/workplace')
            else:
                # Неверный email или пароль
                print ('Password is incorrect')
                return redirect('/logining')
    return render_template('log.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем идентификатор пользователя из сессии
    resp = make_response(redirect('/'))
    resp.set_cookie('user_id', '', expires=0)  # Удаляем куки с идентификатором пользователя
    return resp

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

def unique_filename(filename):
    name, ext = os.path.splitext(filename)
    return f"{name}_{uuid.uuid4().hex}{ext}"

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':

        user = current_user#!!!получаем пользователя!!!
        
        # Проверяем, что файл был загружен
        if 'image' not in request.files:
            return "No file selected", 400

        uploaded_file = request.files['image']

        # Проверяем, что файл имеет имя
        if uploaded_file.filename == "":
            return "No file selected", 400

        if uploaded_file.filename.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
            return "Invalid file type", 400

        # Путь для сохранения загруженного файла
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)

        try:
            # Сохраняем загруженный файл
            uploaded_file.save(file_path)
            # Открываем файл для редактирования
            image = IMAGE.open(file_path)
            # Применяем фильтры и обрезаем изображение
            image = process_image(
                image,
                request.form['contrast-slider'],
                request.form['brightness-slider'],
                request.form['saturation-slider'],
                request.form['sharpness-slider']
            )

            edited_filename = "edited_" + uploaded_file.filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], edited_filename)

            image.save(save_path)
            try:
                image_metadata = dict(image.info)
                image = Image(filename=unique_filename(uploaded_file.filename),
                          path=file_path,
                          metadata=image_metadata,
                          user_id=user.id)
                db.session.add(image)
                db.session.commit()
                return redirect(url_for('download', filename=edited_filename))
            except Exception as e:
                db.session.rollback()
                print (f"Error: {str(e)}", 500)
                return f"Error: {str(e)}", 500
        except Exception as e:
            return f"Error: {str(e)}", 500
    else:
        # Возвращаем ошибку, если метод запроса не POST
        return "Method not allowed", 405

#///
def process_image(image, contrast_slider, brightness_slider, saturation_slider, sharpness_slider):
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

@app.route('/workplace')
def workplace():
    if current_user.is_authenticated:
        
        return render_template("workplace.html")
    else:
        #на страницу входа в систему
        return redirect('/logining')


@app.route('/premier')
def premier():
    return render_template( 'premier.html')

@app.route('/about')
def about():
    return render_template( 'about.html')

if __name__ == "__main__":
    app.run(debug=True)
