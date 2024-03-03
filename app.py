from flask import Flask, render_template, url_for, request, send_file, redirect, session

from PIL import Image, ImageDraw, ImageEnhance
import os



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


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

app.config['SECRET_KEY'] ='secret-pzdc'





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
        
        # Сохранение отредактированного файла
        edited_filename = "edited_" + uploaded_file.filename
        save_path = os.path.join('static', 'EDITOR', edited_filename)
        image.save(save_path)

        return redirect(url_for('download', filename=edited_filename))
    else:
        return "ERROR"
#///



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


@app.route("/get_points", methods=["GET"])
def get_points():
    global points
    return {"points": points, "color": current_color}

if __name__ == "__main__":
    app.run(debug=True)
