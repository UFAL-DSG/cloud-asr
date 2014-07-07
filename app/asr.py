from kaldi.decoders import PyOnlineLatgenRecogniser
from kaldi.utils import lattice_to_nbest, wst2dict
from StringIO import StringIO
import wave

recogniser = None
wst = None


def asr_init(basedir):
    create_recogniser(basedir)
    create_dictionary(basedir)


def create_recogniser(basedir):
    global recogniser

    recogniser = PyOnlineLatgenRecogniser()
    argv = ['--config=%s/models/mfcc.conf' % basedir,
            '--verbose=0', '--max-mem=10000000000', '--lat-lm-scale=15', '--beam=12.0',
            '--lattice-beam=6.0', '--max-active=5000',
            '%s/models/tri2b_bmmi.mdl' % basedir,
            '%s/models/HCLG_tri2b_bmmi.fst' % basedir,
            '1:2:3:4:5:6:7:8:9:10:11:12:13:14:15:16:17:18:19:20:21:22:23:24:25',
            '%s//models/tri2b_bmmi.mat' % basedir]
    recogniser.setup(argv)


def create_dictionary(basedir):
    global wst

    wst = wst2dict('%s/models/words.txt' % basedir)


def recognize_wav(data, def_sample_width=2, def_sample_rate=16000):
    wav = load_wav_from_request_data(data, def_sample_width)
    pcm = convert_wav_to_pcm(wav, def_sample_rate)

    recognize_chunk(pcm)
    return nbest_hypotheses(n=10)

    return create_response(hypotheses)


def recognize_chunk(pcm):
    global recogniser

    decoded_frames = 0
    recogniser.frame_in(pcm)
    dec_t = recogniser.decode(max_frames=10)
    while dec_t > 0:
        decoded_frames += dec_t
        dec_t = recogniser.decode(max_frames=10)

    return recogniser.get_best_path()


def nbest_hypotheses(n=10):
    global recogniser

    recogniser.prune_final()
    utt_lik, lat = recogniser.get_lattice()
    recogniser.reset()

    return [(prob, path_to_text(path)) for (prob, path) in lattice_to_nbest(lat, n=10)]


def path_to_text(path):
    global wst
    return u' '.join([unicode(wst[w]) for w in path])


def load_wav_from_request_data(data, def_sample_width):
    wav = wave.open(StringIO(data), 'r')
    if wav.getnchannels() != 1:
        raise Exception('Input wave is not in mono')
    if wav.getsampwidth() != def_sample_width:
        raise Exception('Input wave is not in %d Bytes' % def_sample_width)

    return wav


def convert_wav_to_pcm(wav, def_sample_rate):
    try:
        chunk = 1024
        pcm = b''
        pcmPart = wav.readframes(chunk)

        while pcmPart:
            pcm += str(pcmPart)
            pcmPart = wav.readframes(chunk)

        return resample_to_def_sample_rate(pcm, wav.getframerate(), def_sample_rate)
    except EOFError:
        raise Exception('Input PCM is corrupted: End of file.')


def resample_to_def_sample_rate(pcm, sample_rate, def_sample_rate):
    if sample_rate != def_sample_rate:
        import audioop
        pcm, state = audioop.ratecv(pcm, 2, 1, sample_rate, def_sample_rate, None)

    return pcm


def create_response(hypotheses):
    return {
        "result": [
            {
                "alternative": [{"transcript": t, "confidence": c} for (c,t) in hypotheses],
                "final": True,
            },
        ],
        "result_index": 0
    }
