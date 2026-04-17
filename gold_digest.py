import os, requests, smtplib
from email.mime.text import MIMEText
from datetime import datetime

API_KEY = os.environ['GOLD_API']
EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASS = os.environ['EMAIL_PASS']
TO_EMAIL = os.environ['TO_EMAIL']

r = requests.get("https://www.goldapi.io/api/XAU/USD",
    headers={"x-access-token": API_KEY})
data = r.json()

usd_price = data['price']
inr_price = usd_price * 85 / 31.1035  # per gram approx
inr_10g = round(inr_price * 10)

body = f"""
🟡 GOLD DIGEST - {datetime.now().strftime('%d %b %Y')}

COMEX Spot : ${usd_price:.2f} /oz
MCX Approx : ₹{inr_10g:,} /10g

Open  : ${data.get('open_price','N/A')}
High  : ${data.get('high_price','N/A')}
Low   : ${data.get('low_price','N/A')}
Change: {data.get('ch','N/A')} ({data.get('chp','N/A')}%)

Have a great trading day!
"""

msg = MIMEText(body)
msg['Subject'] = f"🟡 Gold Digest {datetime.now().strftime('%d %b')}"
msg['From'] = EMAIL_USER
msg['To'] = TO_EMAIL

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
    s.login(EMAIL_USER, EMAIL_PASS)
    s.send_message(msg)

print("Email sent!")
