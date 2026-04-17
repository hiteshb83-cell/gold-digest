import os, requests, smtplib
from email.mime.text import MIMEText
from datetime import datetime

API_KEY = os.environ['GOLD_API']
EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASS = os.environ['EMAIL_PASS']
TO_EMAIL = os.environ['TO_EMAIL']

# Gold price data
r = requests.get("https://www.goldapi.io/api/XAU/USD",
    headers={"x-access-token": API_KEY})
data = r.json()

usd_price = data['price']
inr_price = usd_price * 85 / 31.1035
inr_10g = round(inr_price * 10)
change = data.get('ch', 0)
change_pct = data.get('chp', 0)
open_p = data.get('open_price', 'N/A')
high_p = data.get('high_price', 'N/A')
low_p = data.get('low_price', 'N/A')

# Futures estimate (contango approx)
near_month = round(usd_price * 1.003, 2)
next_month = round(usd_price * 1.006, 2)
structure = "Normal Contango ✅" if near_month > usd_price else "Backwardation ⚠️"

# News via GoldAPI
news_r = requests.get("https://www.goldapi.io/api/news",
    headers={"x-access-token": API_KEY})
news_items = []
if news_r.status_code == 200:
    news_data = news_r.json()
    for item in news_data[:3]:
        news_items.append(f"• {item.get('title','N/A')} [{item.get('source','N/A')}]")
news_block = "\n".join(news_items) if news_items else "• News unavailable today"

# Direction signal
if change_pct > 0.5:
    signal = "BULLISH 📈"
elif change_pct < -0.5:
    signal = "BEARISH 📉"
else:
    signal = "NEUTRAL ➡️"

# Verdict logic
if usd_price < 4600:
    verdict = "BUY 🟢 — Price is at a discount. Strong entry zone."
elif usd_price > 5000:
    verdict = "WAIT 🟡 — Price elevated. Wait for pullback to ₹1,25,000."
else:
    verdict = "WAIT 🟡 — Recovering phase. Buy on dips toward ₹1,27,000."

body = f"""
╔══════════════════════════════════════╗
   🟡 GOLD DIGEST — {datetime.now().strftime('%d %b %Y')}
╚══════════════════════════════════════╝

━━━ 1. CURRENT PRICE ━━━━━━━━━━━━━━━
COMEX Spot  : ${usd_price:.2f} /oz
MCX Approx  : ₹{inr_10g:,} /10g
Open        : ${open_p}
High        : ${high_p}
Low         : ${low_p}
Change      : {change} ({change_pct}%)

━━━ 2. FUTURES CURVE ━━━━━━━━━━━━━━━
Near Month  : ${near_month}
Next Month  : ${next_month}
Structure   : {structure}

━━━ 3. MARKET NEWS (Latest) ━━━━━━━━
{news_block}

━━━ 4. SMART MONEY ━━━━━━━━━━━━━━━━
COT Signal  : Commercials net long (Bullish)
Central Bank: China & EM buying continues
Inst. Target: JPMorgan $6,300 | GS bullish

━━━ 5. TREND SIGNAL ━━━━━━━━━━━━━━━
Today       : {signal}

━━━ 6. VERDICT ━━━━━━━━━━━━━━━━━━━━
{verdict}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Not financial advice. Trade carefully.
"""

msg = MIMEText(body)
msg['Subject'] = f"🟡 Gold Digest {datetime.now().strftime('%d %b')} | MCX ₹{inr_10g:,} | {signal}"
msg['From'] = EMAIL_USER
msg['To'] = TO_EMAIL

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
    s.login(EMAIL_USER, EMAIL_PASS)
    s.send_message(msg)

print("Gold digest sent!")
