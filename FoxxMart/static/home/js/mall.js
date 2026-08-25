(function () {
  var stream = document.querySelector('[data-mall-stream]');
  var line = document.querySelector('[data-mall-line]');
  var canvas = document.querySelector('.mall-stage__particles');
  if (!stream || !line) return;

  var startX = 0;
  var startOffset = 0;
  var offset = 0;
  var dragging = false;
  var moved = false;
  var activePointerId = null;
  var getTranslateX = function () {
    var transform = window.getComputedStyle(line).transform;
    if (!transform || transform === 'none') return 0;
    return new DOMMatrix(transform).m41;
  };
  var move = function (x) {
    offset = startOffset + x - startX;
    line.style.transform = 'translateX(' + offset + 'px)';
  };
  stream.addEventListener('pointerdown', function (event) {
    // Cards are links first. Only the space between cards starts a drag,
    // preventing pointer capture from swallowing a normal card tap.
    if (event.target.closest('a')) return;
    dragging = false;
    moved = false;
    activePointerId = event.pointerId;
    startX = event.clientX;
    startOffset = getTranslateX();
    stream.setPointerCapture(event.pointerId);
  });
  stream.addEventListener('pointermove', function (event) {
    if (event.pointerId !== activePointerId) return;
    if (!event.buttons) return;
    if (!dragging && Math.abs(event.clientX - startX) <= 6) return;
    if (!dragging) {
      dragging = true;
      moved = true;
      line.style.animation = 'none';
      stream.classList.add('is-dragging');
    }
    event.preventDefault();
    move(event.clientX);
  });
  var stopDragging = function (event) {
    if (event.pointerId !== activePointerId) return;
    if (event && stream.hasPointerCapture(event.pointerId)) stream.releasePointerCapture(event.pointerId);
    dragging = false;
    activePointerId = null;
    stream.classList.remove('is-dragging');
  };
  stream.addEventListener('pointerup', stopDragging);
  stream.addEventListener('pointercancel', stopDragging);
  stream.addEventListener('click', function (event) {
    if (event.target.closest('a')) { moved = false; return; }
    if (moved) { event.preventDefault(); moved = false; }
  }, true);

  var context = canvas && canvas.getContext('2d');
  if (!context) return;
  var dots = Array.from({ length: 70 }, function () { return { x: Math.random(), y: Math.random(), r: Math.random() * 1.6 + .2, v: Math.random() * .12 + .02 }; });
  var draw = function () {
    var width = canvas.width = window.innerWidth * devicePixelRatio;
    var height = canvas.height = window.innerHeight * devicePixelRatio;
    context.clearRect(0, 0, width, height);
    dots.forEach(function (dot) { dot.x += dot.v / 1000; if (dot.x > 1) dot.x = 0; context.beginPath(); context.arc(dot.x * width, dot.y * height, dot.r * devicePixelRatio, 0, Math.PI * 2); context.fillStyle = 'rgba(180, 220, 255, .5)'; context.fill(); });
    requestAnimationFrame(draw);
  };
  draw();
}());
