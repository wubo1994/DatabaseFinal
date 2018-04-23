from flask import Flask, request, Response, json, jsonify, render_template, flash, redirect, url_for
from urllib.parse import unquote
from flask_login import current_user, login_user, logout_user, login_required
from flask_login import UserMixin
from app.models import Customer, Order, Part
from werkzeug.urls import url_parse
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
import jinja2
import json

from app import app, db
from app.forms import LoginForm, RegistrationForm, SectionForm, LoadPartForm, SearchByBrandForm, SearchByStkNoForm, OrderForm


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Rohan'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('homepage.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    con = db.engine.connect()
    if form.validate_on_submit():
        user = con.execute('SELECT * FROM Customer WHERE username=="{0}"'.format(form.username.data))
        theUser = user.fetchone()
        if not theUser:
            flash("Invalid username or password")
            return redirect(url_for('login'))
        if not check_password_hash(theUser[3],form.password.data):
            flash("Invalid customername or password")
            return redirect(url_for('login'))
        loginUser = Customer.query.filter_by(username=theUser[1]).first()
        login_user(loginUser,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/arthur', methods=['GET', 'POST'])
def main_arthur():
    '''
        Main page:
        - should be only accessible after the user successfully authenticates (signs in)
    '''
    json = build_json_string(current_user.get_id())
    print(json)
    con = db.engine.connect()
    sections = con.execute('SELECT * FROM Note WHERE user_id = 1').fetchall()
    print(sections)
    return render_template('arthur.html', json=json)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    con = db.engine.connect()
    if form.validate_on_submit():
        '''user = User(username=form.username.data, email=form.email.data)'''
        '''user.set_password(form.password.data)'''
        username=form.username.data
        email=form.email.data
        password_hash=generate_password_hash(form.password.data)
        '''db.session.add(user)'''
        con.execute('INSERT INTO Customer (username,email,password_hash) VALUES ("{0}","{1}","{2}")'.format(username,email,password_hash))
        db.session.commit()
        flash('Congratulations, you are now a registered customer!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/load',methods=['GET','POST'])
def load():
    '''
    Only owner of this system will be allowed to add 
    new parts into the database
    '''
    if int(current_user.get_id()) is not 1:
        print('You do not have the authority!')
        return redirect(url_for('index'))
    form = LoadPartForm()
    con = db.engine.connect()
    if form.validate_on_submit():
        stocknumber = form.stocknumber.data
        brand = form.brand.data
        category = form.category.data
        price = form.price.data
        part = con.execute('SELECT * FROM Part WHERE stocknumber={0}'.format(stocknumber)).fetchone()
        if part:
            number = part[4]
            stock_number = part[0]
            con.execute('UPDATE Part SET quantity={0} WHERE stocknumber={1}'.format(number+1,stock_number))
        else:
            con.execute('INSERT INTO Part (stocknumber,brand,category,price,quantity) VALUES ({0},"{1}","{2}",{3},{4})'.format(stocknumber,brand,category,price,1))
            db.session.commit()
        print(part)
        print(current_user.get_id())
        return redirect(url_for('index'))
    return render_template('LoadPart.html',title='Load',form=form)

@app.route('/view', methods=['GET','POST'])
def view():
    stuff = []
    if current_user.is_authenticated:
        con = db.engine.connect()
        parts = con.execute('SELECT * FROM Part')
        for part in parts:
            stuff.append(part)
        return render_template('ViewParts.html',Stuff=stuff,title='View All Parts')
    return render_template('ViewParts.html',Stuff=stuff,title='View All Parts')


@app.route('/searchbystkno', methods=['GET','POST'])
def searchByStkNo():
    form = SearchByStkNoForm()
    stuff = []
    if current_user.is_authenticated:
        con = db.engine.connect()
        if form.validate_on_submit():
            stockNumber = form.stocknumber.data
            parts = con.execute('SELECT * FROM Part WHERE stocknumber={0}'.format(stockNumber))
            for part in parts:
                stuff.append(part)
            return render_template('SearchByStkNo.html',Stuff=stuff,title='Search By Stock No.',form=form)
    return render_template('SearchByStkNo.html',Stuff=stuff,title='Search By Stock No.',form=form)


@app.route('/searchbybrand', methods=['GET','POST'])
def searchByBrand():
    form = SearchByBrandForm()
    stuff = []
    if current_user.is_authenticated:
        con = db.engine.connect()
        if form.validate_on_submit():
            brand = form.brand.data
            parts = con.execute('SELECT * FROM Part WHERE brand="{0}"'.format(brand))
            for part in parts:
                stuff.append(part)
            return render_template('SearchByBrand.html',Stuff=stuff,title='Search By Brand',form=form)
    return render_template('SearchByBrand.html',Stuff=stuff,title='Search By Brand',form=form)


@app.route('/order', methods=['GET','POST'])
def order():
    form = OrderForm()
    outputInfo = ''
    if current_user.is_authenticated:
        if int(current_user.get_id()) is 1:
            return redirect(url_for('index'))
        con = db.engine.connect()
        if form.validate_on_submit():
            userid = int(current_user.get_id())
            stockNumber = form.stocknumber.data
            part = con.execute('SELECT * FROM Part WHERE stocknumber = {0}'.format(stockNumber)).fetchone()
            if not part:
                outputInfo = 'No part matches the stock number you typed in.'
                return render_template('Order.html',Info=outputInfo,title='Order Info',form=form)
            else:
                originQty = part[4]
                if (originQty > 1):
                    con.execute('UPDATE Part SET quantity = {0} WHERE stocknumber = {1}'.format((originQty-1),stockNumber))
                else:
                    con.execute('DELETE FROM Part WHERE stocknumber = {0}'.format(stockNumber))
                sql_section = 'INSERT INTO [Order] (customer_id, part_id) VALUES ({0}, {1})'.format(userid,stockNumber)
                con.execute(sql_section)
                db.session.commit()
                outputInfo = 'Successfully Ordered!'
                return render_template('Order.html',Info=outputInfo,title='Order Info',form=form)
    return render_template('Order.html',Info=outputInfo,title='Order Info',form=form)

@app.route('/showOrder', methods=['GET','POST'])
def showOrder():
    form = 

    



@app.route('/insert', methods=['GET', 'POST'])
def insert():
    ''' Test function to see if we can insert a new note+section '''
    form = SectionForm()
    con = db.engine.connect()
    if form.validate_on_submit():
        id = current_user.get_id()
        body = form.body.data
        con.execute('INSERT INTO Section(body,user_id) VALUES ("aaaaaaaaaaaaa",{0})'.format(id))
        con.execute('INSERT INTO Note(body, user_id) VALUES ("{0}", {1})'.format(body, id))
        db.session.commit()
        flash('Successfully created a new section!')
        return redirect(url_for('login'))
    return render_template('insert.html', title = 'Insert', form=form)





@app.route('/save', methods=['POST'])
def save_request():
    '''
        Save request handler:
        - Takes the client's AJAX request and saves the content of the DataStore to the DB
    '''
    dsJSON = request.form["json"]
    dsJSON = unquote(dsJSON)
    ds = json.loads(dsJSON)     # Build the DataStore object from the JSON
    

    # Note to Bo, Rohan, etc. (everyone that's setting up the DB access logic)
    #   At this point, you can access the exact DataStore object which contains the new notes 
    #   I've written a demo function that iterates over the DataStore and accesses each information
    #   Please reference this and write the function to run the INSERT sql statements
    #update_db_from_datastore_demo(ds)

    return "success"
"""
def update_db_from_datastore_demo(ds):
    '''
        Example function to demonstrate how we will access the DataStore object
    '''
    user_name = "Uda Yeruultsengel" # Note: this should probably be set somewhere globally for each request
    
    for section in ds:
        # Check if the current section already exists
        my_sql = '''
            SELECT TOP 1 FROM dataSections A INNER JOIN dataUsers as B ON A.uID = B.uID
            WHERE A.uID = ''' + user_name + ''' AND A.Title = ''' + section['title'] + '''
            '''
        # Note: this is a pseudo function 
        section_exists = check_if_sql_returns_a_record(my_sql)

        # Section already exists. So iterate over notes and perform UPDATE statements
        if section_exists:
            for note in section['notes']:
                # Perform the same check for notes 

                # If it already exists, perform UPDATE statement

                # Else, if it it doesn't exist, create a new record

        # Section does not exist. Run a INSERT INTO statement
        else:
            my_sql_1 = '''
                DECLARE @NEXTKEY as int = ''' + grab_next_key() + '''
                DECLARE @title as nvarchar(max) = ''' + section['title'] +'''
                DECLARE @uid as int = ''' + grab_user_pk() +'''
                DECLARE @tags as nvarchar(max) = ''' + ','.join(section['tags']) +'''

                INSERT INTO dataSections
                (sID, Title, uID, Tags, GETDATE(), GETDATE())
                VALUES
                (@NEXTKEY, @title, @uid, @tags)
                '''
            run_the_real_execute_function(my_sql_1)

            # Do the same check and insertion or update for the dataNoteTags

            # Then insert the notes into dataNotes
            my_sql_2 = ''' the real sql to insert each notes'''
            run_the_real_execute_function(my_sql_1)
"""

# class UserInfo():
    # def __init__(self):


def build_json_string(userno):
    '''
    This function builds the JSON string from the DB for the current user.
    '''

    '''
    0 -- id
    1 -- body
    2 -- user_id
    3 -- notes
    4 -- tags
    '''

    sql_sections = 'SELECT * FROM Section WHERE user_id = {0}'.format(userno)

    con = db.engine.connect()
    table = con.execute(sql_sections)
    sections_rows = table.fetchall()

    data_store = []

    # Populate the DataStore with sections
    for row in sections_rows:
        cur_section = {}
        cur_section['id'] = row[0]
        cur_section['title'] = row[1]
        cur_section['notes'] = []

        sql_notes = '''
            SELECT * 
            FROM Note 
            WHERE section_id = {0} 
        ''' .format(cur_section['id'])

        con = db.engine.connect()
        table = con.execute(sql_notes)
        notes_rows = table.fetchall()

        # Populate current section's notes array
        for row in notes_rows:
            cur_note = {}
            cur_note['id'] = row[0]
            cur_note['text'] = row[1]
            cur_note['tags'] = []  # Default to empty right now

            cur_section['notes'].append(cur_note)
        #end-for-notes

        # Add this to the
        data_store.append(cur_section)
    #end-for-sections

    return json.dumps(data_store)
