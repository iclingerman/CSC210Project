from app import app, mail


def sendReminder(dow, time, name, msg, calname):
    print("Reminder sent")
    with app.app_context():
        time_str = ""
        if (time.hour > 12):
            time_str = str(time.hour-12) + ":" + str(time.minute) + " PM"
        else:
            time_str = str(time) + " AM"
        msg.body = "This is your reminder for " + str(name) + " on " + str(dow) + " at " + time_str + ", from " + calname
        mail.send(msg)