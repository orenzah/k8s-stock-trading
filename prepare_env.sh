#!/bin/bash
sudo apt-get install update
sudo apt-get install -y python3 python3-pip
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
pip install -r ./stocks/requirements.txt
pip install -r ./ci/requirements.txt
pip install -r ./gdelt/requirements.txt