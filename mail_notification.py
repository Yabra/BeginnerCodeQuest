import datetime
import smtplib
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pymorphy2
import schedule

from data.db_session import global_init, create_session
from data.user import User


def send_email(receiver, days, name):
    me = "beginnercodequest@rambler.ru"
    password = "Qwerty16012006"
    you = receiver

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Давно не виделись"
    msg['From'] = me
    msg['To'] = you
    morph = pymorphy2.MorphAnalyzer()
    p = morph.parse("день")[0]
    w = p.make_agree_with_number(int(days)).word
    html = f"""\
    <html lang="ru">
      <head></head>
      <body>
        <p><b>Привет, {name}!</b><br>
           Ты уже {days} {w} не был на Beginner Code Quest <br>
           Удели время развитию себя в программировании <br>
            Самое время порешать <a href="google.com"> задачи</a>
        </p>
      </body>
    </html>
    """

    part2 = MIMEText(html, 'html')

    msg.attach(part2)

    s = smtplib.SMTP("smtp.rambler.ru", 587)
    s.starttls()
    s.login(me, password)
    s.sendmail(me, you, msg.as_string())


def email_notification(db_name):
    now = datetime.datetime.now()
    db_name = db_name
    global_init(db_name)
    db_sess = create_session()
    for user in db_sess.query(User):
        time_diff = (now - user.last_active).days
        if time_diff > 0:
            send_email(user.email, time_diff, user.name)


def start_notification():
    schedule.every().day.at("00:00").do(email_notification, db_name="db/db.db")
    while True:
        schedule.run_pending()
        time.sleep(30)


def notification_in_thread():
    th = threading.Thread(target=start_notification)
    th.start()
