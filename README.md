# Smart Pot Hub

The Smart Pots do not connect directly to the internet.
Instead they use Bluetooth Low Energy (BLE) to communicate with a central hub.
The central hub is connected to WiFi and offers an API for the Smart Pot App.
In this guide, the setup of the central hub is described.

## Setup

### Required Hardware

The following components are needed for the central node.

 - Raspberry Pi Zero W
 - An SD card with a capacity of at least one gigabyte.

Hereinafter we will refer to the components as "Pi" and "SD", respectively.

### OS Installation

 1. Install Raspberry Pi OS Lite on the SD using the [Raspberry Pi Imager][rpi-imager].

 2. Create an empty `ssh` file on the `boot` partition of the SD.

    ```sh
    touch ssh
    ```

 3. Create a file called `wpa_supplicant.conf` on the boot partition of the SD with the following contents.

    ```ini
    country=YOUR_COUNTY_CODE
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    network={
        ssid="YOUR_NETWORK_NAME"
        psk="YOUR_PASSWORD"
        key_mgmt=WPA-PSK
    }
    ```

    Replace `YOUR_NETWORK_NAME` and `YOUR_PASSWORD` with the SSID and password of your WiFi network and `YOUR_COUNTY_CODE` with the 2-digit county code of your country (e.g., `DE`).

 4. Put the SD into the Pi.

To verify that the installation was successful, you can now power up the Pi, wait for it to boot and connect via SSH using the following command.

```sh
ssh pi@raspberrypi
```

The default password of the `pi` user is `raspberry`.
Follow the guide in the next section to change the Pi's default configuration.

### OS Configuration

Connect to the Pi via SSH as described above and open the configuration tool by typing the following command.

```sh
sudo raspi-config
```

In the configuration tool, make the following changes.

 1. In `System Options > Password` assign a new password to the `pi` user.
    Changing the password is recommended for security reasons.

 2. In `System Options > Hostname` change the Pi's hostname to `smart-pot-hub`.
    Changing the hostname is required for the App to connect to the API.

Optionally, change other settings, then close the configuration tool and reboot the Pi by typing the following command.

```sh
sudo reboot now
```

Once the Pi has rebooted, use the new hostname to open an SSH session.

```sh
ssh pi@smart-pot-hub
```

### Firmware Installation

 1. Connect to the Pi via SSH as described above, clone this repository via Git or download the code as a zip file and extract it in the home directory of the `pi` user.
    Now, the following files and directories should exist.

    ```
    /home/pi/smart-pot-hub
    ├── README.md
    ├── smartpot
    └── tool
    ```

    During development the `./tool/upload.sh` script can be used to upload the code from your local machine to the Pi.

 2. Change into the root directory of the repository and run the installation script to download depdencies.

    ```sh
    cd /home/pi/smart-pot-hub
    ./tool/install.sh
    ```

 3. Confirm that the Smart Pot Hub service was installed and started successfully by typing the follwoing command.

    ```sh
    sudo systemctl status smart-pot-hub.service
    ```

[rpi-imager]:
  https://www.raspberrypi.org/software/
  "Install Raspberry Pi OS using Raspberry Pi Imager"
