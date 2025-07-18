#!/bin/bash

sudo touch /etc/udev/rules.d/99-uinput.rules

echo "Created udev rule at /etc/udev/rules.d/99-uinput.rules"

sudo echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' >> /etc/udev/rules.d/99-uinput.rules

echo "Reloading Udev rules."

sudo udevadm control --reload-rules

sudo udevadm trigger

echo "Execution Completed."
