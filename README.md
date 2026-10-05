# PhonePhoning

Send a text message to one or more phone numbers on a schedule.

## How it works

Your code never talks to the phone network directly. It makes an HTTPS call to an SMS
gateway (Twilio here), and the gateway hands the message to the carriers. So the whole
problem is two pieces:

1. **A sender** that hits the gateway API (`send_sms.py`, or `send_sms.js` in Node).
2. **A scheduler** that runs the sender once a day (`.github/workflows/daily-sms.yml`,
   or a cron entry on any always-on machine).

## Setup

1. Create a Twilio account at twilio.com, get a phone number, and note your
   Account SID, Auth Token, and the number.
2. On a trial account you must verify each recipient number in the Twilio console
   before it will accept messages to it.
3. Install and run:

```bash
pip install -r requirements.txt
export TWILIO_ACCOUNT_SID=ACxxxxxxxx
export TWILIO_AUTH_TOKEN=xxxxxxxx
export TWILIO_FROM_NUMBER=+15550001111
python send_sms.py --to +13219164708 --message "hello"
```

## Running it daily

**Option A: GitHub Actions (nothing to host).** Add the three values above as repository
secrets under Settings > Secrets and variables > Actions. The workflow in
`.github/workflows/daily-sms.yml` runs every day at 13:00 UTC. Edit the cron line to change
the time. You can also trigger it by hand from the Actions tab.

**Option B: cron on a machine that is always on.** `crontab -e`, then:

```
0 9 * * * cd /path/to/PhonePhoning && TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=... TWILIO_FROM_NUMBER=... python send_sms.py
```

## Multiple recipients

Pass several numbers to `--to`, or edit `DEFAULT_RECIPIENTS` in `send_sms.py`.
Numbers must be in E.164 format: `+1` then the 10 digits for US numbers.
