let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let fileInput = document.getElementById("file");
let image;

fileInput.addEventListener("change", loadImage);

// Загружаем изображение
function loadImage() {
    let file = fileInput.files[0];
    let reader = new FileReader();

    reader.onload = function (e) {
        image = new Image();
        image.onload = function () {
            canvas.width = image.width;
            canvas.height = image.height;
            ctx.drawImage(image, 0, 0);
            updateImage(); // Вызываем функцию обновления изображения
            document.querySelector('.image-editor').style.display = 'block';
            document.querySelector('.reset-button').style.display = 'block';
            document.querySelector('.image-editor').classList.remove('hide'); // Удаляем класс hide
            document.querySelector('.reset-button').classList.remove('hide'); // Удаляем класс hide
            document.querySelector('.BODY_1').classList.add('hide');
            document.querySelector('.BODY_2').classList.add('hide');
            document.querySelector('.image-selection').classList.add('hide'); // Добавляем класс hide
            document.querySelector('.controls').classList.remove('hide');

        }
        image.src = e.target.result;
    }

    reader.readAsDataURL(file);
}

// Обновляем фильтры изображения
function updateImage() {
    let contrast = document.getElementById('contrast-slider').value;
    document.getElementById('contrast-value').textContent = contrast;
    
    // Обновляем значение яркости
    let brightness = document.getElementById('brightness-slider').value;
    document.getElementById('brightness-value').textContent = brightness;
    
    // Обновляем значение насыщенности
    let saturation = document.getElementById('saturation-slider').value;
    document.getElementById('saturation-value').textContent = saturation;
    
    // Обновляем значение резкости
    let sharpness = document.getElementById('sharpness-slider').value;
    document.getElementById('sharpness-value').textContent = sharpness;

    // Рисуем изображение с применением фильтров
    ctx.filter = `contrast(${contrast}) brightness(${brightness}) saturate(${saturation}) blur(${sharpness}px)`;
    ctx.drawImage(image, 0, 0); // Убираем передачу размеров
    ctx.filter = 'none'; // Сбрасываем фильтры
}

// Сброс формы
function resetForms() {
    document.getElementById("file").value = "";
    document.getElementById("contrast-slider").value = 1;
    document.getElementById("brightness-slider").value = 1;
    document.getElementById("saturation-slider").value = 1;
    document.getElementById("sharpness-slider").value = 0;

    location.reload();
}

document.querySelector('form').addEventListener('reset', function() {
    document.querySelector('.file').value = ''; // Сброс значения input типа file
    document.querySelector('.image-editor').style.display = 'none'; // Скрываем image-editor div при сбросе формы
});