# Schengen Visa Appointment Monitor

Monitors https://schengenappointments.com/in/london/netherlands/tourism every 5 minutes for Netherlands tourism visa slots. Sends email + WhatsApp notifications when slots open.

Runs entirely on **GitHub Actions** — no server needed, completely free.

---

## Setup

### 1. Fork and push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
gh repo create schengen-visa-notif --public --source=. --push
# or: git remote add origin https://github.com/YOUR_USERNAME/schengen-visa-notif.git && git push -u origin main
```

### 2. Get a Gmail App Password

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** if not already on
3. Search for **App passwords** (or go to https://myaccount.google.com/apppasswords)
4. Create a new app password — name it "Visa Monitor"
5. Copy the 16-character password (no spaces)

### 3. Set up CallMeBot (WhatsApp)

1. Add `+34 644 59 77 59` to your WhatsApp contacts (name it "CallMeBot")
2. Send the message: `I allow callmebot to send me messages`
3. Wait for a reply with your API key (usually arrives within a minute)

### 4. Add GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `GMAIL_ADDRESS` | Your Gmail address (e.g. `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character app password from step 2 |
| `CALLMEBOT_PHONE` | Your phone with country code, no `+` (e.g. `447911123456`) |
| `CALLMEBOT_APIKEY` | The API key from the CallMeBot WhatsApp reply |

### 5. Verify it works

Go to **Actions tab → Check Visa Appointments → Run workflow** to trigger a manual run.

Check the logs — you should see:
```
Current status: No appointments available
Last state: None
No appointments available. No notification needed.
```

---

## Testing notifications

To force a notification to test your email/WhatsApp setup, temporarily edit `check_visa.py` and change:

```python
appointments_available = NO_APPOINTMENTS_TEXT not in status
```

to:

```python
appointments_available = True
```

Trigger a manual run, verify you receive the email and WhatsApp message, then revert the change.

---

## How it works

- GitHub Actions runs the workflow every 5 minutes via cron
- `check_visa.py` scrapes the page and extracts the `<h5>` status text
- `state.txt` (cached between runs via `actions/cache`) tracks the last known status
- Notifications are only sent when status **changes** from unavailable → available (no spam)
- Both email (Gmail SMTP) and WhatsApp (CallMeBot API) are notified simultaneously
