import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()
def prompt(prompt):
    return input(prompt).strip()
fromaddr = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
domain = os.environ.get('DOMAIN')
# print(fromaddr, password, domain)
toaddrs  = "22f3000607@ds.study.iitm.ac.in"

server = smtplib.SMTP(domain, 587)
server.starttls()
server.login(fromaddr, password)

msg = EmailMessage()
msg.set_content("message")

msg['Subject'] = 'TEST'
msg['From'] = fromaddr
msg['To'] = toaddrs
server.send_message(msg)



