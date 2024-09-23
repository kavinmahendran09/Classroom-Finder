#!/usr/bin/env bash

# Download and install Chromium
CHROME_VERSION=$(curl -sS https://omahaproxy.appspot.com/linux | grep -oP "\d{8}")
wget https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F${CHROME_VERSION}%2Fchrome-linux.zip?alt=media -O chrome-linux.zip
unzip chrome-linux.zip
mv chrome-linux /usr/local/chromium
