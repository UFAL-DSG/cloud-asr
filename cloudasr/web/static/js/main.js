var lastResult;

$(document).ready(function() {
    var speechRecognition = new SpeechRecognition(apiUrl);
    var $result = $('#result');

    speechRecognition.onresult = function(result) {
        var transcript = result.result.hypotheses[0].transcript;
        $result.text(transcript);
        $('#request_id').text(result.request_id);
    }

    speechRecognition.onstart = function(e) {
        $('#start_recording').hide()
        $('#stop_recording').show()
        $('#start_recording_text').hide()
        $('#stop_recording_text').show()
        $('#error').hide()
        $('#request_id').parent().hide()
    }

    speechRecognition.onend = function(e) {
        $('#start_recording').show()
        $('#stop_recording').hide()
        $('#start_recording_text').show()
        $('#stop_recording_text').hide()
        $('#request_id').parent().show()
    }

    speechRecognition.onerror = function(e) {
        speechRecognition.stop()
        $('#error').html("<strong>" + e + "</strong> Please try again later.").show()
    }

    $('#start_recording').click(function() {
        lang = $('#language-model').val()
        speechRecognition.start(lang);
    });

    $('#stop_recording').click(function() {
        speechRecognition.stop();
    });

    var modelSelect = $('#language-model');
    $.each(models, function(id, label) {
        modelSelect.append($("<option></option>").attr("value", id).text(label))
    })

    modelSelect.change(function(elem) {
        $('.lang-description').hide();
        $('#' + modelSelect.val()).show();
    });

});
