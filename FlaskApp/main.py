# main.py
# Aritra Biswas, 2016
#
# Main Flask routines for lightcoin.

from __future__ import print_function
import sys

from flask import Flask, render_template, request, redirect, session
from flask.ext.mysql import MySQL

from werkzeug import generate_password_hash, check_password_hash

import time

app = Flask(__name__)
app.secret_key = 'secret_key' # TODO: change
mysql = MySQL()

# enter MySQL database
app.config['MYSQL_DATABASE_USER'] = 'root'  # TODO: change, this is very bad
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
app.config['MYSQL_DATABASE_DB'] = 'store'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def main():
    '''Display a login prompt.'''

    return render_template('index.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    '''Validate the user's credentials and redirect them to the lightcoin
    console.'''

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # get password of user
        args = (request.form['username'],)
        cursor.callproc('GetUserPassword', args)
        data = cursor.fetchone()
        
        # validate user
        if data:
            if check_password_hash(data[0], request.form['password']):

                # register session
                session['user'] = request.form['username']
        
                return redirect('/home')

            else:
                return render_template(
                    'error.html',
                    error = 'Wrong password.'
                )
        else:
            return render_template(
                'error.html',
                error = 'Username does not exist.'
            )


        # close connection
        cursor.close()
        conn.close()
        
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    '''Takes the user back to the login screen.'''

    session.pop('user', None)
    return redirect('/')

@app.route('/home')
def home():
    '''Display a default homepage.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    return render_template('home.html', user = session.get('user'))

@app.route('/employee')
def employee():
    '''List employees and allow adding a new employee.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()

    # fetch employee data
    cursor.callproc('GetEmployees')
    employees = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'employee.html',
        user = session.get('user'),
        employees = employees
    )

@app.route('/employee_add', methods = ['POST'])
def add_employee():
    '''Adds a new employee to the employee table. If username already exists,
    the SQL stored procedure makes no modifications.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # make sure passwords match
        if request.form['password'] != request.form['confirm_password']:
            return render_template(
                'error.html',
                error = 'Passwords did not match.'
            )
            

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # attempt to add employee
        
        args = (
            request.form['username'],
            generate_password_hash(request.form['password']),
            time.strftime('%Y%m%d'),
            request.form['priv']
        )
        cursor.callproc('CreateUser', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/employee')

@app.route('/employee_delete', methods = ['POST'])
def delete_employee():
    '''Deletes an employee from the employee table.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # delete user
        args = (request.form['username'],)
        cursor.callproc('DeleteUser', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/employee')

if __name__ == '__main__':
    app.run(debug = True)
