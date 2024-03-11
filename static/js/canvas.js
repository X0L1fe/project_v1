let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let fileInput = document.getElementById("file-input");

fileInput.addEventListener("change", loadImage);

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

function updateImage() {
    let contrast = document.getElementById('contrast-slider').value;
    let brightness = document.getElementById('brightness-slider').value;
    let saturation = document.getElementById('saturation-slider').value;
    let sharpness = document.getElementById('sharpness-slider').value;

    canvas.style.filter = `contrast(${contrast}) brightness(${brightness}) saturate(${saturation}) blur(${sharpness}px)`;
}

function resetForms() {
    document.getElementById("file-input").value = "";
    document.getElementById("contrast-slider").value = 1;
    document.getElementById("brightness-slider").value = 1;
    document.getElementById("saturation-slider").value = 1;
    document.getElementById("sharpness-slider").value = 0;

    location.reload();
}
