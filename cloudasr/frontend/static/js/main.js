var lastResult;

$(document).ready(function() {
    var speechRecognition = new SpeechRecognition();
    speechRecognition.onresult = function(results) {
        if (results.length > 0 && results[0].final == true) {
            var transcript = results[0].alternative[0].transcript;

            $('#result').prepend('<div class="well well-sm">' + transcript + '</div>');
        };
    }

    speechRecognition.onstart = function(e) {
       $('#record').html('<i class="icon-stop"></i>Stop recording');
    }

    speechRecognition.onend = function(e) {
        $('#record').html('<i class="icon-bullhorn"></i>Start recording');
    }

    speechRecognition.onerror = function(e) {
        $('#result').prepend('<div class="alert alert-danger" role="alert">' + e + '</div>');
    }

    $('#record').click(function() {
        if(!speechRecognition.isRecording) {
            speechRecognition.start();
        } else {
            speechRecognition.stop();
        }
    });

});
