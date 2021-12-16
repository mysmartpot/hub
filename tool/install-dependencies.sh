#!/bin/bash

# This script installs the packages needed to run the Smart Pot Hub.

# Update all installed packages.
sudo apt-get update
sudo apt-get upgrade -y

# Install bluetooth stack.
sudo apt-get install -y bluetooth bluez libbluetooth-dev libudev-dev

# Install python library for BLE.
sudo apt-get install -y python3-pip
sudo pip3 install bleak

# Install python libraries for REST API.
sudo pip3 install Flask Flask-JSON

# Install utility libraries.
sudo pip3 install mvar
