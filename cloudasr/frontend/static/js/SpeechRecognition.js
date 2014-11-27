(function(window){

    var SpeechRecognition = function() {
        this.continuous = true;
        this.interimResults = true;
        this.onstart = function() {};
        this.onresult = function(event) {};
        this.onerror = function(event) {};
        this.onend = function() {};
        this.isRecording = false;

        var recognizer = this;
        var recorder = createRecorder();
        var socket = createSocket();

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

        function createSocket() {
            socket = io.connect();

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
            socket.emit("chunk", {chunk: floatTo16BitPCM(chunk[0]), frame_rate: 44100});
        }

        function floatTo16BitPCM(chunk){
            result = [];
            for( i = 0; i < chunk.length; i++ ) {
                var s = Math.max(-1, Math.min(1, chunk[i]));
                result[i] = Math.round(s < 0 ? s * 0x8000 : s * 0x7FFF);
            }

            return result;
        }

    }

    window.SpeechRecognition = SpeechRecognition;

})(window);
