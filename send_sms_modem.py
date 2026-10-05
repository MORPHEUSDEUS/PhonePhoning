"""Send an SMS through a GSM/LTE modem you own, using raw AT commands.

No cloud service involved. The message goes: this script -> USB serial -> modem -> your SIM
-> the carrier -> the recipient. The only outside party is the carrier that issued the SIM,
and there is no way around that one.

Hardware that works with this script (any modem that speaks the standard AT command set):
    - SIM800L / SIM900 boards (cheap 2G; 2G is shut down in most of the US, so avoid there)
    - SIM7600 / SIM7670 (4G LTE, the sane choice in 2026)
    - Huawei E3372 / E8372 USB sticks, Quectel EC25, Waveshare SIM7600 HAT for a Raspberry Pi
    - A phone in "modem mode" sometimes exposes a serial port too, but Termux is easier there.

Setup:
    pip install -r requirements.txt
    Plug in the modem, put a SIM with an active plan in it, find its port:
        Linux:   ls /dev/ttyUSB*  (usually /dev/ttyUSB2 on multi-port modems) or /dev/ttyACM0
        macOS:   ls /dev/tty.usbserial* /dev/tty.usbmodem*
        Windows: Device Manager -> Ports (COM3, COM4, ...)

Run:
    python send_sms_modem.py --port /dev/ttyUSB2
    python send_sms_modem.py --port /dev/ttyUSB2 --to +13219164708 +15551234567 --message "hello"
"""

import argparse
import sys
import time

import serial

DEFAULT_RECIPIENTS = ["+13219164708"]
DEFAULT_MESSAGE = "hello"
CTRL_Z = b"\x1a"


class Modem:
    def __init__(self, port, baud=115200, timeout=5):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(0.5)
        self.ser.reset_input_buffer()

    def close(self):
        self.ser.close()

    def command(self, cmd, expect="OK", wait=2.0):
        """Write one AT command, collect the reply, raise if the expected token is missing."""
        self.ser.write((cmd + "\r").encode())
        deadline = time.time() + wait
        reply = b""
        while time.time() < deadline:
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if chunk:
                reply += chunk
                if expect.encode() in reply or b"ERROR" in reply:
                    break
        text = reply.decode(errors="replace")
        if expect not in text:
            raise RuntimeError(f"{cmd!r} failed, modem said: {text.strip()!r}")
        return text

    def check_ready(self):
        self.command("AT")                  # modem alive
        self.command("AT+CPIN?", "READY")   # SIM unlocked and present
        reg = self.command("AT+CREG?")      # network registration: ",1" home or ",5" roaming
        if ",1" not in reg and ",5" not in reg:
            raise RuntimeError(f"not registered on a network yet: {reg.strip()!r}")
        self.command("AT+CMGF=1")           # text mode instead of PDU (hex) mode

    def send_sms(self, to, body):
        self.command(f'AT+CMGS="{to}"', expect=">")
        self.ser.write(body.encode() + CTRL_Z)
        # Sending to the tower can take several seconds.
        reply = self.command("", expect="+CMGS", wait=30)
        return reply


def main():
    parser = argparse.ArgumentParser(description="Send an SMS via a serial GSM/LTE modem.")
    parser.add_argument("--port", required=True, help="Serial port of the modem, e.g. /dev/ttyUSB2 or COM3")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--to", nargs="+", default=DEFAULT_RECIPIENTS, help="Recipients in E.164 format")
    parser.add_argument("--message", default=DEFAULT_MESSAGE)
    args = parser.parse_args()

    modem = Modem(args.port, args.baud)
    try:
        modem.check_ready()
        for number in args.to:
            modem.send_sms(number, args.message)
            print(f"sent to {number}")
            time.sleep(1)  # be polite to the tower between messages
    except (RuntimeError, serial.SerialException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        modem.close()


if __name__ == "__main__":
    main()
