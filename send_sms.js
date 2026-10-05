// Same thing in Node.js, for comparison.
//   npm install twilio
//   TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=... TWILIO_FROM_NUMBER=+1555... node send_sms.js

const twilio = require("twilio");

const recipients = ["+13219164708"];
const body = "hello";

const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

async function main() {
  for (const to of recipients) {
    const msg = await client.messages.create({ to, from: process.env.TWILIO_FROM_NUMBER, body });
    console.log(`sent to ${to}: sid=${msg.sid} status=${msg.status}`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
