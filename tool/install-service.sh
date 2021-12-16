#!/bin/bash

smartpot_service="smart-pot-hub.service"
service_file="/lib/systemd/system/$smartpot_service"

# Create service configuration file.
echo """\
[Unit]
Description=Smart Pot Hub
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$PWD
ExecStart=/usr/bin/python3 -m smartpot
Restart=on-abort

[Install]
WantedBy=multi-user.target
""" | sudo tee "$service_file" > /dev/null

# Enable smart pot service.
sudo chmod 644 "$service_file"
sudo systemctl daemon-reload
sudo systemctl enable "$smartpot_service"
sudo systemctl start "$smartpot_service"
