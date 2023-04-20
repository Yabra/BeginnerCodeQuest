import datetime
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_mail import Mail, Message
import ssl

import pymorphy2
import schedule

from data.user import User


mail: Mail = None


def init_mail(app):
    global mail
    mail = Mail(app)


def send_email(receiver, days, name, problem_adress):

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
            Самое время порешать <a href="{problem_adress}"> задачи</a>
        </p>
      </body>
    </html>
    """

    msg = Message('Давно не виделись', recipients=[receiver])
    msg.body = MIMEText(html, 'html').as_string()
    mail.send(msg)


def email_notification(db_sess, problem_adress):
    now = datetime.datetime.now()
    for user in db_sess.query(User):
        time_diff = (now - user.last_active).days
        if time_diff > 0:
            send_email(user.email, time_diff, user.name, problem_adress)


def start_notification(db_sess, problem_adress):
    schedule.every().day.at("00:00").do(email_notification, db_sess=db_sess, problem_adress=problem_adress)
    while True:
        schedule.run_pending()
        time.sleep(30)


def notification_in_thread(db_sess, problem_adress):
    th = threading.Thread(target=start_notification, args=(db_sess, problem_adress))
    th.start()
