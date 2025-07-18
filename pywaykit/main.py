import os
import time
import subprocess
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from . import hours, mins, secs, s_width, s_height, ROOT_DIR

# Path to save WhatsApp session/profile
save_location = os.path.join(os.getenv("HOME"))
PROFILE_DIR = os.path.join(ROOT_DIR, "./firefox_whatsapp_profile")


class Ydotool:
    """
    A class wrapper for ydotool commands to simulate keyboard and mouse events.
    """

    def type(self, typ: str):
        """
        Type the given string using ydotool.

        Args:
            typ (str): The string to type.
        """
        subprocess.run(f"ydotool type {typ}", shell=True)

    def key(self, value: int, state: int):
        """
        Simulate a key press or release.

        Args:
            value (int): Key code.
            state (int): 1 for press, 0 for release.
        """
        subprocess.run(f"ydotool key {value}:{state}", shell=True)

    def click(self, value: int):
        """
        Simulate a mouse click.

        Args:
            value (int): Mouse button value.
        """
        subprocess.run(f"ydotool click 0xC{str(value)}", shell=True)

    def Enter(self):
        """
        Simulate pressing the Enter key.
        """
        self.key(28, 1)
        self.key(28, 0)

    def Left_click(self):
        """
        Simulate a left mouse click.
        """
        self.click(0)

    def move(self, x: int, y: int):
        """
        Move the mouse cursor to the given screen coordinates.

        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.
        """
        subprocess.run(f"ydotool mousemove --absolute -x {x} -y {y}", shell=True)


def send_msg(phone_no: str, message: str, silent=False, scheduled=None, instant=None, log=False):
    """
    Send a WhatsApp message via web interface using Playwright and ydotool.

    Args:
        phone_no (str): Target phone number in international format.
        message (str): Message to send.
        silent (bool): Whether to suppress physical keypress simulation. Default is False.
        scheduled (str): Scheduled time in HH:MM:SS format. Default is None.
        instant (int): Delay after sending message before closing. Default is None.
        log (bool): Whether to print debug logs. Default is False.
    """
    tool = Ydotool()
    is_first_time = not os.path.exists(PROFILE_DIR)

    with sync_playwright() as p:
        print("Launching Firefox with persistent profile...")
        context = p.firefox.launch_persistent_context(PROFILE_DIR, headless=silent, args=["--start-maximized"])
        page = context.pages[0] if context.pages else context.new_page()
        page.set_viewport_size({"width": s_width, "height": s_height})

        start_time_to_sleep = 0
        if not is_first_time and scheduled:
            try:
                h, m, s = map(int, scheduled.split(":"))
                h_d, m_d, s_d = abs(hours - h), abs(mins - m), abs(secs - s)
                start_time_to_sleep = (h_d * 60 + m_d) * 60 + s_d
                if log:
                    print("Sleep:", start_time_to_sleep)
            except ValueError:
                if log:
                    print("Invalid scheduled format. Expected HH:MM:SS")

        time.sleep(start_time_to_sleep)

        page.goto(f"https://web.whatsapp.com/send?phone={phone_no}&text={message}", timeout=60000)

        if is_first_time:
            if log:
                print("First time run. Please scan the QR code. Waiting 40 seconds...")
            time.sleep(40)
        else:
            if log:
                print("Profile exists. Waiting for page to fully load...")
            tool.move(s_width - 1120, s_height - 780)
            time.sleep(2)
            tool.Left_click()

        try:
            page.wait_for_selector("div[role='textbox']", timeout=60000)
            if log:
                print("WhatsApp Web fully loaded.")
            time.sleep(5)
        except PlaywrightTimeoutError:
            print("Timeout: WhatsApp Web did not load properly.")

        # Send the message
        if not silent:
            tool.Enter()
            time.sleep(5)
        else:
            field = page.locator("div[contenteditable='true'][aria-label='Type a message']")
            field.press("Enter")
            time.sleep(2)

        # Save HTML snapshot
        html = page.content()
        with open(os.path.join(ROOT_DIR, "whatsapp_page.html"), "w", encoding="utf-8") as f:
            f.write(html)

        print("WhatsApp page HTML saved.")

        if instant:
            time.sleep(instant)

        print("Done. Browser closed.")


def read_wmsg():
    """
    Read and extract messages from a saved WhatsApp HTML page.

    Returns:
        tuple: (full_message_text, person_a_messages, person_b_messages)
    """
    stored_msg = ""
    people = []

    with open(os.path.join(ROOT_DIR, "whatsapp_page.html"), "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html5lib")
        messages = soup.find_all("div", class_="copyable-text")

        for msg in messages:
            meta = msg.get("data-pre-plain-text", "")
            index = meta.index("] ")
            index2 = meta.index(": ")
            name = meta[index + 1:index2].strip()
            people.append(name)

        people = sorted(set(people))

        if len(people) < 2:
            return stored_msg, [], []

        person_a, person_b = people[0], people[1]
        a_msgs, b_msgs = [person_a], [person_b]

        for msg in messages:
            meta = msg.get("data-pre-plain-text", "")
            index = meta.index("] ")
            index2 = meta.index(": ")
            name = meta[index + 1:index2].strip()
            text_span = msg.find("span", class_="selectable-text")
            text = text_span.text if text_span else ""

            full_msg = f"{meta} {text}"
            if name == person_a:
                a_msgs.append(full_msg)
            elif name == person_b:
                b_msgs.append(full_msg)

            stored_msg += f"\n{full_msg}"

    return stored_msg, a_msgs, b_msgs


def get_message_data(phone_no: str, message: str):
    """
    Launch WhatsApp Web with a profile and load chat with given message,
    saving the rendered HTML content for analysis.

    Args:
        phone_no (str): Target phone number.
        message (str): Message to send in chat input field (not sent).
    """
    is_first_time = not os.path.exists(PROFILE_DIR)

    with sync_playwright() as p:
        print("Launching Firefox with persistent profile...")

        if is_first_time:
            print("First time run. Please scan the QR code. Waiting 40 seconds...")
            context = p.firefox.launch_persistent_context(PROFILE_DIR, headless=False)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://web.whatsapp.com/", timeout=60000)
            time.sleep(40)
            print("Assuming login is done. Session saved.")
        else:
            context = p.firefox.launch_persistent_context(PROFILE_DIR, headless=True)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(f"https://web.whatsapp.com/send?phone={phone_no}&text={message}", timeout=60000)
            print("Profile exists. Waiting for page to fully load...")

        try:
            page.wait_for_selector("div[role='textbox']", timeout=60000)
            print("WhatsApp Web fully loaded.")
            time.sleep(3)
        except PlaywrightTimeoutError:
            print("Timeout: WhatsApp Web did not load properly.")

        html = page.content()
        with open(os.path.join(ROOT_DIR, "whatsapp_page.html"), "w", encoding="utf-8") as f:
            f.write(html)

        print("WhatsApp page HTML saved.")
        print("Done. Browser closed.")
