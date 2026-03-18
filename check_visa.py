import os
import smtplib
import urllib.parse
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

URL = "https://schengenappointments.com/in/london/netherlands/tourism"
BOOKING_URL = "https://visa.vfsglobal.com/gbr/en/nld/login"
STATE_FILE = "state.txt"
NO_APPOINTMENTS_TEXT = "No appointments available"


def get_status():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    h5 = soup.find("h5")
    if not h5:
        raise ValueError("Could not find <h5> status element on page")

    status = h5.get_text(separator=" ", strip=True)
    for a in h5.find_all("a"):
        status = status.replace(a.get_text(), "").strip()

    return status


def read_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return f.read().strip()
    return None


def write_state(status):
    with open(STATE_FILE, "w") as f:
        f.write(status)


def send_email(status):
    gmail_address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEText(
        f"Appointment status: {status}\n\n"
        f"Check availability: {URL}\n"
        f"Book now: {BOOKING_URL}"
    )
    msg["Subject"] = "\U0001f1f3\U0001f1f1 Netherlands Visa Slot Alert!"
    msg["From"] = gmail_address
    msg["To"] = gmail_address

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_address, app_password)
        server.send_message(msg)

    print("Email notification sent.")


def send_whatsapp(status):
    phone = os.environ["CALLMEBOT_PHONE"]
    apikey = os.environ["CALLMEBOT_APIKEY"]

    message = f"Netherlands Visa: {status} - Check: {URL} - Book: {BOOKING_URL}"
    encoded_message = urllib.parse.quote(message)

    api_url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={phone}&text={encoded_message}&apikey={apikey}"
    )
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    print("WhatsApp notification sent.")


def main():
    status = get_status()
    print(f"Current status: {status}")

    last_state = read_last_state()
    print(f"Last state: {last_state!r}")

    appointments_available = True  # TEMP: force notification for testing

    if appointments_available:
        if last_state != status:
            print("Appointments available! Sending notifications...")
            send_email(status)
            send_whatsapp(status)
            write_state(status)
        else:
            print("Appointments available but state unchanged — notifications already sent.")
    else:
        print("No appointments available. No notification needed.")
        write_state(status)


if __name__ == "__main__":
    main()
