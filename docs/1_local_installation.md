# Local Installation of CloudASR

- First, pull the CloudASR git repository from Github with the following command:
    ```shell
    git clone https://github.com/UFAL-DSG/cloud-asr.git
    ```
- Second, install Docker on your machine.
    You can follow the install instructions for your distribution at [http://docs.docker.com/installation/](http://docs.docker.com/installation/).

- Third, go to cloud-asr folder and download images with the command:
    ```shell
    make pull
    ```

- Additionally, if you want to develop CloudASR, it is neccessary to install python requirements for testing with command:
    ```shell
    pip install requirements-pip.txt
    ```
