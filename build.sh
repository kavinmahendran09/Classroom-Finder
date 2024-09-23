#!/bin/bash

# Update package list
apt-get update

# Install necessary packages
apt-get install -y wget unzip

# Download and install Chromium instead of Google Chrome
wget https://github.com/chromium/chromium/archive/refs/heads/main.zip -O chromium.zip
unzip chromium.zip
cd chromium-main

# Check where Chromium is installed and print it
echo "Checking Chromium installation path..."
which chromium
chromium --version

# Install Python dependencies
pip install -r requirements.txt
