# Running CloudASR Locally
- First, edit workers section in`cloudasr.json`:
    ```json
    {
        "domain": "cloudasr.com",
        "registry": "registry.hub.docker.com",
        "tag": "latest",
        "marathon_url": "http://127.0.0.1:8080",
        "master_ip": "127.0.0.1",
        "connection_string": "<mysql connection string>",
        "google_login_client_id": "<google login client id>",
        "google_login_client_secret": "<google login client secret>",
        "ga_tracking_id": "",
        "workers": [
            {"image": "ufaldsg/cloud-asr-worker-en-towninfo", "model": "en-towninfo", "instances": 1}
        ]
    }
    ```
    **Image** is name of worker Docker image, list of possible workers is at [https://hub.docker.com/u/ufaldsg/](https://hub.docker.com/u/ufaldsg/),
        **model** is a keyword which will be used for API requests
        and **instances** is a number of workers that should be started.

- Then, you can run CloudASR with command `make run_locally`.

- After that, you can try a web demo at address [http://localhost:8003/demo/en-towninfo](http://localhost:8003/demo/en-towninfo).
    You can also try curl request:
    ```bash
    curl -X POST --data-binary @resources/test.wav --header 'Content-Type: audio/x-wav; rate=16000;' 'http://localhost:8000/recognize?lang=en-towninfo'
    ```
    Or you can see list of running workers at address [http://localhost:8001/](http://localhost:8001/)

- If you want to use **Login with Google+** functionality,
    edit *google_login_client_id* and *google _login_client_secret* with values obtained at [console.developers.google.com](console.developers.google.com) at section *APIs & auth / Credentials* for *Authorized redirect URI* [localhost:8003/login/google](localhost:8003/login/google)

- If you want to use **Google Analytics**, edit *ga_tracking_id* with value obtained at [http://www.google.com/analytics/](http://www.google.com/analytics/).
