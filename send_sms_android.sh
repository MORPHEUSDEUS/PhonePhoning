#!/data/data/com.termux/files/usr/bin/bash
# Send an SMS from an Android phone you own, using its own SIM. No cloud, no modem to buy.
#
# One-time setup on the phone:
#   1. Install Termux and Termux:API from F-Droid (the Play Store builds are stale and broken).
#   2. In Termux:  pkg install termux-api cronie
#   3. Open the Termux:API app once and grant the SMS permission.
#   4. Make this file executable:  chmod +x send_sms_android.sh
#
# Run by hand:
#   ./send_sms_android.sh
#   ./send_sms_android.sh "+13219164708 +15551234567" "hello"
#
# Run daily at 9:00 (phone's local time):
#   crond                      # start the cron daemon (once per boot; use Termux:Boot to automate)
#   crontab -e                 # then add this line:
#   0 9 * * * /data/data/com.termux/files/home/PhonePhoning/send_sms_android.sh
#
# Android will kill background jobs aggressively. Turn off battery optimization for Termux,
# or acquire a wakelock with `termux-wake-lock`, or the cron job will silently never fire.

RECIPIENTS="${1:-+13219164708}"
MESSAGE="${2:-hello}"

for number in $RECIPIENTS; do
    if termux-sms-send -n "$number" "$MESSAGE"; then
        echo "sent to $number"
    else
        echo "failed to send to $number" >&2
    fi
    sleep 1
done
