#!/usr/bin/env bash

# Download Chromium binary
CHROME_BIN_DIR="chrome"
mkdir -p $CHROME_BIN_DIR
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O $CHROME_BIN_DIR/google-chrome.deb
dpkg -x $CHROME_BIN_DIR/google-chrome.deb $CHROME_BIN_DIR
export PATH="$CHROME_BIN_DIR/opt/google/chrome:$PATH"

# Install Python dependencies
pip install -r requirements.txt
