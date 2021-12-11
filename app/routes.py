from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_mail import Mail, Message
from app import app, db, mail, scheduler
from app.jobs import sendReminder
from app.models import User, Calendars, Events, Share, Reset
from datetime import datetime, time
from app.forms import LoginForm, RegistrationForm, AddCalendarForm, AddEventForm, PasswordResetForm, EmailRequestForm, ShareForm, DeleteCalendarForm, EditEventForm

import secrets, json

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    

    return render_template("home.html", title='Welcome')

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = current_user
    form = AddCalendarForm()
    if form.validate_on_submit():
        check = Calendars.query.filter_by(userid=user.id, name=form.name.data).first()
        if check is not None:
            flash("Calendar name already exists")
            return(redirect(url_for('index')))
    
        calendar = Calendars(userid=user.id, name=form.name.data)
        db.session.add(calendar)
        db.session.commit()
        form.name.data = ""
    calendars = Calendars.query.filter_by(userid=user.id)
    shared = Share.query.filter_by(friendid=user.id)
    
    userCalendars = []
    for calendar in calendars:
        x = calendar.__dict__
        x.pop('_sa_instance_state', None)
        userCalendars.append(x)
    
    sharedCalendars = dict()
    for calendar in shared:
        x = calendar.__dict__
        x.pop('_sa_instance_state', None)
        cal = Calendars.query.filter_by(calendarid=calendar.calendarid).first()
        if cal is not None:
            calname = cal.name
            calowner = User.query.filter_by(id=cal.userid).first()
            calusername = calowner.username
            sharedCalendars[calusername] = calname

    return render_template('index.html', title='Home', name=user.name, calendars=userCalendars, shared=sharedCalendars, form=form)

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#logout page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        code = secrets.token_hex(8)
        user = User(username=form.username.data, name=form.name.data, email=form.email.data, email_confirmed=False, confirmation_code=code)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        url = request.base_url[:-9] + url_for('confirmation', username=form.username.data, code=code)
        # Send registration Email
        msg = Message('Welcome to EzWeek!', sender = 'EzWeekMessages@gmail.com', recipients = [user.email])
        msg.body = "Welcome to EzWeek. Click the link to confirm your email: " + url
        mail.send(msg)

        return redirect(url_for('login'))
    else:
        print(form.errors)
    return render_template('register.html', title='Register', form=form)

