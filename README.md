# pywaykit

**Wayland-compatible WhatsApp Web automation inspired by pywhatkit**  
`pywaykit` enables programmatic WhatsApp messaging via browser automation and system-level input simulation using `Playwright` and `ydotool`.  
Designed for Linux systems — especially Wayland — where traditional GUI automation tools do not work.

---

## Features

- Send WhatsApp messages from Python
- Schedule messages for a specific time
- Silent message delivery using browser events
- Extract chat messages from loaded WhatsApp page
- Persistent login via Firefox profile

---

## Installation

Install with pip:

```bash
pip install pywaykit
```

Install Playwright's browser binaries:

```bash
playwright install firefox
```

---

## ydotool Setup (Required)

`ydotool` is used for input simulation under Wayland.  
You must perform the following setup steps:

### 1. Add your user to the input group:

```bash
sudo usermod -aG input $USER
```

### 2. Create a udev rule (script provided in the repo):

```bash
bash initial.sh
```

**initial.sh**
```bash
#!/bin/bash

sudo touch /etc/udev/rules.d/99-uinput.rules
echo "Created udev rule at /etc/udev/rules.d/99-uinput.rules"

sudo bash -c 'echo KERNEL=="uinput", GROUP="input", MODE="0660" > /etc/udev/rules.d/99-uinput.rules'

echo "Reloading Udev rules."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Execution Completed."
```

---

## Usage

### Send a WhatsApp Message

```python
from pywaykit import send_msg

send_msg(
    phone_no="91xxxxxxxxxx",
    message="Hello from pywaykit",
    silent=False,
    scheduled="14:45:00",  # Optional (HH:MM:SS)
    instant=5,             # Optional delay after send
    log=True
)
```

### Extract Messages from Chat

```python
from pywaykit import read_wmsg

stored_text, a_msgs, b_msgs = read_wmsg()
```

### Load WhatsApp Chat (No Message Sent)

```python
from pywaykit import get_message_data

get_message_data(phone_no="+91xxxxxxxxxx", message=" ") # here the message arg does almost nothing so keep it as an empty string.
```

---

## Notes

- Works only on Linux with Firefox.
- First run requires QR login (saved for future runs).
- Feel free to contribute.
---

## If you like this project, give this repo a ⭐ !
