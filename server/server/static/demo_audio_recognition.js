// var socket = io();
// Socket is in demo_log_stream and that's loaded before this

navigator.mediaDevices.getUserMedia({ audio: true })
.then(function(stream) {
  var audioContext = new AudioContext();
  var audioInput = audioContext.createMediaStreamSource(stream);

  var bufferSize = 2048;
  var scriptNode = audioContext.createScriptProcessor(bufferSize, 1, 1);

  scriptNode.onaudioprocess = function(audioProcessingEvent) {
    var inputBuffer = audioProcessingEvent.inputBuffer;
    var inputData = inputBuffer.getChannelData(0);

    // Convert the float audio data to 16-bit PCM
    var outputData = new Int16Array(inputData.length);
    for (var i = 0; i < inputData.length; i++) {
      outputData[i] = inputData[i] * 32767;
    }

    // Emit the audio data to the server
    socket.emit('demo_audio_stream', outputData);
  };

  audioInput.connect(scriptNode);
  scriptNode.connect(audioContext.destination);
})
.catch(function(err) {
  console.error('Error accessing audio input: ' + err);
});

// Receive and process audio data from the server
socket.on('demo_audio_stream', function(audioData) {
  // Process the received audio data
  // In this example, we simply log the received audio data
  console.log(audioData);
});
