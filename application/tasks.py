from celery import shared_task
import smtplib
from .models import Song, User, Album, db, CreatorLikes, Creator
from instances import app
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import datetime
from jinja2 import Template
from sqlalchemy import func
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from instances import redisInstance


@shared_task()
@app.route('/check_login', methods=['get'])
def check_login():
    users = User.query.filter(User.user_type != "ADMIN").all()
    now = datetime.datetime.now()
    for user in users:
        last_login = redisInstance.get('last_login_' + str(user.id))
        if last_login is not None:
            last = datetime.datetime.strptime(str(last_login), "%Y-%m-%d %H:%M:%S.%f")
            if (now-last).total_seconds() > 86400:
                askLogin.delay(user.email, user.name)
        else:
            askLogin.delay(user.email, user.name)
    return 'hello'


@shared_task()
def askLogin(email, name):
    print(f'''Mail sent to {email}''')
    rendered = f'''
    <html>
    <body>
        <h4>Hello {name}</h4>
        <p>Try out new songs and albums at vibhorify</p>
        <p>Don't miss visit now</p>
    </body>
    </html>
    '''
    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(rendered, 'html'))
    msg['Subject'] = 'Try Songs at Vibhorify' 
    msg['To'] = email
    send_mail(msg)
    return

@shared_task()
@app.route('/send_monthly_report', methods=['get'])
def send_monthly_report():
    creators = User.query.filter(User.user_type == "CREATOR").all()
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    month = last_month.strftime("%m")
    year = last_month.strftime("%Y")
    month_words = last_month.strftime("%B")
    
    for creator in creators:
        report.delay(creator.id, creator.email, month, year, month_words)
    return "hello"

@shared_task()
def report(creator_id, email, month, year, month_words):
    with open('template_report') as file_:
        template = Template(file_.read())

    creator = Creator.query.filter(Creator.id == creator_id).first()

    analytics = {}
    analytics['song_count'] = Song.query.where(Song.creator_id == creator_id).where(
        func.extract('year', Song.created_at) == year).where(
        func.extract('month', Song.created_at) == month).count()
    analytics['album_count'] = Album.query.where(Album.creator_id == creator_id).where(
        func.extract('year', Album.created_at) == year).where(
        func.extract('month', Album.created_at) == month).count()
    query = db.select(
        func.sum(CreatorLikes.likes),
        func.sum(CreatorLikes.views),
        func.sum(CreatorLikes.rating_count),
        func.sum(CreatorLikes.rating * CreatorLikes.rating_count),
    ).where(
        Album.creator_id == creator_id).where(
        func.extract('year', Album.created_at) == year).where(
        func.extract('month', Album.created_at) == month).where(
        CreatorLikes.creator_id == creator_id)
    res = db.session.execute(query).first()
    analytics['likes'] = res[0] if res else 0
    analytics['views'] = res[1] if res else 0
    analytics['rating_count'] = res[2] if res else 0
    analytics['rating'] = res[3]/analytics['rating_count'] if analytics['rating_count'] else 0

    rendered = template.render(analytics = analytics, artist_name = creator.artist,
                                                                month_name = month_words, year = year)
    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(rendered, 'html'))
    msg['Subject'] = f'Vibhorify monthly report for {month_words}, {year}' 
    msg['To'] = email
    send_mail(msg)
    return

load_dotenv()
fromaddress = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
domain = os.environ.get('DOMAIN')

@shared_task()
def send_mail(message):
    server = smtplib.SMTP(domain, 587)
    server.starttls()
    server.login(fromaddress, password)
    server.send_message(message)
    server.close()