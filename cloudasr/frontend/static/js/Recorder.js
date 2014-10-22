(function(window){

    var Recorder = function(cfg){
        var config = cfg || {};
        var bufferLen = config.bufferLen || 16384;
        var numChannels = config.numChannels || 1;
        var bufferCallback = config.bufferCallback || function(buffer) { console.log(buffer); };
        var errorCallback = config.errorCallback || function(error) { console.log(error); };
        var recording = false;
        var sourceProcessor = null;

        this.init = function() {
            audio_context = createAudioContext();
            navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
                errorCallback('No live audio input: ' + e);
            });
        }

        this.configure = function(cfg){
            for (var prop in cfg){
                if (cfg.hasOwnProperty(prop)){
                    config[prop] = cfg[prop];
                }
            }
        }

        this.record = function(){
            recording = true;
        }

        this.stop = function(){
            recording = false;
        }

        function createAudioContext() {
            try {
                window.AudioContext = window.AudioContext || window.webkitAudioContext;
                navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

                audio_context = new AudioContext;
                console.log('Audio context set up.');
                console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));

                return audio_context;
            } catch (e) {
                errorCallback('No web audio support in this browser!');
            }
        }

        function startUserMedia(stream) {
            var source = audio_context.createMediaStreamSource(stream);
            console.log('Media stream created.');

            source.context.createScriptProcessor = source.context.createScriptProcessor || source.context.createJavaScriptNode;
            sourceProcessor = source.context.createScriptProcessor(bufferLen, numChannels, numChannels);

            sourceProcessor.onaudioprocess = function(e){
                if (!recording) return;
                var buffer = [];
                for (var channel = 0; channel < numChannels; channel++){
                        buffer.push(e.inputBuffer.getChannelData(channel));
                }

                bufferCallback(buffer);
            }

            source.connect(sourceProcessor);
            sourceProcessor.connect(source.context.destination);
            console.log('Input connected to audio context destination.');
        }

    };

    window.Recorder = Recorder;

})(window);
