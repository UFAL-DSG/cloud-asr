(function(window){

    var SpeechRecognition = function() {
        this.continuous = true;
        this.interimResults = true;
        this.onstart = function() {};
        this.onresult = function(event) {};
        this.onerror = function(event) {};
        this.onend = function() {};

        var recognizer = this;
        var recorder = createRecorder();
        var socket = createSocket();

        this.start = function() {
            socket.emit('begin', {'lang':'cs'});
            recorder.record();
            this.onstart();
        };

        this.stop = function() {
            socket.emit('end', {});
            recorder.stop();
            this.onend();
        };

        var handleResult = function(results) {
            recognizer.onresult(results.result);
        };

        var handleError = function(error) {
            recognizer.onerror(error);
        };

        var handleEnd = function() {
            recognizer.onend();
        };

        function createSocket() {
            socket = io.connect();

            socket.on("connection", function() {
                console.log("Socket connected");
            });

            socket.on("result", function(results) {
                handleResult(results);
            });

            socket.on("error", function(error) {
                handleError(error);
            });

            socket.on("end", function(error) {
                handleEnd();
            });

            return socket;
        }

        function createRecorder() {
            recorder = new Recorder({
                bufferCallback: handleChunk
            });
            recorder.init();

            return recorder;
        }

        function handleChunk(chunk) {
            socket.emit("chunk", {chunk: floatTo16BitPCM(chunk[0])});
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
