#!/bin/bash

virtualenv venv -p python3
source ./venv/bin/activate

pip3 install cryptography
pip3 install numpy
pip3 install matplotlib