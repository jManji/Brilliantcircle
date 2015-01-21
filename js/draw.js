var PERFECT_CIRCLE_LINE_WIDTH = 8;
var USER_CIRCLE_LINE_WIDTH = 20;
var PERFECT_CIRCLE_COLOR = 'rgba(255,255,255,0.4)';
var USER_CIRCLE_COLOR = 'rgba(227,235,100,0.1)';
var PERFECT_CIRCLE_RADIUS = 150;

var started = false;
var lastx = 0;
var lasty = 0;
var points = [];

// Bind canvas to listeners
var canvas = document.getElementById('drawing_board');
canvas.addEventListener('mousedown', mouseDown, false);
canvas.addEventListener('mousemove', mouseMove, false);
canvas.addEventListener('mouseup', mouseUp, false);
var ctx = canvas.getContext('2d');

// Create objects
var canvasSize = new function() {
  this.x = canvas.width;
  this.y = canvas.height;
}
var centerCoord = new function() {
  this.x = parseInt(canvasSize.x/2,10),
  this.y = parseInt(canvasSize.y/2,10)
}

/**
 * The perfect circle background is drawn when document is ready
 */
$(document).ready(function() {
  drawCircle();
});

/**
 * Draws the default perfect circle
 */
function drawCircle() {
  ctx.beginPath();
  ctx.arc(centerCoord.x, centerCoord.y, PERFECT_CIRCLE_RADIUS, 0, 2 * Math.PI);
  ctx.strokeStyle = PERFECT_CIRCLE_COLOR;
  ctx.setLineDash([30]);
  ctx.lineWidth = PERFECT_CIRCLE_LINE_WIDTH;
  ctx.stroke();

  // reset
  ctx.setLineDash([0]);
  ctx.lineWidth = USER_CIRCLE_LINE_WIDTH;
  ctx.strokeStyle = USER_CIRCLE_COLOR;
}

/**
 * Mouse callback functions
 */
function mouseDown(e) {

  clear();

  var m = getMouse(e, canvas);
  points.push({
    x: m.x,
    y: m.y
  });
  started = true;
};

function mouseMove(e) {
  if (started) {
    // put back the saved content
    var m = getMouse(e, canvas);
    points.push({
      x: m.x,
      y: m.y
    });
    drawPoints(ctx, points);
  }
};

function mouseUp(e) {
  if (started) {
    started = false;

    var pointsStr = JSON.stringify(points);
    var centerCoordStr = JSON.stringify(centerCoord);
    var canvasSizeStr = JSON.stringify(canvasSize);
    // When mouse is up, user has finished drawing. At this point we send
    // a message to the server with all the points of the drawn circle
    sendMessage('/rate', pointsStr, centerCoordStr,
                PERFECT_CIRCLE_RADIUS, canvasSizeStr);
    points = [];
  }
};

/**
 * Sends a request to the server, and handles the response
 * @param path  Path of the message
 * @param data  Data of the message
 */
function sendMessage(path, pointsStr, coordsStr, radiusStr, canvasSizeStr){
  $.ajax({
    url: path,
    type: 'POST',
    data: {
      points: pointsStr,
      center: coordsStr,
      radius: radiusStr,
      canvasSize: canvasSizeStr
    }
  }).done(function(data){
    updateScore(data.score);
  });
};

/**
 * Updates the score on the page
 * @param score  The calculated score
 */
function updateScore(score) {
  var result = document.getElementById('score_value');
  result.innerHTML = score;
}

/**
 * Clears the canvas and redraws the background circle
 */
function clear() {
  ctx.clearRect(0, 0, canvasSize.x, canvasSize.y);
  drawCircle();
};

/**
 * Draws the user's points on the canvas
 * @param ctx     canvas context
 * @param points  All the points to be drawn
 */
function drawPoints(ctx, points) {

  // Draw a basic circle instead
  if (points.length < 6) {
    var b = points[0];
    ctx.beginPath();
    ctx.arc(b.x, b.y, USER_CIRCLE_LINE_WIDTH / 2, 0, Math.PI * 2);
    ctx.fillStyle = USER_CIRCLE_COLOR;
    ctx.closePath(),
    ctx.fill();
    return
  }

  ctx.beginPath(), ctx.moveTo(points[0].x, points[0].y);
  // draw a bunch of quadratics, using the average of two points as the control point
  for (i = 1; i < points.length - 2; i++) {
    var c = (points[i].x + points[i + 1].x) / 2,
    d = (points[i].y + points[i + 1].y) / 2;
    ctx.quadraticCurveTo(points[i].x, points[i].y, c, d)
  }
  ctx.quadraticCurveTo(points[i].x, points[i].y, points[i + 1].x, points[i + 1].y), ctx.stroke()
}

// Creates an object with x and y defined,
// set to the mouse position relative to the state's canvas
// If you wanna be super-correct this can be tricky,
// we have to worry about padding and borders
// takes an event and a reference to the canvas
function getMouse(e, canvas) {
  var element = canvas, offsetX = 0, offsetY = 0, mx, my;

  // Compute the total offset. It's possible to cache this if you want
  if (element.offsetParent !== undefined) {
    do {
      offsetX += element.offsetLeft;
      offsetY += element.offsetTop;
    } while ((element = element.offsetParent));
  }

  mx = e.pageX - offsetX;
  my = e.pageY - offsetY;

  // We return a simple javascript object with x and y defined
  return {x: mx, y: my};
}
