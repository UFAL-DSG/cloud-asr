var lastResult;

$(document).ready(function() {
    var speechRecognition = new SpeechRecognition();
    speechRecognition.onresult = function(results) {
        if (results.length > 0 && results[0].final == true) {
            var transcript = results[0].alternative[0].transcript;

            $('#result').prepend(transcript + '<br>');
        };
    }

    speechRecognition.onstart = function(e) {
       $('#record').html('<i class="icon-stop"></i>Stop recording');
    }

    speechRecognition.onend = function(e) {
        $('#record').html('<i class="icon-bullhorn"></i>Start recording');
    }

    var recording = false;
    $('#record').click(function() {
        if(!recording) {
            speechRecognition.start();
        } else {
            speechRecognition.stop();
        }

        recording = !recording;
    });
});
