from celery import shared_task
import smtplib
from .models import Song, User, Album, db, CreatorLikes, Creator
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import datetime
from jinja2 import Template
from sqlalchemy import func


@shared_task()
def mul(x, y):
    print('mul called')
    return x * y


@shared_task()
def askLogin():
    print('Login Asked')
    return 'hj'

@shared_task()
def send_monthly_report():
    creators = User.query.filter(User.user_type == "CREATOR").all()
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    month = last_month.strftime("%m")
    year = last_month.strftime("%Y")
    month_words = last_month.strftime("%B")
    
    for creator in creators:
        report.delay(creator.id, month, year, month_words)
    return

@shared_task()
def report(creator_id, month, year, month_words):
    with open('report_template') as file_:
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
        func.extract('month', Album.created_at) == month)
    res = db.session.execute(query).first()
    analytics['likes'] = res[0] if res else 0
    analytics['views'] = res[1] if res else 0
    analytics['rating_count'] = res[2] if res else 0
    analytics['rating'] = res[3]/analytics['rating_count'] if analytics['rating_count'] else 0

    print(creator_id, month, year, month_words, template.render(analytics = analytics, artist_name = creator.artist))
    return

load_dotenv()
fromaddr = os.environ.get('EMAIL')

password = os.environ.get('PASSWORD')
domain = os.environ.get('DOMAIN')

@shared_task()
def send_mail(message):
    fromaddr = os.environ.get('EMAIL')
    password = os.environ.get('PASSWORD')
    domain = os.environ.get('DOMAIN')
    server = smtplib.SMTP(domain, 587)
    server.starttls()
    server.login(fromaddr, password)
    server.send_message(message)
    server.close()