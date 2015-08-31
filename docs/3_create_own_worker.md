# Create an own worker
- First, create a folder inside `examples`. In this tutorial we will use name `worker_example`.

- Create a folder `examples/worker_example/models` and put your Kaldi files to this folder.

- Create a file `examples/worker_example/config.py` with your Kaldi configuration with the following contents:
    ```python
    basedir = '/opt/models'
    wst_path = '%s/words.txt' % basedir
    kaldi_config = [
        '--config=%s/mfcc.conf' % basedir,
        '--verbose=0', '--max-mem=10000000000', '--beam=12.0',
        '--acoustic-scale=0.2', '--lattice-beam=2.0', '--max-active=5000',
        '%s/tri2b_bmmi.mdl' % basedir,
        '%s/HCLG_tri2b_bmmi.fst' % basedir,
        '1:2:3:4:5:6:7:8:9:10:11:12:13:14:15:16:17:18:19:20:21:22:23:24:25',
        '%s/tri2b_bmmi.mat' % basedir
    ]
    ```

- Create a file  `examples/worker_example/Dockerfile` with the following contents:
    ```
    FROM ufaldsg/cloud-asr-worker
    MAINTAINER Ondrej Klejch

    WORKDIR /opt/app
    ADD config.py /opt/app/config.py
    ADD models /opt/models

    ENV MODEL example
    ```
- Build a Docker image with command:
  `docker build -t ufaldsg/cloud-asr-worker-example examples/worker_example`

- Edit `cloudasr.json` and put following line into the workers section:
    ```json
        {"image": "ufaldsg/cloud-asr-worker-example", "model": "example", "instances": 1}
    ```

- Run CloudASR platform with `make run_locally`.

- Test that your worker works with the command:
    ```bash
    curl -X POST --data-binary @resources/test.wav --header 'Content-Type: audio/x-wav; rate=16000;' 'http://localhost:8000/recognize?lang=example'
    ```
