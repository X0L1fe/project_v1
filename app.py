from sqlite3 import IntegrityError
from flask import Flask, make_response, render_template, url_for, request, send_file, redirect, session, abort, flash
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect, generate_csrf

from PIL import Image as IMAGE, ImageEnhance
import os
import json

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
app.config['SESSION_TYPE'] = 'null'
app.config['CORS_HEADER'] = 'Content-Type'
app.config['Access-Control-Allow-Origin'] = ('*')

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'helperphotopainter@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = ('Roman Developer','helperphotopainter@gmail.com')
app.config['MAIL_PASSWORD'] = 'nskr herv dxqq wbym'
app.config['MAIL_DEBUG'] = True

db.init_app(app)

app.app_context().push()

mail = Mail(app)
csrf = CSRFProtect(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
    

@app.route('/registering', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template("/")
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
                return redirect('/')
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
    if current_user.is_authenticated:
        return redirect("/")
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
                login_user(user, remember=remember_me)
                return redirect('/')
            else:
                # Неверный email или пароль
                print ('Password is incorrect')
                return redirect('/logining')
    return render_template('log.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/reset_password_request/', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect('/')  # Если пользователь уже аутентифицирован, перенаправляем его на главную страницу

    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            print(form.email.data)
            send_password_reset_email(user)
        flash('Инструкции по сбросу пароля были отправлены на ваш адрес электронной почты.')
        print (form)
        return redirect(url_for('logIN'))  # Перенаправляем пользователя на страницу входа после отправки инструкций
    return render_template('reset_password_request.html', form=form)

def send_password_reset_email(user):
    token = user.get_reset_password_token()  # Это функция, которую вы должны определить в модели пользователя
    msg = Message('Сброс пароля', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])
    msg.body = f'''Для сброса пароля перейдите по ссылке:
{url_for('reset_password', token=token, _external=True)}

Если вы не запрашивали сброс пароля, проигнорируйте это сообщение.
'''
    mail.send(msg)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect('/')  
    print(token)
    user = User.verify_reset_password_token(token)

    if not user:
        print('Недействительный или истекший токен сброса пароля.')
        return redirect(url_for('logIN'))
    form = ResetPasswordForm() 
    if form.validate_on_submit():
        password = form.password.data
        repeat_password = form.repeat_password.data
        print('Форма прошла валидацию')
        if password == repeat_password:
            user.set_password(password)
            db.session.commit()
            print('Ваш пароль был успешно изменен.')
            return redirect(url_for('logIN'))
        else:
            flash('Пароли не совпадают.', 'error')
            return redirect(url_for('reset_password', token=token))
    print('Ошибки валидации формы:', form.errors)
    return render_template('reset_password.html', form=form, token=token)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

def unique_filename(filename):
    name, ext = os.path.splitext(filename)
    return f"{name}_{uuid.uuid4().hex}{ext}"

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        user = current_user

        if 'image' not in request.files:
            return "No file selected", 400

        uploaded_file = request.files['image']

        if uploaded_file.filename == "":
            return "No file selected", 400

        if uploaded_file.filename.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
            return "Invalid file type", 400

        # Получение значений ползунков
        contrast_slider = request.form.get('contrast-slider', 1)
        brightness_slider = request.form.get('brightness-slider', 1)
        saturation_slider = request.form.get('saturation-slider', 1)
        sharpness_slider = request.form.get('sharpness-slider', 0)

        # Генерация уникального имени файла и сохранение в локальное хранилище
        unique_name = unique_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        uploaded_file.save(file_path)

        try:
            # Открытие файла для редактирования
            image = IMAGE.open(file_path)
            image = process_image(
                image,
                contrast_slider,
                brightness_slider,
                saturation_slider,
                sharpness_slider
            )

            edited_filename = "edited_" + unique_name
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], edited_filename)

            # Сохранение редактированного изображения
            image.save(save_path)

            try:
                # Сохранение записи об изображении в базе данных
                image_metadata = {
                    "filesize": image.size,
                    "image_width": image.width,
                    "image_height": image.height,
                }
                image_metadata = json.dumps(image_metadata)

                original_filename = secure_filename(edited_filename)

                # Создание объекта Image и добавление его в сессию базы данных
                image = Image(
                    filename=edited_filename,
                    original_filename=original_filename,  # Сохраняем оригинальное имя файла
                    path=save_path,
                    metadata=image_metadata,
                    user_id=user.id
                )
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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_file(file_path, as_attachment=True)

@app.route('/delete_image/<int:image_id>', methods=['GET', 'POST'])
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    # Проверяем, что текущий пользователь является владельцем изображения
    if image.user_id != current_user.id:
        abort(403)  # Ошибка "Доступ запрещен"
    
    try:
        # Удаляем изображение из базы данных и сохраняем изменения
        db.session.delete(image)
        db.session.commit()
        # Успешное удаление изображения
        flash('Изображение успешно удалено', 'success')
        return redirect(url_for('profile'))
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}", 500)
        flash('Ошибка при удалении изображения', 'error')
        return redirect(url_for('profile'))

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
    if current_user.is_authenticated:
        user_images = Image.query.filter_by(user_id=current_user.id).all()
        return render_template('premier.html', user_images=user_images)
    else:
        #на страницу входа в систему
        return redirect('/logining')

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        user_images = current_user.images
        return render_template('profile.html', user_images=user_images)
    else:
        #на страницу входа в систему
        return redirect('/logining')    

@app.route('/about')
def about():
    return render_template( 'about.html')

@app.route('/helper')
def helper():
    return render_template( 'helper.html')

if __name__ == "__main__":
    app.run(debug=True)
