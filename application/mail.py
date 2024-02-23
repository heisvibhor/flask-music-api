import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()
fromaddr = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
domain = os.environ.get('DOMAIN')

def send_mail(message):
    fromaddr = os.environ.get('EMAIL')
    password = os.environ.get('PASSWORD')
    domain = os.environ.get('DOMAIN')
    server = smtplib.SMTP(domain, 587)
    server.starttls()
    server.login(fromaddr, password)
    server.send_message(message)
    server.close()