@app.route('/calendars/<username>/<calendarname>', methods=['GET', 'POST'])
@login_required
def calendars(username, calendarname):
    user = User.query.filter_by(username=username).first()
    calendar = Calendars.query.filter_by(userid=user.id, name=calendarname).first()
    if current_user != user and calendar is not None:
        print("current user is viewing another user's calendar")
        share2 = Share.query.filter_by(calendarid=calendar.calendarid, friendid=current_user.id)
        print(share2)
        share = Share.query.filter_by(calendarid=calendar.calendarid, friendid=current_user.id).first()
        if (share is None):
            print("You are not allowed to view this calendar")
            return render_template("nopermission.html", title="No Permission")

    shareform = ShareForm()
    if shareform.validate_on_submit():
        print("VALIDDATE")
        friendlist = User.query.filter_by(username=shareform.username.data)
        frienduser = User.query.filter_by(username=shareform.username.data).first()
        if friendlist is None or frienduser is None:
            flash("Invalid username", "share")
            return redirect(url_for('calendars', username=username, calendarname=calendarname))
        if frienduser.id == current_user.id:
            flash("Can't share with yourself", "share")
            return redirect(url_for('calendars', username=username, calendarname=calendarname))
        sharecheck = Share.query.filter_by(calendarid=calendar.calendarid, friendid=frienduser.id).first()
        if sharecheck is not None:
            msg = "This calendar has already been shared with " + frienduser.username
            flash(msg, "share")
            return redirect(url_for('calendars', username=username, calendarname=calendarname))
        shared = Share(calendarid=calendar.calendarid, friendid=frienduser.id)
        db.session.add(shared)
        db.session.commit()
        sub = 12 + len(username) + len(calendarname)
        print(request.base_url[:-sub])
        print(url_for('calendars', username=username, calendarname=calendarname))
        url = request.base_url[:-sub] + url_for('calendars', username=username, calendarname=calendarname)
        # Send shared notification email with link to shared calendar
        subject = user.name + " has shared " + calendar.name + " with you! "
        msg = Message("New Shared Calendar", sender = 'EzWeekMessages@gmail.com', recipients = [frienduser.email])
        msg.body = subject + "Click the link to view your shared calendar: " + url
        mail.send(msg)
        shareform.username.data = ""
        #send notification email to friendID's email
    else:
        for error in shareform.errors:
            print(error)

    deleteform = DeleteCalendarForm()
    if deleteform.delete.data==True and deleteform.validate():
        print("in delete calendar")
        Calendars.query.filter_by(calendarid=calendar.calendarid).delete()
        events = Events.query.filter_by(calendarid=calendar.calendarid)
        for e in events:
            for job in scheduler.get_jobs():
                if job.id == str(e.eventid):
                    scheduler.remove_job(str(e.eventid))
        Events.query.filter_by(calendarid=calendar.calendarid).delete()
        Share.query.filter_by(calendarid=calendar.calendarid).delete()
        db.session.commit()
        return redirect(url_for('index'))

    form = AddEventForm()
    if form.validate_on_submit():
        # add code to iterate over days of week
        for day in form.dow.data:
            if day == 'Sunday':
                dayOfWeek = 6
            elif day == 'Monday':
                dayOfWeek = 0
            elif day == 'Tuesday':
                dayOfWeek = 1
            elif day == 'Wednesday':
                dayOfWeek = 2
            elif day == 'Thursday':
                dayOfWeek = 3
            elif day == 'Friday':
                dayOfWeek = 4
            else:
                dayOfWeek = 5    
            #validate start and end times: make sure they don't overlap with current events in calendar
            #also make sure the start time is before the end time
            
            start = time(hour=form.start.data.hour, minute=form.start.data.minute)
            end = time(hour=form.end.data.hour, minute=form.end.data.minute)
            
            if not end.hour > start.hour:
                if end.hour < start.hour:
                    flash("End time must be after start time", "event")
                    return redirect(url_for('calendars', username=username, calendarname=calendarname))
                elif end.minute < start.minute:
                    flash("End time must be after start time", "event")
                    return redirect(url_for('calendars', username=username, calendarname=calendarname))
            
            #list of all events from same calendar, on same day
            poss_conflicts = Events.query.filter_by(calendarid=calendar.calendarid, DOW=dayOfWeek)
            for e in poss_conflicts:
                e_start = time(hour=e.start_time.hour, minute=e.start_time.minute)
                e_end = time(hour=e.end_time.hour, minute=e.end_time.minute)
                if (start > e_start and start < e_end) or (end > e_start and end < e_end): #new event contained in old event
                    msg = "Conflict with " + e.name
                    flash(msg, "event")
                    return redirect(url_for('calendars', username=username, calendarname=calendarname))
                elif (e_start > start and e_start < end) or (e_end > start and e_end < end): #old event contained in new event
                    msg = "Conflict with " + e.name
                    flash(msg, "event")
                    return redirect(url_for('calendars', username=username, calendarname=calendarname))

            print("Notification? " + str(form.notification.data))
            notif = "F"
            if form.notification.data:
                notif = "T"

            event = Events(calendarid=calendar.calendarid, DOW=dayOfWeek, start_time=form.start.data, end_time=form.end.data, name=form.name.data, notification=notif)
            db.session.add(event)
            db.session.commit()
            if form.notification.data:
                hour = event.start_time.hour
                if event.start_time.minute < 15:
                    minute = (event.start_time.minute-15) % 60
                    hour = (hour - 1) % 24
                else:
                    minute = (event.start_time.minute-15)
                name = user.username+"|"+event.name
                msg = Message('EzWeek Event Reminder - ' + str(event.name), sender = 'EzWeekMessages@gmail.com', recipients= [user.email])
                scheduler.add_job(func=sendReminder, args=[day, event.start_time, event.name, msg, calendar.name], trigger='cron', day_of_week=dayOfWeek, hour=hour, minute=minute, id=str(event.eventid), name=name)
                for job in scheduler.get_jobs():
                    print("name: %s, trigger: %s, next run: %s, handler: %s , id: %s" % (
                    job.name, job.trigger, job.next_run_time, job.func, job.id))


    events = Events.query.filter_by(calendarid=calendar.calendarid)
    eventList = []
    eventDict = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}}
    for e in events:
        x = e.__dict__
        x.pop('_sa_instance_state', None)
        eventList.append(x)
        eventDict[e.DOW].update({e.start_time.strftime("%H:%M"): x})
    sortedEvents = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}}
    for key in eventDict:
        sortedEvents.update({key: dict(sorted(eventDict[key].items()))})
    return render_template('calendar.html', title='Calendar', calendar = calendar, events = json.dumps(sortedEvents, default=str), form=form, shareform=shareform, deleteform=deleteform, username=user.username)



