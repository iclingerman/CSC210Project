from app import app, db
from app.models import User, Calendars, Events, Share, Reset


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Calendars': Calendars, 'Events': Events, 'Share': Share, 'Reset': Reset}