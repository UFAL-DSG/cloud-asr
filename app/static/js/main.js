var audio_context;
var recorder;


function prepareForRecording() {
    try {
        // webkit shim
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;

        audio_context = new AudioContext;
        console.log('Audio context set up.');
        console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
    } catch (e) {
        alert('No web audio support in this browser!');
    }

    navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
        console.log('No live audio input: ' + e);
    });
}


function startUserMedia(stream) {
    var input = audio_context.createMediaStreamSource(stream);
    console.log('Media stream created.');

    input.connect(audio_context.destination);
    console.log('Input connected to audio context destination.');

    config = {
        numChannels: 1,
        workerPath: 'static/js/recorderWorker.js'
    }
    recorder = new Recorder(input, config);
    console.log('Recorder initialised.');
}


function startRecording() {
    recorder && recorder.record();
    console.log('Recording started');

    $('#record').html('<i class="icon-stop"></i>Stop recording');
}


function evaluateRecording() {
    recorder && recorder.stop();
    recorder.exportWAV(recognizeSpeech(processTranscripts));
    recorder.clear();
    console.log('Recording stopped');

    $('#record').html('<i class="icon-bullhorn"></i>Start recording');
}


function recognizeSpeech(cb) {
    return function(blob) {
        $.ajax({
            type: 'POST',
            url: '/recognize',
            data: blob,
            processData: false,
            contentType: false
        }).done(cb);
    }
}


function processTranscripts(data) {
    if (typeof(data.result[0].alternative[0].transcript) != 'undefined') {
        var transcript = data.result[0].alternative[0].transcript;

        $('#result').prepend(transcript + '<br>');
    }
}


$(document).ready(function() {
    prepareForRecording();

    var recording = false;
    $('#record').click(function() {
        if(recording) {
            evaluateRecording();
        } else {
            startRecording();
        }

        recording = !recording;
    });
});
