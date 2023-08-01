import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formatdate
import sys, codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

sendAddress = "maedahiroto0709@gmail.com"
password = "MAEDAhiroto1610"

subject = "件名"
bodyText = "本文"
fromAddress = "a8120178@gsuite.si.aoyama.ac.jp"
toAddress = "a8120178@aoyama.jp"

# SMTPサーバに接続
smtpobj = smtplib.SMTP("smtp.gmail.com", 587)
smtpobj.starttls()
smtpobj.login(sendAddress, password)

# メール作成
msg = MIMEText(bodyText)
msg["Subject"] = subject
msg["From"] = fromAddress
msg["To"] = toAddress
msg["Date"] = formatdate()

# 作成したメールを送信
smtpobj.send_message(msg)
smtpobj.close()
