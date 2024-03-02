from flask import Flask, render_template, url_for, request, send_file, redirect, session

from PIL import Image, ImageDraw, ImageEnhance
import os

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import email_validator

app = Flask(__name__)

image = None
draw = None
last_point = None
current_color = (0, 0, 0)
canvas_size = (500, 500)

def init_image():
    global image, draw
    image = Image.new("RGB", canvas_size, color="white")
    draw = ImageDraw.Draw(image)

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль:', validators=[DataRequired(), Length(min=6, max=20)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
class RegisterForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Пароль:', validators=[DataRequired(), Length(min=6, max=20)])
    repeat_password = PasswordField('Повторите пароль:', validators=[DataRequired(), Length(min=6, max=20)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

app.config['SECRET_KEY'] ='secret-pzdc'

@app.route('/registering', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        login = form.login.data
        email = form.email.data
        password = form.password.data
        repeat_password = form.repeat_password.data
        remember_me = form.remember_me.data
        submit = form.submit.data
        if password == repeat_password and login != "" and password != "" and repeat_password != "":
            print(login, email, password, repeat_password,  remember_me, submit)
            return {"login": login,
                "email": email,
                "password": password,
                "repeat_password": repeat_password,
                "remeber": remember_me,
                "submit": submit
                }
        else:
            return redirect('/registering')
    return render_template('reg.html', form=form)


@app.route('/logining', methods=['GET', 'POST'])
def logIN():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        remember_me = form.remember_me.data
        submit = form.submit.data
        if login != "" and password != "":
            print(login, password, remember_me, submit)
            return {"login": login,
                    "password": password,
                    "remeber": remember_me,
                    "submit": submit
                    }
    return render_template('log.html', form=form)



@app.route('/upload', methods=['POST'])
def upload():
    global image, draw
    if request.method == 'POST':
        # Открытие изображения
        # файл из запроса
        uploaded_file = request.files['image']
        
        if uploaded_file.filename == "":
            return "No file selected"
        
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        if uploaded_file.filename.split('.')[-1].lower() not in allowed_extensions:
            return "Invalid file type"

        # Открываем файл на сервере
        file_path = os.path.join('static', 'EDITOR', uploaded_file.filename)
        uploaded_file.save(file_path)
        
        image = Image.open(uploaded_file)


        init_image()
        
        contrast_slider = float(request.form['contrast-slider'])
        brightness_slider = float(request.form['brightness-slider'])
        saturation_slider = float(request.form['saturation-slider'])
        sharpness_slider = float(request.form['sharpness-slider'])

        # Применение эффектов контраста, яркости, насыщенности, резкости
        
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(contrast_slider)

        brightness = ImageEnhance.Brightness(image)
        image = brightness.enhance(brightness_slider)

        saturation = ImageEnhance.Color(image)
        image = saturation.enhance(saturation_slider)

        sharpness = ImageEnhance.Sharpness(image)
        image = sharpness.enhance(sharpness_slider)
        
        
        draw = ImageDraw.Draw(image)
        draw_image()
        # Сохранение отредактированного файла
        edited_filename = "edited_" + uploaded_file.filename
        save_path = os.path.join('static', 'EDITOR', edited_filename)
        image.save(save_path)

        return redirect(url_for('download', filename=edited_filename))
    else:
        return "ERROR"
#///

@app.route("/draw", methods=["POST"])
def draw_line():
    global image, draw, last_point
    if request.method == "POST":
        data = request.json
        points = [(x, y) for x, y in zip(data["x"], data["y"])]
        color = tuple(map(int, data["color"]))

        if len(points) > 1:
            draw.line(points, fill=color, width=2)

        last_point = points[-1]

        return "Drawing updated!"

@app.route("/erase", methods=["POST"])
def erase():
    global image, draw, last_point
    if request.method == "POST":
        draw.rectangle([(0, 0), canvas_size], fill="white")  # Нарисовать белый прямоугольник
        last_point = None
        return "Erasing updated!"

@app.route("/fill", methods=["POST"])
def fill():
    global image, draw
    if request.method == "POST":
        data = request.json
        start_point = tuple(data["start"])

        orig_color = image.getpixel(start_point)
        new_color = tuple(map(int, data["color"]))

        stack = [start_point]

        while stack:
            x, y = stack.pop()
            if image.getpixel((x, y)) == orig_color:
                draw.point((x, y), fill=new_color)
                if x > 0:
                    stack.append((x - 1, y))
                if x < canvas_size[0] - 1:
                    stack.append((x + 1, y))
                if y > 0:
                    stack.append((x, y - 1))
                if y < canvas_size[1] - 1:
                    stack.append((x, y + 1))

        return "Filling updated!"

#///
@app.route('/download/<filename>', methods=['POST','GET'])
def download(filename):
    # Отдаем сохраненный файл пользователю
    file_path = os.path.join('static', 'EDITOR', filename)
    if not os.path.exists(file_path):
        return redirect('/')
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


def draw_image():
    global image
    image.show()

@app.route("/get_points", methods=["GET"])
def get_points():
    global points
    return {"points": points, "color": current_color}

if __name__ == "__main__":
    app.run(debug=True)
