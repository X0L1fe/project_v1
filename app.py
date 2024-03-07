from flask import Flask, render_template, url_for, request, send_file, redirect, session, abort

from PIL import Image, ImageDraw, ImageEnhance
import os

from flask_sqlalchemy import SQLAlchemy

from models import *
from forms import *

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
        remember_me = form.remember_me.data
        if password == repeat_password and login != "" and password != "" and repeat_password != "":
            user = User(login=login, email=email, password=password)
            print(login, email, password, repeat_password,  remember_me)
            try:
                db.session.add(user)
                db.session.commit()
                return redirect('/workplace')
            except:
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
        if login_email != "" and password != "":
            
            print(login_email, password, remember_me)
            try:
                pass#///
            except:
                return redirect('/logining')
    return render_template('log.html', form=form)

from flask import abort

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
            
            # Применяем эффекты редактирования
            
            contrast = ImageEnhance.Contrast(image)
            image = contrast.enhance(float(request.form['contrast-slider']))

            brightness = ImageEnhance.Brightness(image)
            image = brightness.enhance(float(request.form['brightness-slider']))

            saturation = ImageEnhance.Color(image)
            image = saturation.enhance(float(request.form['saturation-slider']))

            sharpness = ImageEnhance.Sharpness(image)
            image = sharpness.enhance(float(request.form['sharpness-slider']))
            
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
