#!/usr/bin/env bash

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Download and install Chromium (stable version)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb

# Install the downloaded Chrome package
apt-get update
apt-get install -y ./chrome.deb

# Clean up the package
rm chrome.deb
