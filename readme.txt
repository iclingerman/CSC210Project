CSC210 Project - EZWeek
Erin Gibson, Sophie Stahl, Ian Clingerman
egibson4, sstahl, iclinger

------- RUN INSTRUCTIONS -------

A list of required python packages are included in requirements.txt, all of which can be installed in a virtual environment using
'pip install ___'. To run, activate the virtual environment, and inside the Project folder, use the command 'flask run'. Then click
the provided link to open the website. To run in https, the command 'flask run --cert=cert.pem --key=key.pem'.


------- OVERVIEW AND DESCRIPTION -------

Our website, called EZWeek, provides a secure way to create and share weekly calendars. Users can create an account with the 'register'
page, confirm their email with an emailed link, securely login, and reset their password using an emailed code. 
In the home page, owned calendars can be selected and created, and shared calendars can also be selected. 
When an owned calendar is selected, an intuitive weekly view is shown, and forms to add an event, share the calendar, and delete the 
calendar.
When a shared calendar is selected, and the current user does not own that calendar, the calendar can only be viewed, not edited.
 

------- INCLUDED FILES -------

HTML FILES in templates folder
404.HTML addevent.HTML base.HTML calendar.HTML
confirmation.HTML editevent.HTML home.HTML index.HTML login.HTML 
noeditpermission.HTML nopermission.HTML password_reset.HTML register.HTML

IMAGES, SCRIPTS, CSS in static folder
account-icon.png ezweek.png scripts.js styles.css
transparent-icon.webp white-profile.jpg

PYTHON files in app folder
__init__.PY forms.PY jobs.PY models.PY routes.PY

PYTHON, DB files in Project folder
app.db cert.pem config.PY db.txt key.pem main.PY requirements.txt


------- BASIC REQUIREMENTS -------

HTML and CSS: We created and wrote HTML files (including templates) as well as styles.css
Python-Flask: The backend is build from Python-Flask, as seen in routes.PY
WTForms: We build forms using WTForms to create, edit, and delete calendars/events, as well as login/register forms
Flask-SQLAlchemy: Our database, app.db, uses SQLAlchemy to insert and delete items
Flask-Login: We used Flask-Login for login, logout, and register, and hashing passwords

Database Layout: we have 5 tables in our database:
User = (id, username, password, name, email, confirmation_code, email_confirmed)
Calendars = (userid, calendarid, name)
Events = (calendarid, eventid, DOW, start_time, end_time, name, notification)
Share = (calendarid, friendid)
Reset = (userid, reset_code, timestamp, date)


------- ADDITIONAL FEATURES -------

Email Interaction: We used Flask-Mail and APScheduler to send email confirmation links, password reset codes, and scheduled event reminders.
Calendar Sharing: We allow users to share individual calendars with other accounts, in a view-only format (only calendar owners can edit)
User Interface: We used Bootstrap to build a responsive user interface, with a top navbar, intuitive calendar layout, and the ability
                to click events to edit/delete.


