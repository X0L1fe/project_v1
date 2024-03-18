let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let fileInput = document.getElementById("file-input");

fileInput.addEventListener("change", loadImage);

// Загружаем изображение
function loadImage() {
    let file = fileInput.files[0];
    let reader = new FileReader();

    reader.onload = function (e) {
        let image = new Image();
        image.onload = function () {
            canvas.width = image.width;
            canvas.height = image.height;
            ctx.drawImage(image, 0, 0);
        }
        image.src = e.target.result;
    }

    reader.readAsDataURL(file);
}

// Обновляем фильтры изображения
function updateImage() {
    let contrast = document.getElementById('contrast-slider').value;
    let brightness = document.getElementById('brightness-slider').value;
    let saturation = document.getElementById('saturation-slider').value;
    let sharpness = document.getElementById('sharpness-slider').value;

    let filters = `contrast(${contrast}) brightness(${brightness}) saturate(${saturation}) blur(${sharpness}px)`;
    document.getElementById('image').style.filter = filters;
}

// Сброс формы
function resetForms() {
    document.getElementById("file-input").value = "";
    document.getElementById("contrast-slider").value = 1;
    document.getElementById("brightness-slider").value = 1;
    document.getElementById("saturation-slider").value = 1;
    document.getElementById("sharpness-slider").value = 0;

    location.reload();
}

// Получаем элементы из DOM
let imageContainer = document.getElementById("image-container");
let image = document.getElementById("image");
let selectionBox = document.getElementById("selection-box");
let cropButton = document.getElementById("croping");
cropButton.addEventListener("click", cropImage);

// Обновляем выделение области при движении мыши
imageContainer.addEventListener("mousemove", function (e) {
    let rect = image.getBoundingClientRect();
    let x = e.clientX - rect.left;
    let y = e.clientY - rect.top;
    // Устанавливаем размеры и положение выделения
    selectionBox.style.left = x + "px";
    selectionBox.style.top = y + "px";
});

// Обработка нажатия кнопки "Обрезать"
function cropImage() {
    let selectionX = parseInt(selectionBox.style.left);
    let selectionY = parseInt(selectionBox.style.top);
    let selectionWidth = parseInt(selectionBox.offsetWidth);
    let selectionHeight = parseInt(selectionBox.offsetHeight);

    // Создаем объект FormData и добавляем данные формы
    let formData = new FormData();
    formData.append('x', selectionX);
    formData.append('y', selectionY);
    formData.append('width', selectionWidth);
    formData.append('height', selectionHeight);
    // Отправляем данные формы на сервер
    fetch("http://localhost:5000/croping", {
        method: "POST",
        body: formData 
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
    })
    .catch(error => console.error('There has been a problem with your fetch operation:', error));
}

