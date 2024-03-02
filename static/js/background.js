document.addEventListener('mousemove', function (event) {
  var background = document.getElementById('background');
  var mouseX = event.clientX;
  var mouseY = event.clientY;
  background.style.backgroundPosition = mouseX + 'px ' + mouseY + 'px';
});
