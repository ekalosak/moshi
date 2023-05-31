const socket = io.connect('http://localhost:5000');
console.log('Made socket: ' + socket);
var ulElement = document.getElementById("text-stream-ul");
console.log('Got ulElement: ' + ulElement);
var logUlElement = document.getElementById("log-stream-ul");

function addLogEntry(logEntry) {
  var liElement = document.createElement("li");
  liElement.textContent = logEntry;
  logUlElement.appendChild(liElement);
}

socket.on('connect', function() {
  console.log('Connected to the server');
});

socket.on('stream_data', function(chunk) {
  console.log('Received data:', chunk.data);
  var liElement = document.createElement("li");
  liElement.textContent = chunk.data;
  ulElement.appendChild(liElement);
});

socket.on('log', function(data) {
  console.log('Log data: ' + data);
  var logLevel = data.level;
  var logMessage = data.message;
  var logTime = data.time;
  var logName = data.name;
  var logFunction = data.function;
  var logLine = data.line;
  var logEntry = '[' + logTime + '] [' + logLevel + '] ' + logMessage + ' (Logger: ' + logName + ', Function: ' + logFunction + ', Line: ' + logLine + ')';
  addLogEntry(logEntry);
});

socket.on('disconnect', function() {
  console.log('Disconnected from the server');
});

socket.emit('start_stream');
