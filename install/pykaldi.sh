#!/bin/bash

set -e # Stop on any error

git clone https://github.com/UFAL-DSG/pykaldi pykaldi
cd pykaldi

pushd tools
  make atlas openfst_tgt

  pushd openfst
    ./configure --prefix=/usr
    sudo make install
  popd

  git clone https://github.com/UFAL-DSG/pyfst.git pyfst
  pushd pyfst
    sudo python setup.py install
  popd
popd

pushd src
  ./configure && \
  make depend && \
  make && \
  make test && \
  echo 'KALDI LIBRARY INSTALLED OK'

  pushd onl-rec && \
    make depend && \
    make && \
    make test && \
    echo 'OnlineLatgenRecogniser build OK'
  popd # onl-rec

  pushd pykaldi
    make && sudo make install && echo 'INSTALLATION Works OK'
    sudo python setup.py install && echo 'PYKALDI LIBRARY INSTALLED OK'
  popd # pykaldi

popd # src