@app.route('/calendars/<eventid>', methods=['GET', 'POST'])
@login_required
def calendar_edit_event(eventid):
    event = Events.query.filter_by(eventid=eventid).first()
    if event is None:
        print("event doesn't exist")
        return render_template("404.html")
    calendar = Calendars.query.filter_by(calendarid=event.calendarid).first()
    if calendar is None:
        print("calendar doesn't exist")
        return render_template("404.html")
    user = User.query.filter_by(id=calendar.userid).first()
    if current_user != user:
        print("user doesn't have edit permissions")
        return render_template("noeditpermission.html", title="No Permission")

    days = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
    if event.DOW==0:
        day = "Monday"
    elif event.DOW==1:
        day = "Tuesday"
    elif event.DOW==2:
        day="Wednesday"
    elif event.DOW==3:
        day="Thursday"
    elif event.DOW==4:
        day="Friday"
    elif event.DOW==5:
        day="Saturday"
    else:
        day="Sunday"

    notif = False
    if event.notification == 'T':
        notif = True
    editform = EditEventForm(name=event.name, dow=day, start=event.start_time, end=event.end_time, notification=notif)

    if editform.validate_on_submit():
        print('inside edit submission')
        oldevent = Events.query.filter_by(eventid=eventid).first()
        if oldevent is None:
            print("can't find event")
        if oldevent is not None:
            print("found event")
            Events.query.filter_by(eventid=event.eventid).delete()
            db.session.commit()
            # removes the job from the scheduler
            for job in scheduler.get_jobs():
                if job.id == str(event.eventid):
                    scheduler.remove_job(str(event.eventid))
            print("Current jobs after removing")
            for job in scheduler.get_jobs():
                print("name: %s, trigger: %s, next run: %s, handler: %s , id: %s" % (job.name, job.trigger, job.next_run_time, job.func, job.id))
        if editform.delete2.data==True:
            return redirect(url_for('calendars', username=user.username, calendarname=calendar.name))
        for day in editform.dow.data:
            if day == 'Sunday':
                dayOfWeek = 6
            elif day == 'Monday':
                dayOfWeek = 0
            elif day == 'Tuesday':
                dayOfWeek = 1
            elif day == 'Wednesday':
                dayOfWeek = 2
            elif day == 'Thursday':
                dayOfWeek = 3
            elif day == 'Friday':
                dayOfWeek = 4
            else:
                dayOfWeek = 5    
            #validate start and end times: make sure they don't overlap with current events in calendar
            #also make sure the start time is before the end time
            start = time(hour=editform.start.data.hour, minute=editform.start.data.minute)
            end = time(hour=editform.end.data.hour, minute=editform.end.data.minute)
            if end < start:
                flash("End time must be after start time", "event")
                return redirect(url_for('calendar_edit_event', eventid=eventid))
            if not end.hour > start.hour:
                if end.hour < start.hour:
                    flash("End time must be after start time", "event")
                    return redirect(url_for('calendars', username=user.username, calendarname=calendar.name))
                elif end.minute < start.minute:
                    flash("End time must be after start time", "event")
                    return redirect(url_for('calendars', username=user.username, calendarname=calendar.name))
            
            #list of all events from same calendar, on same day
            poss_conflicts = Events.query.filter_by(calendarid=calendar.calendarid, DOW=dayOfWeek)
            for e in poss_conflicts:
                if e.eventid != eventid:
                    e_start = time(hour=e.start_time.hour, minute=e.start_time.minute)
                    e_end = time(hour=e.end_time.hour, minute=e.end_time.minute)
                    if (start > e_start and start < e_end) or (end > e_start and end < e_end): #new event contained in old event
                        msg = "Conflict with " + e.name
                        flash(msg, "event")
                        return redirect(url_for('calendar_edit_event', eventid=eventid))
                    elif (e_start > start and e_start < end) or (e_end > start and e_end < end): #old event contained in new event
                        msg = "Conflict with " + e.name
                        flash(msg, "event")
                        return redirect(url_for('calendar_edit_event', eventid=eventid))
            #create and add new event
            notif = "F"
            if editform.notification.data:
                notif = "T"
            newevent = Events(calendarid=calendar.calendarid, DOW=dayOfWeek, start_time=editform.start.data, end_time=editform.end.data, name=editform.name.data, notification=notif)
            db.session.add(newevent)
            db.session.commit()
            #add email job if notifications are requested
            if editform.notification.data:
                notification_time_before_event = 15
                print("new job")
                hour = event.start_time.hour
                if event.start_time.minute < 15:
                    minute = (event.start_time.minute-15) % 60
                    hour = (hour - 1) % 24
                else:
                    minute = (event.start_time.minute-15)
                name = user.username+"|"+newevent.name
                msg = Message('EzWeek Event Reminder - ' + str(newevent.name), sender = 'EzWeekMessages@gmail.com', recipients= [user.email])
                scheduler.add_job(func=sendReminder, args=[day, newevent.start_time, newevent.name, msg, calendar.name], trigger='cron', day_of_week=dayOfWeek, hour=hour, minute=minute, id=str(newevent.eventid), name=name)
                for job in scheduler.get_jobs():
                    print("name: %s, trigger: %s, next run: %s, handler: %s , id: %s" % (
                    job.name, job.trigger, job.next_run_time, job.func, job.id))           
        return redirect(url_for('calendars', username=user.username, calendarname=calendar.name))
    else:
        print(editform.errors)
        print("not valid")
    return render_template('editevent.html', eventid=eventid, editform=editform)




