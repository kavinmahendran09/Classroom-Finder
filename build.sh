#!/bin/bash

# Update package list
sudo apt-get update

# Install necessary packages
sudo apt-get install -y wget unzip

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f  # Fix any missing dependencies

# Install Python dependencies
pip install -r requirements.txt
