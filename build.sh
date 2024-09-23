#!/bin/bash

# Update package list
apt-get update

# Install necessary packages
apt-get install -y wget unzip

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f

# Check where Chrome is installed and print it
echo "Checking Google Chrome installation path..."
which google-chrome
google-chrome --version

# Install Python dependencies
pip install -r requirements.txt
