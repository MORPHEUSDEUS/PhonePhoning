"""Send an SMS to one or more phone numbers using Twilio.

Setup (one time):
    pip install -r requirements.txt
    export TWILIO_ACCOUNT_SID=ACxxxxxxxx
    export TWILIO_AUTH_TOKEN=xxxxxxxx
    export TWILIO_FROM_NUMBER=+15550001111   # the number Twilio gave you

Run:
    python send_sms.py                        # sends "hello" to the default list
    python send_sms.py --to +13219164708 --message "hello"
    python send_sms.py --to +13219164708 +15551234567 --message "hi both"
"""

import argparse
import os
import sys

from twilio.rest import Client

# Default recipients. E.164 format: +, country code, then the number.
DEFAULT_RECIPIENTS = ["+13219164708"]
DEFAULT_MESSAGE = "hello"


def send_sms(to_numbers, body):
    """Send `body` to every number in `to_numbers`. Returns a list of Twilio message SIDs."""
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_FROM_NUMBER"]

    client = Client(account_sid, auth_token)
    sids = []
    for number in to_numbers:
        message = client.messages.create(to=number, from_=from_number, body=body)
        print(f"sent to {number}: sid={message.sid} status={message.status}")
        sids.append(message.sid)
    return sids


def main():
    parser = argparse.ArgumentParser(description="Send an SMS via Twilio.")
    parser.add_argument("--to", nargs="+", default=DEFAULT_RECIPIENTS, help="Recipient numbers in E.164 format")
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="Text to send")
    args = parser.parse_args()

    missing = [k for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER") if k not in os.environ]
    if missing:
        print(f"missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    send_sms(args.to, args.message)


if __name__ == "__main__":
    main()
