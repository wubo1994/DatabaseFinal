from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(128))
    orders = db.relationship('Order',backref='customer',lazy='dynamic')

    def __repr__(self):
        return '<Customer {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return Customer.query.get(int(id))

    '''
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)
    '''

'''
@login.user_loader
def load_user(id):
    return Customer.query.get(int(id))


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.relationship('Note', backref='section', lazy='dynamic')
    tags = db.relationship('Tag', backref='section', lazy='dynamic')

    def __repr__(self):
        return '<Section {}>'.format(self.body)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    tags = db.relationship('Tag', backref='note', lazy='dynamic')

    def __repr__(self):
        return '<Note {}>'.format(self.body)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Note {}>'.format(self.body)
    
'''

class Order(db.Model):
    ordernumber = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer,db.ForeignKey('customer.id'))
    part_id = db.Column(db.Integer,db.ForeignKey('part.stocknumber'))

    def __repr__(self):
        return '<Order {}>'.format(self.ordernumber)

class Part(db.Model):
    stocknumber = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(64))
    category = db.Column(db.String(64))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    order_number = db.relationship('Order',backref='part',lazy='dynamic')

    def __repr__(self):
        return '<Part {0},{1}>'.format(self.brand,self.category)

    
