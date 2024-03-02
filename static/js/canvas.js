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

function erase() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    loadImage();
}

function fill() {
    let start = [250, 250]; // Example start point
    let color = [255, 0, 0]; // Example color (red)

    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "/fill",
        data: JSON.stringify({ "start": start, "color": color }),
        success: function () {
            console.log("Fill updated!");
            loadImage();
        }
    });
}