@app.route('/confirmation/<username>', methods=['GET', 'POST'], defaults={'code': None}) 
@app.route('/confirmation/<username>/<code>', methods=['GET', 'POST'])
def confirmation(username, code):
    confirmation_code = int(code, base=16)
    
    user = User.query.filter_by(username=username).first()
    if confirmation_code == int(user.confirmation_code, 16):
        setattr(user, 'email_confirmed', True)
        db.session.commit()
        return render_template('confirmation.html', title='Confirmation')
    else:
        print("ERROR on email confirmation")
        return render_template("home.html", title='Welcome')

@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    email_entered = False
    form = EmailRequestForm()
    if form.validate_on_submit():
        print("HERE")
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user is not None and user.email_confirmed:
            print("We can send an email")
            code = secrets.token_hex(4)
            msg = Message('EzWeek Password Reset', sender = 'EzWeekMessages@gmail.com', recipients = [user.email])
            msg.body = "Hi " + user.name + ",\nHere is the code to reset your password: " + str(code) + "\nThis link will only be active for 1 hour."
            mail.send(msg)
            time = datetime.now().time()
            date = datetime.now().date()
            Reset.query.filter_by(userid=user.id).delete()
            reset = Reset(userid=user.id, reset_code=code, timestamp=time, date=date)
            db.session.add(reset)
            db.session.commit()
            email_entered = True
            return redirect(url_for('password_reset_code'))  
        else: 
            print("we cannot send an email")
        return render_template("password_reset.html", title='Password Reset', form=form, email_entered=email_entered)
    return render_template("password_reset.html", title='Password Reset', form=form, email_entered=email_entered)

@app.route('/password_reset/code', methods=['GET', 'POST'])
def password_reset_code():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        print("form validated")
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            reset = Reset.query.filter_by(userid=user.id).first()
            if reset is not None:
                now = datetime.now()
                timestamp = datetime(year=reset.date.year, month=reset.date.month, day=reset.date.day, hour=reset.timestamp.hour, minute=reset.timestamp.minute, second=reset.timestamp.second)
                print(now)
                print(timestamp)
                difference = now - timestamp
                print(difference)
                if form.code.data == reset.reset_code: 
                    if difference.days < 1 and divmod(difference.seconds, 3600)[0] < 1:
                        #Code verified 
                        print("code verified and valid")
                        user.set_password(form.password.data)
                        Reset.query.filter_by(userid=user.id).delete()
                        db.session.commit()
                        return redirect(url_for('login'))
                    else:
                        print("error 4")
                        flash('Expired code. Please request a new code.')
                        Reset.query.filter_by(userid=user.id).delete()
                        db.session.commit()
                else: 
                    print("error 3")
                    flash('Invalid or expired code')
            else:
                print("error 2")
                flash('Reset was not requested')     
        else:
            print("error 1")
            flash('Invalid username')
    else:
        print(form.errors)
    return render_template('password_reset.html', title='Password Reset', form=form, email_entered=True)