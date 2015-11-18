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

            var $currentResult = $('#result-evaluation .current');
            var $wrong = $('<a href="#" class="btn btn-xs btn-danger"><span class="glyphicon glyphicon-remove"></span></a>');
            $wrong.click(function() {
                $currentResult.empty()

                $input = $("<input type='text' class='form-control' />").val(transcript);
                $button = $("<input type='button' value='Save transcription' class='btn btn-success' />");
                $button.click(function() {
                    if($input.val() == transcript) {
                        return alert("Please, correct the transcription.");
                    }

                    var request_data = JSON.stringify({
                        "user_id": user_id,
                        "recording_id": result.chunk_id,
                        "transcription": $input.val()
                    });

                    $.post(apiUrl + "/transcribe", request_data, function(data) {
                        $currentResult.text($input.val());
                        $currentResult.prepend($('<div class="text-right pull-right"><strong>Thank you!</strong></div>'));
                    });
                });

                $form = $("<form class='form-horizontal'></form>");
                $form.append($("<div class='col-sm-10'></div>").append($input));
                $form.append($("<div class='text-right'></div>").append($button));
                $currentResult.append($form);
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
        $('#canvas').show();
    }

    speechRecognition.onend = function(e) {
        $('#start_recording').show()
        $('#stop_recording').hide()
        $('#start_recording_text').show()
        $('#stop_recording_text').hide()
        $('#request_id').parent().show()
        $('#canvas').hide();
    }

    speechRecognition.onerror = function(e) {
        $('#error').html("<strong>" + e + "</strong> Please try again later.").show()
    }

    speechRecognition.onchunk = function(chunk) {
        var peaks = getPeaks(chunk, 256);
        drawPeaks(peaks);
    }

    function getPeaks(channels, length) {
        var sampleSize = channels[0].length / length;
        var sampleStep = ~~(sampleSize / 10) || 1;
        var mergedPeaks = [];

        for (var c = 0; c < channels.length; c++) {
            var peaks = [];
            var chan = channels[c];

            for (var i = 0; i < length; i++) {
                var start = ~~(i * sampleSize);
                var end = ~~(start + sampleSize);
                var min = chan[start];
                var max = chan[start];

                for (var j = start; j < end; j += sampleStep) {
                    var value = chan[j];

                    if (value > max) {
                        max = value;
                    }

                    if (value < min) {
                        min = value;
                    }
                }

                var floatToInt16 = function(x) {
                    return Math.round(x < 0 ? x * 0x8000 : x * 0x7FFF);
                }

                max = floatToInt16(max);
                min = floatToInt16(min);
                peaks[2 * i] = max;
                peaks[2 * i + 1] = min;

                if (c == 0 || max > mergedPeaks[2 * i]) {
                    mergedPeaks[2 * i] = max;
                }

                if (c == 0 || min < mergedPeaks[2 * i + 1]) {
                    mergedPeaks[2 * i + 1] = min;
                }
            }
        }

        return mergedPeaks;
    }

    function drawPeaks(peaks) {
        var canvasEl = document.getElementById('canvas');
        var canvas = canvasEl.getContext('2d');
        var params_height = canvasEl.height;
        var params_width = canvasEl.width;
        var params_waveColor = "black";

        var $ = 0.5;
        var height = params_height;
        var halfH = height / 2
        var length = ~~(peaks.length / 2);
        var scale = params_width / length ;
        var absmax = 2 << 15;

        canvas.clearRect(0, 0, params_width, params_height);
        canvas.fillStyle = params_waveColor;

        canvas.beginPath();
        canvas.moveTo($, halfH);

        for (var i = 0; i < length; i++) {
            var h = Math.round(peaks[2 * i] / absmax * halfH);
            canvas.lineTo(i * scale + $, halfH - h);
        }

        for (var i = length - 1; i >= 0; i--) {
            var h = Math.round(peaks[2 * i + 1] / absmax * halfH);
            canvas.lineTo(i * scale + $, halfH - h);
        }

        canvas.closePath();
        canvas.fill();

        canvas.fillRect(0, 0, params_width, $/2);
        canvas.fillRect(0, height - $/2, params_width, $/2);
        canvas.fillRect(0, halfH - $, params_width, $);
    }

    $('#start_recording').click(function() {
        lang = $('#acoustic-model').val()
        speechRecognition.start(lang);
        speechRecognition.changeLM($('#language-model').val());
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

    var acousticModelSelect = $('#acoustic-model');
    var languageModelSelect = $('#language-model');
    var models = [];

    acousticModelSelect.change(function() {
        $('.lang-name').text(models[acousticModelSelect.val()]["name"]);
        $('.lang-description').html(models[acousticModelSelect.val()]["description"]);

        languageModelSelect.empty();
        var languageModels = models[acousticModelSelect.val()]["language_models"];
        if(languageModels.length == 0) {
            languageModelSelect.hide();
        } else {
            $.each(languageModels, function(i, model) {
                languageModelSelect.append($("<option></option>").attr("value", model["key"]).text(model["name"]));
            });
            languageModelSelect.show();
        }
    });

    languageModelSelect.change(function(event) {
        if(speechRecognition.isRecording) {
            speechRecognition.changeLM(languageModelSelect.val());
        }
    });

    $.get(availableWorkersUrl, function(data) {
        $.each(data["workers"], function(key, value) {
            models[value["id"]] = value;
            acousticModelSelect.append($("<option></option>").attr("value", value["id"]).text(value["name"]));
        });

        acousticModelSelect.val(model);
        acousticModelSelect.trigger('change');
    });

});
