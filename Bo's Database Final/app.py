from app import app, db
from app.models import Customer, Order, Part


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Customer': Customer, 'Order': Order, 'Part': Part}

#To try to run the website type in: set FLASK_APP=app.py    and then type in: flask run