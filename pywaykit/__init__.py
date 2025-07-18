# start vars
import os
import time
import subprocess
from screeninfo import get_monitors

subprocess.run("kill $(ps aux | grep '[y]dotoold' | awk '{print $2}')",shell=True)
subprocess.run("ydotoold > /dev/null 2>&1 &",shell=True)

time.sleep(1)

ROOT_DIR = os.path.join(os.getenv("HOME"),"./pywaykit")

if not os.path.exists(ROOT_DIR):
    os.mkdir(ROOT_DIR)


for m in get_monitors():
    s_width, s_height = m.width, m.height

t = time.localtime()
hours,mins,secs = int(time.strftime("%H", t)),int(time.strftime("%M", t)),int(time.strftime("%S", t))

from .main import send_msg, read_wmsg, get_message_data