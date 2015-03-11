var lastResult;

$(document).ready(function() {
    var speechRecognition = new SpeechRecognition(apiUrl);
    var $result = $('#result');

    speechRecognition.onresult = function(result) {
        var transcript = result.result.hypotheses[0].transcript;
        if(transcript == '') {
            return;
        }

        $('#result-evaluation .current').text(transcript + " ");
        $('#result-dictation .current').text(transcript + " ");

        if(result.final) {
            var $vote = $('<div class="text-right pull-right"></div>');
            var $right = $('<a href="#" class="btn btn-xs btn-success"><span class="glyphicon glyphicon-ok"></span></a>');
            $right.click(function() {
                var request_data = JSON.stringify({
                    "user_id": user_id,
                    "recording_id": result.chunk_id,
                    "transcription": transcript
                });

                $.post(apiUrl + "/transcribe", request_data, function(data) {
                    $vote.html("<strong>Thank you!</strong>");
                });
            });

            var $wrong = $('<a href="#" class="btn btn-xs btn-danger"><span class="glyphicon glyphicon-remove"></span></a>');
            $wrong.click(function() {
                $vote.html("<a href='/transcribe/" + result.chunk_id + "'>Add your transcription</a>");
            });
            $vote.append($right, "<span> </span>", $wrong);

            $('#result-evaluation .current').prepend($vote);

            $('#result-evaluation .current').removeClass("current");
            $('#result-evaluation').append("<div class='current transcription-result'></div>");
            $('#result-dictation .current').removeClass("current");
            $('#result-dictation').append("<span class='current transcription-result'></span>");
        }

        $('#request_id').text(result.request_id);
    }

    speechRecognition.onstart = function(e) {
        $('#start_recording').hide()
        $('#stop_recording').show()
        $('#start_recording_text').hide()
        $('#stop_recording_text').show()
        $('#error').hide()

        $('#result-dictation').html("<span class='current transcription-result'></span>");
        $('#result-evaluation').html("<div class='current transcription-result'></div>");
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

    $('#dictation').click(function() {
        $('#evaluation').parent().removeClass('active');
        $('#dictation').parent().addClass('active');

        $('#result-evaluation').hide();
        $('#result-dictation').show();
    });

    $('#evaluation').click(function() {
        $('#dictation').parent().removeClass('active');
        $('#evaluation').parent().addClass('active');

        $('#result-dictation').hide();
        $('#result-evaluation').show();
    });

    var modelSelect = $('#language-model');
    var models = [];

    $.get(availableWorkersUrl, function(data) {
        $.each(data["workers"], function(key, value) {
            models[value["id"]] = value;
            modelSelect.append($("<option></option>").attr("value", value["id"]).text(value["name"]));
        });

        modelSelect.val(model);
        $('.lang-name').text(models[modelSelect.val()]["name"]);
        $('.lang-description').html(models[modelSelect.val()]["description"]);
    });

    modelSelect.change(function(elem) {
        $('.lang-name').text(models[modelSelect.val()]["name"]);
        $('.lang-description').html(models[modelSelect.val()]["description"]);
    });

});
