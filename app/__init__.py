from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
scheduler = APScheduler()
scheduler.init_app(app)

scheduler.start()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'EzWeekMessages@gmail.com'
app.config['MAIL_PASSWORD'] = '*****' #Password for email needs to be entered here
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


from app.models import Events, Calendars, User
from app.jobs import sendReminder
for event in Events.query.filter_by(notification='T'):
    calendar = Calendars.query.filter_by(calendarid=event.calendarid).first()
    user = User.query.filter_by(id=calendar.userid).first()
    hour = event.start_time.hour
    minute = 0
    if event.start_time.minute < 15:
        minute = (event.start_time.minute-15) % 60
        hour = (hour - 1) % 24
    else:
        minute = (event.start_time.minute-15)
    dayOfWeek = event.DOW
    day = event.DOW
    msg = Message('EzWeek Event Reminder - ' + str(event.name), sender = 'EzWeekMessages@gmail.com', recipients= [user.email])
    name = user.username+"|"+event.name
    scheduler.add_job(func=sendReminder, args=[day, event.start_time, event.name, msg, calendar.name], trigger='cron', day_of_week=dayOfWeek, hour=hour, minute=minute, id=str(event.eventid), name=name)

print("Scheduled Jobs at Start:")
for job in scheduler.get_jobs():
    print("name: %s, trigger: %s, next run: %s, handler: %s , id: %s" % (
        job.name, job.trigger, job.next_run_time, job.func, job.id))

# var = "56"
# scheduler.remove_job(var)
# print("Part 2:")
# for job in scheduler.get_jobs():
#     print("name: %s, trigger: %s, next run: %s, handler: %s , id: %s" % (
#         job.name, job.trigger, job.next_run_time, job.func, job.id))



from app import routes, models