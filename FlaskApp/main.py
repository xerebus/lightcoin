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


## INITIALIZATION

app = Flask(__name__)
app.secret_key = 'secret_key' # TODO: change
mysql = MySQL()

# enter MySQL database
app.config['MYSQL_DATABASE_USER'] = 'root'  # TODO: change, this is very bad
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
app.config['MYSQL_DATABASE_DB'] = 'store'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


## LOGIN AND LOGOUT

@app.route('/')
def main():
    '''Display a login prompt, or redirect to home if user is logged in.'''

    if session.get('user'):
        return redirect('/home')

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


## HOME SCREEN

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


## EMPLOYEE/USER MANAGEMENT INTERFACE

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


## PRODUCT MANAGEMENT INTERFACE

@app.route('/product', methods=['POST', 'GET'])
def product():
    '''Display a paginated product list, with options to
    add a new product (new entry in product_line) or a new pack size
    of an existing product.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # parse page number
    if request.method == 'POST':
        page = int(request.form['page'])
    else:
        page = 0

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # number of items per page
    list_limit = 10

    # fetch product data
    args = (list_limit, page * list_limit)
    cursor.callproc('GetProducts', args)
    products = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'product.html',
        user = session.get('user'),
        products = products,
        page = page
    )

@app.route('/product_line_add', methods = ['POST'])
def add_product():
    '''Adds a new product. This corresponds to a new product_line as
    well as a new product associated with that product_line -- both tables
    are updated.'''

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


        # attempt to add product
        args = (
            request.form['upc'],
            request.form['pid'],
            request.form['name'],
            request.form['pack_size'],
            request.form['cost'],
            request.form['sale']
        )
        cursor.callproc('CreateProduct', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/product')

@app.route('/product_add', methods = ['POST'])
def add_product_pack():
    '''Adds a new pack size of an existing product. Product must already
    exist in product_line.'''

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


        # attempt to add product
        args = (
            request.form['upc'],
            request.form['pid'],
            request.form['pack_size'],
            request.form['cost'],
            request.form['sale']
        )
        cursor.callproc('CreateProductPack', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/product')

@app.route('/product_delete', methods = ['POST'])
def delete_product_pack():
    '''Delete a product pack. If this is the last pack of this product,
    delete the product as well.'''

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

        # delete product
        args = (request.form['upc'],)
        cursor.callproc('DeleteProduct', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/product')


## CUSTOMER MANAGEMENT INTERFACE

@app.route('/customer', methods=['POST', 'GET'])
def customer():
    '''Display customer list.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # parse page number
    if request.method == 'POST':
        page = int(request.form['page'])
    else:
        page = 0

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # number of items per page
    list_limit = 10

    # fetch product data
    args = (list_limit, page * list_limit)
    cursor.callproc('GetCustomers', args)
    customers = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'customer.html',
        user = session.get('user'),
        customers = customers,
        page = page
    )

@app.route('/customer_add', methods = ['POST'])
def add_customer():
    '''Add a new customer.'''

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

        # attempt to add customer
        args = (
            request.form['name'],
            request.form['phone']
        )
        cursor.callproc('CreateCustomer', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/customer')

@app.route('/customer_delete', methods = ['POST'])
def delete_customer():
    '''Delete a customer. TODO: deal with receipts referring to this
    customer.'''

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

        # delete product
        args = (request.form['cid'],)
        cursor.callproc('DeleteCustomer', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/customer')


## VENDOR MANAGEMENT INTERFACE

@app.route('/vendor', methods=['POST', 'GET'])
def vendor():
    '''Display vendor list.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # parse page number
    if request.method == 'POST':
        page = int(request.form['page'])
    else:
        page = 0

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # number of items per page
    list_limit = 10

    # fetch product data
    args = (list_limit, page * list_limit)
    cursor.callproc('GetVendors', args)
    vendors = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'vendor.html',
        user = session.get('user'),
        vendors = vendors,
        page = page
    )

@app.route('/vendor_add', methods = ['POST'])
def add_vendor():
    '''Add a new vendor.'''

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

        # attempt to add vendor
        args = (
            request.form['name'],
            request.form['rating']
        )
        cursor.callproc('CreateVendor', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/vendor')

@app.route('/vendor_delete', methods = ['POST'])
def delete_vendor():
    '''Delete a vendor. TODO: deal with orders referring to this
    vendor.'''

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

        # delete product
        args = (request.form['vid'],)
        cursor.callproc('DeleteVendor', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/vendor')

if __name__ == '__main__':
    app.run(debug = True)
