let tool = 'draw'; // По умолчанию выбран инструмент "Рисование"

function setTool(selectedTool) {
    tool = selectedTool;
}

function draw(e) {
    if (!isDrawing) return;
    ctx.lineWidth = 5; // Ширина линии рисования
    ctx.lineCap = 'round'; // Форма конца линии (круглая)
    ctx.strokeStyle = '#000'; // Цвет рисования (черный)

    // Логика рисования, стирания и заливки
    if (tool === 'draw' || tool === 'erase') {
        // Рисование и стирание
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
        [lastX, lastY] = [e.offsetX, e.offsetY];
    } else if (tool === 'fill') {
        // Заливка
        const pixelStack = [[e.offsetX, e.offsetY]];
        const targetColor = ctx.getImageData(e.offsetX, e.offsetY, 1, 1).data;

        while (pixelStack.length) {
            let newPos, x, y, pixelPos, reachLeft, reachRight;
            newPos = pixelStack.pop();
            x = newPos[0];
            y = newPos[1];

            pixelPos = (y * canvas.width + x) * 4;
            while (y-- >= 0 && matchStartColor(pixelPos, targetColor)) {
                pixelPos -= canvas.width * 4;
            }
            pixelPos += canvas.width * 4;
            ++y;
            reachLeft = false;
            reachRight = false;

            while (y++ < canvas.height - 1 && matchStartColor(pixelPos, targetColor)) {
                colorPixel(pixelPos);

                if (x > 0) {
                    if (matchStartColor(pixelPos - 4, targetColor)) {
                        if (!reachLeft) {
                            pixelStack.push([x - 1, y]);
                            reachLeft = true;
                        }
                    } else if (reachLeft) {
                        reachLeft = false;
                    }
                }

                if (x < canvas.width - 1) {
                    if (matchStartColor(pixelPos + 4, targetColor)) {
                        if (!reachRight) {
                            pixelStack.push([x + 1, y]);
                            reachRight = true;
                        }
                    } else if (reachRight) {
                        reachRight = false;
                    }
                }

                pixelPos += canvas.width * 4;
            }
        }
    }
}

function saveImage() {
    const dataURL = canvas.toDataURL('image/png');
    fetch('/save', {
        method: 'POST',
        body: JSON.stringify({ image: dataURL }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Изображение сохранено!');
            // Отправить ссылку пользователю для скачивания
            var link = document.createElement('a');
            link.href = editedImage.src;
            link.download = 'edited_image.png';
            link.click();
        } else {
            alert('Не удалось сохранить изображение.');
        }
    })
    .catch(error => {
        console.error('Ошибка при сохранении:', error);
    });
}
