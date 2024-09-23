#!/usr/bin/env bash
# Update and install dependencies
apt-get update && apt-get install -y wget unzip
apt-get install -y chromium-browser

# Make the Chromium browser available to Selenium
CHROME_BIN=$(which chromium-browser)
