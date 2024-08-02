#!/usr/bin/env bash
echo -e "Installing required packages..."
sudo apt-get -y update >/dev/null
sudo apt install libpq5 >/dev/null

# install python packages
pip install -r requirements.txt >/dev/null
