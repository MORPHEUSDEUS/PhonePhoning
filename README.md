# PhonePhoning

Send a text message to one or more phone numbers on a schedule, with no cloud SMS service.

## Where the line really is

SMS is a carrier protocol. A message enters the network only through a SIM the carrier
issued. Services like Twilio are just companies that own a lot of SIMs and resell them over
HTTP. You cannot replace the carrier, but you can replace the middleman by owning the SIM and
the radio yourself. That is what this repo does. Two ways:

| Route | What you need | Cost | Notes |
|---|---|---|---|
| **Your Android phone** (`send_sms_android.sh`) | Termux + Termux:API | Free, uses your plan | Fastest to get working. Phone must stay on and unoptimized. |
| **A modem you own** (`send_sms_modem.py`) | USB LTE modem + SIM + any computer or Raspberry Pi | ~$30-60 modem, ~$5-10/mo prepaid SIM | Dedicated, always-on, no phone involved. |

Both end up at the same place: your SIM, your carrier, the recipient. Nothing in between
that you do not control.

Not possible: sending SMS with no SIM at all. That would mean peering with carriers over SS7
and running your own SMS center, which requires carrier interconnect agreements that are
not granted to individuals.

## Route 1: your Android phone

See the comments at the top of `send_sms_android.sh`. Summary:

```bash
pkg install termux-api cronie
./send_sms_android.sh "+13219164708" "hello"
```

Schedule daily with `crontab -e` inside Termux. Disable battery optimization for Termux or
Android will kill the job.

iPhone: there is no supported way to script SMS from iOS. The Shortcuts app can send a text
on a schedule through its Automation tab, but that is a GUI, not code.

## Route 2: a modem you own

Buy a 4G LTE USB modem or Raspberry Pi HAT (SIM7600 family, Quectel EC25, Huawei E3372) and a
prepaid SIM. Avoid 2G-only boards like the SIM800L in the US; the 2G network is gone.

```bash
pip install -r requirements.txt
python send_sms_modem.py --port /dev/ttyUSB2 --to +13219164708 --message "hello"
```

The script talks to the modem with AT commands, the same text protocol modems have used since
the 1980s. Watch it work with a serial terminal if you want to see what it is doing:

```
AT                  -> OK
AT+CPIN?            -> +CPIN: READY
AT+CREG?            -> +CREG: 0,1
AT+CMGF=1           -> OK
AT+CMGS="+13219164708"
> hello<Ctrl-Z>     -> +CMGS: 12
```

Schedule daily with cron on the machine the modem is plugged into:

```
0 9 * * * cd /home/pi/PhonePhoning && python send_sms_modem.py --port /dev/ttyUSB2 >> sms.log 2>&1
```

## Multiple recipients

Both scripts take a list of numbers. Numbers must be in E.164 format: `+1` then the 10 digits
for US numbers, so 3219164708 becomes `+13219164708`.

## A note on volume

Carriers watch consumer SIMs for automated bulk sending. A few messages a day to people who
know you is fine. Hundreds a day will get the SIM flagged and blocked.
