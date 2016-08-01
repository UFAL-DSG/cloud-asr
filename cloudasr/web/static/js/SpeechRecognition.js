(function(window){

    var SpeechRecognition = function(apiUrl) {
        this.continuous = true;
        this.interimResults = true;
        this.onstart = function() {};
        this.onresult = function(event) {};
        this.onerror = function(event) {};
        this.onend = function() {};
        this.onchunk = function(chunk) {};
        this.volumeCallback = function(volume) {};
        this.isRecording = false;
        this.quietForChunks = 0;

        var recognizer = this;
        var recorder = createRecorder();
        var socket = createSocket(apiUrl);

        this.start = function(model) {
            socket.send(model);
            socket.send(44100);
            recorder.record();
            this.isRecording = true;
            this.onstart();
        };

        this.stop = function() {
            socket.send("");
            recorder.stop();
            this.isRecording = false;
            this.onend();
        };

        this.changeLM = function(newLM) {
            console.log("Not supported at the moment.");
        }

        var handleResult = function(results) {
            recognizer.onresult(results);
        };

        var handleError = function(error) {
            recognizer.onerror(error);
            recognizer.onend();
            recognizer.isRecording = false;
            recorder.stop();
        };

        var handleEnd = function() {
            recognizer.onend();
        };

        function createSocket(apiUrl) {
            wsApiUrl = apiUrl.replace('http', 'ws') // works also for https and wss
            socket = new WebSocket(wsApiUrl + "/transcribe-online");

            socket.onopen = function() {
                console.log("Socket connected");
            };

            socket.onerror = function(error) {
                handleError(error);
            };

            socket.onmessage = function(message) {
                message = JSON.parse(message.data);

                if(message["status"] == "error") {
                    handleError(message);
                } else {
                    handleResult(message);
                }
            };

            socket.onclose = function(error) {
                console.log('Speech socket disconnected'); 
                handleEnd();
            };

            return socket;
        }

        function createRecorder() {
            recorder = new Recorder({
                bufferCallback: handleChunk,
                errorCallback: handleError,
                volumeCallback: handleVolume,
            });
            recorder.init();

            return recorder;
        }

        function handleChunk(chunk) {
            socket.send(floatTo16BitPcm(chunk[0]));
            recognizer.onchunk(chunk);
        }

        function floatTo16BitPcm(chunk) {
            result = new Int16Array(chunk.length);
            for( i = 0; i < chunk.length; i++ ) {
                var s = Math.max(-1, Math.min(1, chunk[i]));
                result[i] = Math.round(s < 0 ? s * 0x8000 : s * 0x7FFF);
            }

            return result.buffer;
        }

        function handleVolume(volume) {
            if(volume == 0) {
                if(recognizer.quietForChunks >= 10) {
                    return handleError("Microphone is not working!");
                }

                recognizer.quietForChunks++;
            } else {
                recognizer.quietForChunks = 0;
            }

            recognizer.volumeCallback(volume);
        };
    }

    window.SpeechRecognition = SpeechRecognition;

})(window);
