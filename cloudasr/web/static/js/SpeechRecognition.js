(function(window){

    var SpeechRecognition = function(apiUrl) {
        this.continuous = true;
        this.interimResults = true;
        this.onstart = function() {};
        this.onresult = function(event) {};
        this.onerror = function(event) {};
        this.onend = function() {};
        this.isRecording = false;

        var recognizer = this;
        var recorder = createRecorder();
        var socket = createSocket(apiUrl);

        this.start = function(model) {
            socket.emit('begin', {'model':model});
            recorder.record();
            this.isRecording = true;
            this.onstart();
        };

        this.stop = function() {
            socket.emit('end', {});
            recorder.stop();
            this.isRecording = false;
            this.onend();
        };

        var handleResult = function(results) {
            recognizer.onresult(results);
        };

        var handleError = function(error) {
            recognizer.onerror(error);
            recognizer.stop();
        };

        var handleEnd = function() {
            recognizer.onend();
        };

        function createSocket(apiUrl) {
            socket = io.connect(apiUrl);

            socket.on("connect", function() {
                console.log("Socket connected");
            });

            socket.on("connect_failed", function() {
                handleError("Unable to connect to the server.");
            });

            socket.on("result", function(result) {
                handleResult(result);
            });

            socket.on("error", function(error) {
                handleError(error);
            });

            socket.on("server_error", function(error) {
                handleError(error.message);
            });

            socket.on("end", function(error) {
                handleEnd();
            });

            return socket;
        }

        function createRecorder() {
            recorder = new Recorder({
                bufferCallback: handleChunk,
                errorCallback: handleError
            });
            recorder.init();

            return recorder;
        }

        function handleChunk(chunk) {
            socket.emit("chunk", {chunk: encode16BitPcmToBase64(floatTo16BitPcm(chunk[0])), frame_rate: 44100});
        }

        function floatTo16BitPcm(chunk) {
            result = [];
            for( i = 0; i < chunk.length; i++ ) {
                var s = Math.max(-1, Math.min(1, chunk[i]));
                result[i] = Math.round(s < 0 ? s * 0x8000 : s * 0x7FFF);
            }

            return result;
        }

        function encode16BitPcmToBase64(pcm) {
            chars = []
            for(i=0; i < pcm.length; i++) {
                lower = pcm[i] & 255;
                upper = pcm[i] >> 8;
                if(upper < 0) {
                    upper += 256;
                }

                chars[2*i] = String.fromCharCode(lower);
                chars[2*i+1] = String.fromCharCode(upper);
            }

            return btoa(chars.join(""));
        }

    }

    window.SpeechRecognition = SpeechRecognition;

})(window);
