# main.py
# Aritra Biswas, 2016
#
# Main Flask routines for lightcoin.

from __future__ import print_function
import sys

from flask import Flask, render_template, request, redirect, session
from flask.ext.mysql import MySQL

from werkzeug import generate_password_hash, check_password_hash

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

@app.route('/login', methods=['POST', 'GET'])
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

@app.route('/home')
def home():
    '''TODO: home. For now, just a successful login message.'''

    if session.get('user'):
        return 'You got in!'
    else:
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )
    return "nothing to see here"
        

if __name__ == '__main__':
    app.run(debug = True)
